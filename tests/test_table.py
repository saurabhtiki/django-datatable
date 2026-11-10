import csv
import io

import pytest
from django.http import QueryDict
from django.template.loader import render_to_string
from django.test import RequestFactory

from django_datatable import CHOICE, NUMBER, Column, DataTable, RowsTable, table_response
from tests.models import Thing

COLUMNS = [
    Column("code", "Code"),
    Column("kind", "Kind", type=CHOICE),
    Column("qty", "Qty", type=NUMBER),
]


@pytest.fixture
def things(db):
    Thing.objects.create(code="Bolt", kind="metal", qty="10")
    Thing.objects.create(code="nut", kind="metal", qty="2.50")
    Thing.objects.create(code="Rope", kind="", qty="7")
    Thing.objects.create(code="=1+1", kind="odd", qty="1")


def make(query="", **extra):
    return DataTable(QueryDict(query), Thing.objects.all(), COLUMNS, table_id="t", **extra)


def codes(table):
    return [row.code for row in table.page]


def test_text_filter_is_contains_and_ignores_case(things):
    assert codes(make("code=OL")) == ["Bolt"]


def test_choice_and_blank_filter(things):
    assert sorted(codes(make("kind=metal"))) == ["Bolt", "nut"]
    assert codes(make("kind=__blank__")) == ["Rope"]


def test_number_range_and_bad_number_is_skipped(things):
    assert sorted(codes(make("qty_min=5"))) == ["Bolt", "Rope"]
    table = make("qty_min=abc")
    assert table.errors and len(table.page) == 4


def test_sort_ignores_case(things):
    assert codes(make("sort=code"))[:3] == ["=1+1", "Bolt", "nut"]


def test_page_size_and_page_past_the_end(things):
    table = make("per_page=25&page=99")
    assert table.page.number == 1


def test_csv_has_plain_numbers_and_formula_guard(things):
    body = b"".join(make().csv_response().streaming_content).decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(body)))
    assert rows[0] == ["Code", "Kind", "Qty"]
    assert ["'=1+1", "odd", "1.00"] in rows
    assert ["nut", "metal", "2.50"] in rows


def test_rows_table_works_on_plain_dicts():
    rows = [{"code": "a", "qty": 3}, {"code": "b", "qty": 9}]
    table = RowsTable(
        QueryDict("qty_min=5"), rows, [Column("code", "Code"), Column("qty", "Qty", type=NUMBER)],
        table_id="r",
    )  # fmt: skip
    assert [row["code"] for row in table.page] == ["b"]


def test_templates_render(things):
    request = RequestFactory().get("/")
    html = render_to_string("tests/table.html", {"table": make()}, request=request)
    assert 'id="t"' in html and "Bolt" in html


def test_empty_table_shows_empty_text(db):
    request = RequestFactory().get("/")
    html = render_to_string("tests/table.html", {"table": make()}, request=request)
    assert "No things yet." in html


def test_table_response_sends_only_the_table_for_an_htmx_click(things):
    request = RequestFactory().get("/", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="t")
    request.user = type("U", (), {"username": "x"})()
    table = make()
    response = table_response(
        request, table, "tests/page.html", "tests/table.html", {"table": table}
    )
    assert b"<html" not in response.content


def test_table_response_csv_works_for_anonymous_user(things):
    request = RequestFactory().get("/", {"export": "csv"})
    table = DataTable(request.GET, Thing.objects.all(), COLUMNS, table_id="t")
    response = table_response(request, table, "x", "y", {})
    assert response["Content-Type"].startswith("text/csv")


def test_header_sticky_cell_sits_above_body_cells():
    from pathlib import Path

    import django_datatable

    css = Path(django_datatable.__file__).parent / "static/django_datatable/datatable.css"
    assert ".data-table thead .dt-sticky { z-index: 3; }" in css.read_text(encoding="utf-8")


def render_table(table):
    request = RequestFactory().get("/")
    return render_to_string("tests/table.html", {"table": table}, request=request)


def test_new_options_are_off_by_default(things):
    html = render_table(make())
    assert "dtDensity" not in html and "dtColumns" not in html
    assert "dt-scroll-sticky" not in html and "dt-bordered" not in html
    assert "table-zebra" in html  # the old look is unchanged


def test_look_options_add_their_classes(things):
    html = render_table(make(striped=False, bordered=True, sticky_header=True))
    assert "dt-bordered" in html and "dt-scroll-sticky" in html
    assert "table-zebra" not in html


def test_density_and_column_menu_show_when_turned_on(things):
    html = render_table(make(density_switch=True, column_toggle=True))
    assert "dtDensity" in html and "dtColumns('t')" in html
    assert 'data-dt-col="qty"' in html  # lets the menu find each column


def test_loading_hint_hook_is_on_the_table_wrapper(things):
    assert 'hx-indicator="this"' in render_table(make())


def test_custom_page_sizes(things):
    table = make("per_page=10", page_sizes=(5, 10))
    assert table.page_sizes == (5, 10) and table.per_page == 10
    assert make("per_page=50", page_sizes=(5, 10)).per_page == 5  # not allowed: first size
    assert make().per_page == 25  # default list unchanged

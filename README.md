# django-datatable

A server-side table for Django: a filter on every column, search box, sort, pages and CSV download.
Everything the user picks lives in the page URL, so refresh, Back and shared links show the same rows.

Needs: Django 5.2+, **htmx 2**, **Alpine.js 3**, **Tailwind + DaisyUI 5** in the host project.

## Install (in an app)

```bash
uv add ../django-datatable                 # local folder (edits show up at once)
# or, from git:  uv add "django-datatable @ git+<repo-url>@v0.1.0"
```

1. Add to `INSTALLED_APPS`: `"django.contrib.humanize"` (the templates use it) and `"django_datatable"`
2. In your base template (JS **before** Alpine, both `defer`):
   ```html
   <link href="{% static 'django_datatable/datatable.css' %}" rel="stylesheet">
   <script defer src="{% static 'django_datatable/datatable.js' %}"></script>
   <script defer src="...alpine.min.js"></script>
   ```
3. **Tailwind must see the package's templates**, or the DaisyUI classes in them are dropped.
   Add to your Tailwind input file (path to wherever the package lives):
   ```css
   @source "../../django-datatable/django_datatable/templates";
   ```
   then rebuild your CSS. (If the package is installed from git into `.venv`, point at the
   `site-packages/django_datatable/templates` folder instead.)

## Use

View:
```python
from django_datatable import CHOICE, Column, DataTable, table_response

table = DataTable(
    request.GET,
    Item.objects.all(),
    [Column("code", "Item code"), Column("uom", "UoM", type=CHOICE)],
    table_id="item-table",
    base_url=request.path,
    search_fields=("code",),
)
return table_response(
    request, table, "items/list.html", "items/partials/item_table.html", {"table": table}
)
```

`items/partials/item_table.html` (redrawn by htmx on every click):
```django
{% include "django_datatable/list_table.html" with row_template="items/partials/item_row.html" empty_text="No items yet." %}
```

`items/partials/item_row.html` draws one row (gets `row`):
```django
<tr><td>{{ row.code }}</td><td>{{ row.uom }}</td></tr>
```

Page `items/list.html` just does `{% include "items/partials/item_table.html" %}`.

Other pieces: `RowsTable` (same table over a Python list of dicts), `rows_csv_response`,
`Column(type=TEXT|CHOICE|NUMBER|DATE)`, `shortcuts=`, `keep=`, `push_url=False` (table inside
another page). Read the docstrings in `django_datatable/datatable.py`.

## Options (all optional)

```python
DataTable(..., density_switch=True,   # S / M / L row height buttons, remembered in the browser
                column_toggle=True,   # "Columns" menu to hide columns, remembered per table
                sticky_header=True,   # column names stay visible while scrolling (box height: --dt-max-height, default 70vh)
                bordered=True,        # lines around every cell
                striped=False,        # turn off alternate row shading
                page_sizes=(10, 25, 50))  # the "per page" choices
```
Colours follow your DaisyUI theme. Rows fade while a click is loading (always on).

## Updating this package

1. Change the code here, add/adjust a test in `tests/`, run `uv run pytest`.
2. Add a line to `CHANGELOG.md`, bump `version` in `pyproject.toml` and `__init__.py`.
3. `git commit`, then `git tag vX.Y.Z`.
4. In each app, pick up the change (see below), run that app's tests, deploy.

**Apps linked by folder** (`uv add ../django-datatable`): nothing to do, the app already uses the
edited files. Run `uv run python manage.py collectstatic` before deploying.

**Apps installed from git**: `uv lock --upgrade-package django-datatable && uv sync`.

Rule: never edit a copy inside an app. Change it here, once.
Don't rename `Column`/`DataTable` arguments or the template variables (`table`, `row_template`,
`empty_text`, `actions_heading`) without a major version bump, since every app depends on them.

## Tests

```bash
uv run pytest
```

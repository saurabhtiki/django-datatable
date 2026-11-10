# Changelog

Newest first. Bump `version` in `pyproject.toml` and `django_datatable/__init__.py` for each release, then `git tag vX.Y.Z`.

## 0.3.1
- Sticky header: the table box now fits the screen (height minus 16rem), so it scrolls inside and the header stays in view even with only 20 rows.

## 0.3.0
- Sticky header is now on by default (`sticky_header=False` turns it off).
- New `border_toggle=True`: a "Lines" button to show or hide cell lines (remembered).
- Page sizes are now 10, 20, 25, 50, 100, 200, and the default is 20.

## 0.2.0
- New options, all off by default: `density_switch` (S/M/L row height), `column_toggle` (hide columns),
  `sticky_header`, `bordered`, `striped=False`, `page_sizes=(...)`.
- Rows fade while a click is loading.

## 0.1.0
- First release, taken from the Stock Audit project (`core/datatable.py`).

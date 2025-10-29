# Repository Guidelines

## Project Structure & Modules
Core Django apps live in `farm`, `taxon`, `shop`, `labels`, and `users`; shared site configuration sits in `seeplahar/` (settings, root URLs, project-wide templates). UI assets are served from `static/` and `theme/static_src/`; user uploads land in `media/`. Reusable fixtures and import data belong in `fixtures/`. Keep each app’s `templates/` and `tests/` folders aligned with its views so new features stay co-located with their domain logic.

## Build, Test, and Development Commands
Create a virtual environment, then `pip install -r requirements.txt`. Apply migrations with `python manage.py migrate` and run the local server via `python manage.py runserver`. Use `pytest` for the primary test suite (`pytest farm/tests/test_models.py::TestSeedLot` to target a case). Tailwind assets compile with `python manage.py tailwind build`; for live reload during UI work, run `python manage.py tailwind start` in parallel with the dev server.

## Coding Style & Naming Conventions
Follow PEP 8: four-space indentation, `snake_case` for functions, `PascalCase` for models/forms, and module-level constants in all caps. Keep view, serializer, and form names aligned with their URL or template (e.g., `SeedLotDetailView`). Template files under each app should mirror the view path (`seedlot/detail.html`). Prefer descriptive QuerySet names and keep business logic in app-level `utils/` modules rather than views.

## Testing Guidelines
`pytest` with `pytest-django` powers the suite; place new tests under the relevant app’s `tests/` directory using `test_*.py` files and `Test<ClassName>` classes. Add fixture data close to the test when practical, or reuse entries in `fixtures/`. Cover new models, forms, and services with at least one happy-path and one failure-path assertion, and run `pytest` before pushing.

## Commit & Pull Request Guidelines
Recent history favors short, title-cased summaries (`Data Model Changes:`); follow that pattern or a succinct imperative line under ~72 characters, adding details in the body if needed. One feature or fix per commit. Pull requests should describe the change set, link any issues or tickets, list migration impacts, and include screenshots or terminal output whenever UI or CLI behavior shifts. Confirm tests pass and note any manual verification steps.

## Environment & Secrets
Settings use `python-decouple`; provide a `.env` with keys such as `SECRET_KEY=...` and `ALLOWED_HOSTS=localhost`. Never commit secrets or the bundled `db.sqlite3` used for local smoke testing. Document any new environment variables in the PR so deploy targets stay in sync.

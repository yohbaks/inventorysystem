# Copilot Instructions for DPWH IT Equipment Inventory System

## Project Overview
This is a Django-based inventory management system for DPWH IT equipment. The project tracks equipment, maintenance, and related documents, with a web interface for CRUD operations and reporting.

## Architecture & Key Components
- **Django Project Structure**: Main app is `inventory`, with core logic in `models.py`, `views.py`, and `admin.py`.
- **Templates**: HTML files in `templates/` provide the UI, using Bootstrap 5 (Kaiadmin Lite theme).
- **Static Files**: Located in `static/`, including assets, CSS, JS, and templates for Excel/Word export.
- **Media Files**: Uploaded documents and images are stored in `media/`.
- **Settings**: Project configuration in `inventorysystem/settings.py`.
- **Database**: Uses SQLite (`db.sqlite3`) by default.

## Developer Workflows
- **Run Server**: `python manage.py runserver`
- **Migrations**: `python manage.py makemigrations` and `python manage.py migrate`
- **Create Superuser**: `python manage.py createsuperuser`
- **Collect Static Files**: `python manage.py collectstatic`
- **Testing**: Tests are in `inventory/tests.py`. Run with `python manage.py test inventory`.

## Conventions & Patterns
- **Model-View-Template (MVT)**: Follows Django's MVT pattern. Business logic in models/views, presentation in templates.
- **Custom Context Processors**: See `inventory/context_processors.py` for global template variables.
- **Signals**: Used for model event handling in `inventory/signals.py`.
- **File Uploads**: Handled via Django's `MEDIA_ROOT` and `media/` directory.
- **Static/Media Separation**: Static files for assets, media for user uploads.
- **Template Inheritance**: Base layout in `templates/base.html`, extended by other templates.

## Integration Points
- **Bootstrap 5 (Kaiadmin Lite)**: UI uses Kaiadmin Lite theme, referenced in `templates/README.md`.
- **Excel/Word Export**: Templates for exporting reports are in `static/excel_template/` and `static/word_template/`.
- **Image Handling**: Equipment images in `equipment_images/` and `media/equipment_images/`.

## Project-Specific Notes
- **Backup Templates**: `backup templates/` contains legacy or backup HTML templates.
- **Admin Customization**: Equipment management via Django admin (`inventory/admin.py`).
- **Document Management**: PM checklists and reports stored in `media/`.

## Example Patterns
- **CRUD Views**: See `inventory/views.py` for equipment CRUD logic.
- **Template Usage**: Example: `desktop_details_view.html` extends `base.html` and uses context from views/context processors.
- **Signals**: Example: automatic actions on equipment changes in `signals.py`.

## References
- Main Django docs: https://docs.djangoproject.com/
- Kaiadmin Lite theme: https://themekita.com/kaiadmin-lite-bootstrap-5-dashboard.html

---
For questions about project-specific conventions, review `inventory/context_processors.py`, `signals.py`, and the main templates in `templates/`.

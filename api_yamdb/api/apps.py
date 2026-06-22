from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configure the API application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

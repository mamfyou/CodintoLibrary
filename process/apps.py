from django.apps import AppConfig


class ProcessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'process'

    def ready(self) -> None:
        import process.signals.handlers

from django.apps import AppConfig


class MychatappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mychatApp'

def ready(self):
        import mychatApp.signals
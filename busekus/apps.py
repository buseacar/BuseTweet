from django.apps import AppConfig

class BusekusConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'busekus'

    def ready(self):
        import busekus.signals

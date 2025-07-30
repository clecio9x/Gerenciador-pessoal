# em cofre/apps.py

from django.apps import AppConfig

class CofreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cofre'

    def ready(self):
        # Importa os sinais para que eles sejam registrados
        import cofre.signals

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'waslaa_telecom.apps.users'  # ← full dotted path, not just 'users'
    label = 'users'
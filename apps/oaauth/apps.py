from django.apps import AppConfig


class OaauthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    # 修改路径后注意修改该name，否则会找不到该app
    name = "apps.oaauth"

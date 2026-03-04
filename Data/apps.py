# from django.apps import AppConfig


# class DataConfig(AppConfig):
#     name = 'data'
# data/apps.py mein
from django.apps import AppConfig
import os


class DataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data"

    def ready(self):
        # Local (RUN_MAIN) aur Live (SERVER_SOFTWARE) dono ke liye check
        if os.environ.get("RUN_MAIN") == "true" or os.environ.get("SERVER_SOFTWARE"):
            from data.background_tasks import run_background_monitor

            run_background_monitor()

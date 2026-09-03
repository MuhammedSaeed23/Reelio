import time
import shutil
from pathlib import Path

TEMP_DIR = Path("media/temp")
MAX_TIME = 30 * 60


def cleanup_temp():
    now = time.time()

    for folder in TEMP_DIR.iterdir():

        if not folder.is_dir():
            continue

        age = now - folder.stat().st_mtime

        if age > MAX_TIME:
            shutil.rmtree(folder, ignore_errors=True)
            print(f"🗑️ Deleted old folder: {folder}")


from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        cleanup_temp()
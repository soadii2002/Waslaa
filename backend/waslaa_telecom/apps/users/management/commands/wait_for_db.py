import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    help = 'Waits for the database to be available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_up = False
        attempts = 0
        while not db_up:
            try:
                conn = connections['default']
                conn.ensure_connection()
                db_up = True
            except (OperationalError, Psycopg2Error):
                attempts += 1
                self.stdout.write(f'Database unavailable, attempt {attempts}. Waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
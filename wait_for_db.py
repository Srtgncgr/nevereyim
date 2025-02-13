# accounts/management/commands/wait_for_db.py
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
    help = 'Waits for database to be available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        attempts = 0
        while not db_conn and attempts < 10:
            try:
                db_conn = connections['default']
                db_conn.ensure_connection()
            except OperationalError:
                self.stdout.write(f'Database unavailable, waiting 5 seconds... (Attempt {attempts + 1})')
                time.sleep(5)
                attempts += 1
        
        if db_conn:
            self.stdout.write(self.style.SUCCESS('Database available!'))
        else:
            self.stdout.write(self.style.ERROR('Could not connect to database'))
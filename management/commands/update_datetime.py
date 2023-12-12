# update_datetime.py
from django.core.management.base import BaseCommand
from django.db import transaction
from runner.models import Event
from datetime import datetime

class Command(BaseCommand):
    help = 'Update the datetime field for each event by combining date and time'

    def handle(self, *args, **options):
        try:
            # Use atomic() to ensure transactional behavior
            with transaction.atomic():
                # Get all events from the database
                events = Event.objects.all()

                # Iterate through each event and update the datetime field
                for event in events:
                    combined_datetime = datetime.combine(event.date, event.time)
                    event.datetime = combined_datetime
                    event.save()
                    print(f"Event: {event.id} datetime changed to: {event.datetime}")

                self.stdout.write(self.style.SUCCESS('Successfully updated datetime for all events.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error updating datetime: {e}'))

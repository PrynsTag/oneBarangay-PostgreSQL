"""Create your custom management commands here."""
import random
from pathlib import Path
from typing import Union

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.models import Max

from config.settings.base import APPS_DIR
from onebarangay_psql.announcement.factories import AnnouncementFactory
from onebarangay_psql.announcement.models import Announcement
from onebarangay_psql.appointment.factories import AppointmentFactory
from onebarangay_psql.appointment.models import Appointment
from onebarangay_psql.rbi.factories import FamilyMemberFactory, HouseRecordFactory
from onebarangay_psql.rbi.models import FamilyMember, HouseRecord
from onebarangay_psql.users.factories import UserFactory

NUM_USERS = 50
NUM_APPOINTMENTS = 25
NUM_APPOINTMENTS_PER_USER = 4
NUM_ANNOUNCEMENTS = 25
NUM_ANNOUNCEMENTS_PER_USER = 5
NUM_HOUSE = 25
NUM_FAMILY_PER_HOUSE = random.randrange(2, 6)

User = get_user_model()


# mypy: ignore-errors
class Command(BaseCommand):
    """Create your custom management commands here."""

    help = "Generates test data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        """Create your custom management commands here."""
        self.stdout.write("Deleting old data...")
        models = [
            Appointment,
            Announcement,
            User,
            HouseRecord,
            FamilyMember,
        ]
        for m in models:
            m.objects.all().delete()

        self.stdout.write("Creating test and superuser account...")
        User.objects.create_superuser("prince", "prince@onebarangay.com", "prynstag")
        User.objects.create_user("test", "test@onebarangay.com", "prynstag")

        self.stdout.write("Creating new data...")
        # Create all the users
        people = []
        for _ in range(NUM_USERS):
            person = UserFactory()
            person.profile.phone_number = f"09{random.randint(1000000, 9999999)}"
            people.append(person)

        # Add users as announcers
        for _ in range(NUM_ANNOUNCEMENTS):
            announcers = random.choices(people, k=NUM_ANNOUNCEMENTS_PER_USER)
            #  pylint: disable=expression-not-assigned
            [AnnouncementFactory(author=announcer) for announcer in announcers]

        # Add users as appointees
        for _ in range(NUM_APPOINTMENTS):
            appointee = random.choices(people, k=NUM_APPOINTMENTS_PER_USER)
            #  pylint: disable=expression-not-assigned
            [AppointmentFactory(user=user) for user in appointee]

        houses = HouseRecordFactory.create_batch(size=NUM_HOUSE)
        for house in houses:
            FamilyMemberFactory.create_batch(
                size=NUM_FAMILY_PER_HOUSE,
                house_record=house,
                last_name=house.family_name,
            )

        self.stdout.write("Resetting indexes...")
        for m in models:
            set_sequence(m)

        self.stdout.write("Deleting old images...")
        delete_all_media_files()


def set_sequence(
    model: Union[Appointment, Announcement, User, HouseRecord, FamilyMember]
) -> None:
    """Reset the id sequence of a table.

    Args:
        model (Model): The model to reset the sequence of.
    Returns:
        None
    """
    if model == HouseRecord:
        model_id = "house_id"
    elif model == FamilyMember:
        model_id = "family_member_id"
    else:
        model_id = "id"

    max_id = model.objects.aggregate(m=Max(model_id))["m"]
    seq = max_id or 1
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT setval(pg_get_serial_sequence(%s,%s), %s);",
            [model._meta.db_table, model_id, seq],
        )


def delete_all_media_files():
    """Delete all media files.

    Returns:
        None
    """
    media_path = Path(APPS_DIR / "media/appointment/government_id")

    for f in media_path.iterdir():
        if not f.name.startswith(".") and f.is_file() and f.suffix in [".jpg", ".png"]:
            if f.name != "default.png":
                f.unlink()

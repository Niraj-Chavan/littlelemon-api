from datetime import datetime
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils.timezone import make_aware

from .base import NoThrottleMixin
from restaurant.models import Booking, Menu


class MenuModelTest(NoThrottleMixin, TestCase):
    def test_create_menu_item(self):
        item = Menu.objects.create(
            title="Greek Salad", price=Decimal("11.99"), inventory=20
        )
        self.assertEqual(Menu.objects.count(), 1)
        self.assertEqual(item.title, "Greek Salad")
        self.assertEqual(item.price, Decimal("11.99"))
        self.assertEqual(item.inventory, 20)

    def test_str_returns_title_and_price(self):
        item = Menu.objects.create(
            title="Pasta Carbonara", price=Decimal("13.50"), inventory=10
        )
        self.assertEqual(str(item), "Pasta Carbonara : 13.50")


class BookingModelTest(NoThrottleMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.slot = make_aware(datetime(2026, 12, 1, 19, 0, 0))

    def test_create_booking(self):
        booking = Booking.objects.create(
            name="Niraj",
            no_of_guests=4,
            table_number=5,
            booking_date=self.slot,
        )
        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(booking.no_of_guests, 4)

    def test_double_booking_is_blocked(self):
        """The UniqueConstraint must stop a second booking for the
        same table at the same date and time."""
        Booking.objects.create(
            name="First Guest",
            no_of_guests=2,
            table_number=3,
            booking_date=self.slot,
        )
        duplicate = Booking(
            name="Second Guest",
            no_of_guests=2,
            table_number=3,
            booking_date=self.slot,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                duplicate.save()

    def test_same_table_different_time_is_allowed(self):
        Booking.objects.create(
            name="Lunch Guest",
            no_of_guests=2,
            table_number=3,
            booking_date=self.slot,
        )
        later = make_aware(datetime(2026, 12, 1, 21, 0, 0))
        Booking.objects.create(
            name="Dinner Guest",
            no_of_guests=2,
            table_number=3,
            booking_date=later,
        )
        self.assertEqual(Booking.objects.count(), 2)

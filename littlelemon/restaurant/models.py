from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Menu(models.Model):
    """A single item on the Little Lemon menu."""

    title = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    inventory = models.IntegerField(default=5, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} : {self.price}"


class Booking(models.Model):
    """A table reservation.

    A table cannot be booked twice for the same date and time: the
    UniqueConstraint in Meta makes MySQL reject duplicate bookings
    at the database level.
    """

    name = models.CharField(max_length=255)
    no_of_guests = models.IntegerField(validators=[MinValueValidator(1)])
    table_number = models.IntegerField(validators=[MinValueValidator(1)])
    booking_date = models.DateTimeField()

    class Meta:
        ordering = ["booking_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["table_number", "booking_date"],
                name="unique_table_per_timeslot",
            )
        ]

    def __str__(self):
        return (
            f"{self.name} (table {self.table_number}) on {self.booking_date}"
        )

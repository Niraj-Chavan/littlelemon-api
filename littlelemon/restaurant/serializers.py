from django.utils.timezone import make_aware, is_naive
from rest_framework import serializers

from .models import Booking, Menu


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    def validate_booking_date(self, value):
        """Store naive datetimes as UTC-aware for consistent comparisons."""
        if is_naive(value):
            return make_aware(value)
        return value

    def validate(self, attrs):
        """
        Turn the database-level double-booking constraint into a clean
        400 response instead of an unhandled IntegrityError (500).
        """
        request = self.context.get("request")

        # On PUT/PATCH, fall back to the existing values.
        if self.instance is not None:
            table_number = attrs.get(
                "table_number", self.instance.table_number
            )
            booking_date = attrs.get(
                "booking_date", self.instance.booking_date
            )
        else:
            table_number = attrs.get("table_number")
            booking_date = attrs.get("booking_date")

        if table_number is not None and booking_date is not None:
            if is_naive(booking_date):
                booking_date = make_aware(booking_date)

            qs = Booking.objects.filter(
                table_number=table_number, booking_date=booking_date
            )
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError(
                    {
                        "detail": (
                            f"Table {table_number} is already booked at "
                            f"{booking_date}. Please choose another slot."
                        )
                    }
                )

        # Silence unused-argument linters; request kept for context.
        _ = request
        return attrs

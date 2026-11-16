from rest_framework import status
from rest_framework.test import APITestCase

from .base import NoThrottleMixin
from restaurant.models import Booking


class BookingSecurityTest(NoThrottleMixin, APITestCase):
    """Covers the Insomnia scenario from the presentation:
    401 without a token, 201 with one, 400 for a double booking."""

    def setUp(self):
        super().setUp()
        self.booking_url = "/restaurant/booking/tables/"
        self.payload = {
            "name": "Niraj",
            "no_of_guests": 4,
            "table_number": 7,
            "booking_date": "2026-12-01T19:00:00",
        }

    def _register_and_get_token(self, username="booker"):
        """Register through Djoser and log in for a token, exactly
        like the API consumers would."""
        self.client.post(
            "/auth/users/",
            {"username": username, "password": "Str0ngPass!2026"},
        )
        login = self.client.post(
            "/auth/token/login/",
            {"username": username, "password": "Str0ngPass!2026"},
        )
        return login.data["auth_token"]

    def test_anonymous_booking_is_unauthorized(self):
        response = self.client.post(self.booking_url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Booking.objects.count(), 0)

    def test_authenticated_booking_succeeds(self):
        token = self._register_and_get_token()
        response = self.client.post(
            self.booking_url,
            self.payload,
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

    def test_duplicate_booking_returns_400(self):
        token = self._register_and_get_token()
        auth = {"HTTP_AUTHORIZATION": f"Token {token}"}

        first = self.client.post(self.booking_url, self.payload, **auth)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post(self.booking_url, self.payload, **auth)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Booking.objects.count(), 1)
        # DRF surfaces the model's UniqueConstraint as a validation error.
        self.assertIn("unique", str(second.data).lower())

    def test_registration_and_login_return_token(self):
        response = self.client.post(
            "/auth/users/",
            {"username": "newuser", "password": "Str0ngPass!2026"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        login = self.client.post(
            "/auth/token/login/",
            {"username": "newuser", "password": "Str0ngPass!2026"},
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("auth_token", login.data)

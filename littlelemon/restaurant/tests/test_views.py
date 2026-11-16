from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .base import NoThrottleMixin
from restaurant.models import Menu


class MenuViewTest(NoThrottleMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username="testuser", password="Testpass123!"
        )
        self.client.force_authenticate(user=self.user)
        Menu.objects.create(
            title="Greek Salad", price=Decimal("11.99"), inventory=20
        )
        Menu.objects.create(
            title="Bruschetta", price=Decimal("7.50"), inventory=15
        )
        Menu.objects.create(
            title="Lemon Cake", price=Decimal("6.25"), inventory=8
        )

    def _results(self, response):
        """Handle both paginated and non-paginated responses."""
        data = response.data
        return data["results"] if isinstance(data, dict) else data

    def test_get_all_menu_items(self):
        response = self.client.get("/restaurant/menu/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = self._results(response)
        self.assertEqual(len(results), 3)
        titles = {item["title"] for item in results}
        self.assertEqual(titles, {"Greek Salad", "Bruschetta", "Lemon Cake"})

    def test_serialized_data_matches_database(self):
        response = self.client.get("/restaurant/menu/")
        results = self._results(response)
        greek = next(
            item for item in results if item["title"] == "Greek Salad"
        )
        self.assertEqual(greek["price"], "11.99")
        self.assertEqual(greek["inventory"], 20)

    def test_create_menu_item(self):
        payload = {"title": "Tiramisu", "price": "9.00", "inventory": 5}
        response = self.client.post("/restaurant/menu/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Menu.objects.filter(title="Tiramisu").exists())

    def test_get_single_menu_item(self):
        item = Menu.objects.first()
        response = self.client.get(f"/restaurant/menu/{item.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], item.title)

    def test_update_menu_item(self):
        item = Menu.objects.first()
        payload = {"title": item.title, "price": "12.99", "inventory": 25}
        response = self.client.put(f"/restaurant/menu/{item.pk}/", payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(str(item.price), "12.99")

    def test_delete_menu_item(self):
        item = Menu.objects.first()
        response = self.client.delete(f"/restaurant/menu/{item.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Menu.objects.count(), 2)

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Booking, Menu
from .serializers import BookingSerializer, MenuSerializer


def index(request):
    """Little Lemon frontend: live menu, auth and booking demo."""
    return render(request, "restaurant/index.html")


class MenuItemsView(ListCreateAPIView):
    """GET lists all menu items, POST adds a new one."""

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer


class SingleMenuItemView(RetrieveUpdateDestroyAPIView):
    """GET, PUT/PATCH and DELETE for a single menu item."""

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for table bookings.

    Only authenticated users may create, change or delete bookings,
    so a request without a valid token receives 401.
    """

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

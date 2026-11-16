from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import BookingViewSet, MenuItemsView, SingleMenuItemView

router = DefaultRouter()
router.register(r"booking/tables", BookingViewSet, basename="booking")


urlpatterns = [
    # Static welcome page
    path("restaurant/", views.index, name="index"),
    # Menu API
    path("restaurant/menu/", MenuItemsView.as_view(), name="menu-items"),
    path(
        "restaurant/menu/<int:pk>/",
        SingleMenuItemView.as_view(),
        name="single-menu-item",
    ),
    # Booking API (router provides list and detail routes)
    path("restaurant/", include(router.urls)),
]

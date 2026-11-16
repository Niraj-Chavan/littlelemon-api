"""
URL configuration for the Little Lemon project.
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    # Little Lemon restaurant app (static welcome page + APIs)
    path("", include("restaurant.urls")),
    # Djoser: registration and token management
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    # Token endpoint required by the course peer review
    path("api-token-auth/", obtain_auth_token),
]

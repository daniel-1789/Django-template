"""Project URL routing.

The API routes live in catalog/urls.py (included at the root). Here we mount the
Django admin and the drf-spectacular docs. The docs paths mirror a Swagger-style
layout: the raw spec at /apidoc/openapi.json, with Swagger UI and ReDoc reading
from it.
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    # Raw OpenAPI spec (feed it to codegen, Postman, etc.).
    path("apidoc/openapi.json", SpectacularJSONAPIView.as_view(), name="schema"),
    # Interactive docs, both generated from the same schema above.
    path("apidoc/swagger", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("apidoc/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

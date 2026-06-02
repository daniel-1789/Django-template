from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalog.views import ItemViewSet, ManufacturerViewSet, healthz

# trailing_slash=False so the routes read /items and /items/1 (no trailing
# slash), matching the Flask template. The router generates:
#   GET/POST  /items            -> list / create
#   GET       /items/{pk}       -> retrieve
# and likewise for /manufacturers.
router = DefaultRouter(trailing_slash=False)
router.register("items", ItemViewSet, basename="item")
router.register("manufacturers", ManufacturerViewSet, basename="manufacturer")

urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path("", include(router.urls)),
]

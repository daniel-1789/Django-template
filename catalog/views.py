from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catalog.models import Item, Manufacturer
from catalog.serializers import HealthSerializer, ItemSerializer, ManufacturerSerializer


@extend_schema(responses=HealthSerializer, tags=["meta"])
@api_view(["GET"])
@permission_classes([AllowAny])
def healthz(_request):
    """Liveness check."""
    return Response({"status": "ok"})


def _search_filter(queryset, request):
    """Apply an optional case-insensitive `?search=` filter on `name`.

    Django's __icontains escapes LIKE wildcards (%, _) in the term for us, so a
    literal "%" typed in the search matches itself rather than acting as a
    wildcard. Blank/missing search returns the queryset untouched.
    """
    term = (request.query_params.get("search") or "").strip()
    return queryset.filter(name__icontains=term) if term else queryset


# Documents the list endpoints' ?search= param in the OpenAPI spec.
_list_with_search = extend_schema_view(
    list=extend_schema(
        parameters=[OpenApiParameter("search", str, description="Case-insensitive filter on name")]
    )
)


# ListModelMixin + RetrieveModelMixin + CreateModelMixin == list / retrieve /
# create only (no update or destroy), matching the Flask template's endpoints.
class _ListRetrieveCreateViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    pass


@_list_with_search
@extend_schema(tags=["manufacturers"])
class ManufacturerViewSet(_ListRetrieveCreateViewSet):
    serializer_class = ManufacturerSerializer
    queryset = Manufacturer.objects.order_by("id")

    def get_queryset(self):
        return _search_filter(super().get_queryset(), self.request)


@_list_with_search
@extend_schema(tags=["items"])
class ItemViewSet(_ListRetrieveCreateViewSet):
    serializer_class = ItemSerializer
    # select_related pulls each item's manufacturer in the same query (a JOIN),
    # so serializing the nested manufacturer doesn't trigger an N+1.
    queryset = Item.objects.select_related("manufacturer").order_by("id")

    def get_queryset(self):
        return _search_filter(super().get_queryset(), self.request)

from rest_framework import serializers

from catalog.models import Item, Manufacturer


class HealthSerializer(serializers.Serializer):
    """Response shape for GET /healthz (also documents it in the OpenAPI spec)."""

    status = serializers.CharField()


class ManufacturerSerializer(serializers.ModelSerializer):
    """Manufacturer for both reads and POST /manufacturers. Also nested in ItemSerializer."""

    class Meta:
        model = Manufacturer
        fields = ["id", "name", "state"]


class ItemSerializer(serializers.ModelSerializer):
    """Item for reads and POST /items.

    `manufacturer` is the nested read-only object; `manufacturer_id` is the
    writable FK. Pointing both at the same model field (source="manufacturer")
    means a write validates the id exists — an unknown manufacturer_id returns a
    400 automatically — and a read echoes it back alongside the nested object,
    matching the Flask template's payload shape.
    """

    manufacturer = ManufacturerSerializer(read_only=True)
    manufacturer_id = serializers.PrimaryKeyRelatedField(
        source="manufacturer",
        queryset=Manufacturer.objects.all(),
    )

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "description",
            "price",
            "created_at",
            "manufacturer_id",
            "manufacturer",
        ]

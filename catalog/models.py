from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models


class Manufacturer(models.Model):
    """A maker of items. One manufacturer has many items (see Item.manufacturer)."""

    name = models.CharField(max_length=255, unique=True)
    # 2-letter state code, e.g. "CA". CharField enforces the max; the min-length
    # validator pins it to exactly 2 (validators run in the admin and DRF).
    state = models.CharField(max_length=2, validators=[MinLengthValidator(2)])

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    """A product, belonging to exactly one Manufacturer."""

    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=1024, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)

    # on_delete=PROTECT mirrors the Flask template's non-null FK: you can't delete
    # a manufacturer while items still point at it. The reverse accessor is
    # `manufacturer.items` (set via related_name).
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name="items",
    )

    def __str__(self) -> str:
        return self.name

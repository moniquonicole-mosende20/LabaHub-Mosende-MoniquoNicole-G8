from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price_per_kg = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (₱{self.price_per_kg}/kg)'
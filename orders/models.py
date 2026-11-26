from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        WASHING = 'washing', 'Washing'
        READY = 'ready', 'Ready'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders',
    )
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='orders')
    weight_kg = models.DecimalField(
        'Estimated weight (kg)', max_digits=6, decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00')), MaxValueValidator(Decimal('50.00'))],
    )
    pickup_address = models.CharField(max_length=255)
    pickup_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} - {self.customer}'

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def badge_class(self):
        return {
            'pending': 'warning text-dark',
            'washing': 'info text-dark',
            'ready': 'primary',
            'completed': 'success',
            'cancelled': 'secondary',
        }[self.status]

    def save(self, *args, **kwargs):
        self.total_price = (self.weight_kg * self.service.price_per_kg).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP,
        )
        super().save(*args, **kwargs)
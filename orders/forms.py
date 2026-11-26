from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from .models import Order, Service


def style_fields(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.Select):
            css = 'form-select'
        elif isinstance(field.widget, forms.CheckboxInput):
            css = 'form-check-input'
        else:
            css = 'form-control'
        field.widget.attrs['class'] = css


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('name', 'description', 'price_per_kg', 'is_active')
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}
        labels = {
            'price_per_kg': 'Price per kg (₱)',
            'is_active': 'Available to customers',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        duplicates = Service.objects.filter(name__iexact=name).exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError('A service with this name already exists.')
        return name


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('service', 'weight_kg', 'pickup_address', 'pickup_date', 'notes')
        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'weight_kg': forms.NumberInput(attrs={'step': '0.01', 'min': '1', 'max': '50'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(
            Q(is_active=True) | Q(pk=self.instance.service_id)
        )
        self.fields['service'].empty_label = 'Select a service'
        style_fields(self)

    def clean_pickup_date(self):
        pickup_date = self.cleaned_data['pickup_date']
        if pickup_date < timezone.localdate():
            raise ValidationError('Pickup date cannot be in the past.')
        return pickup_date

    def clean_pickup_address(self):
        address = self.cleaned_data['pickup_address'].strip()
        if len(address) < 5:
            raise ValidationError('Please enter a complete pickup address.')
        return address


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('status',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)

    def clean_status(self):
        new_status = self.cleaned_data['status']
        current = self.instance.status
        finished = (Order.Status.COMPLETED, Order.Status.CANCELLED)
        if current in finished and new_status != current:
            raise ValidationError(f'A {current} order can no longer be changed.')
        return new_status
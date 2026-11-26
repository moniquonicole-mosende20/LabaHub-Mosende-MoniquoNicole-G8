from django import forms

from .models import Service


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
        for name, field in self.fields.items():
            css = 'form-check-input' if name == 'is_active' else 'form-control'
            field.widget.attrs['class'] = css

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        duplicates = Service.objects.filter(name__iexact=name).exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError('A service with this name already exists.')
        return name
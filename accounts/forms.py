from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import User

phone_validator = RegexValidator(
    r'^\+?\d{7,15}$',
    'Enter a valid contact number (7 to 15 digits, may start with +).',
)


def add_bootstrap(form):
    for field in form.fields.values():
        field.widget.attrs.setdefault('class', 'form-control')


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'contact_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('first_name', 'last_name', 'email', 'contact_number'):
            self.fields[name].required = True
        self.fields['contact_number'].validators.append(phone_validator)
        add_bootstrap(self)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap(self)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'contact_number', 'profile_photo')
        widgets = {'profile_photo': forms.FileInput(attrs={'accept': 'image/*'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('first_name', 'last_name', 'email'):
            self.fields[name].required = True
        self.fields['contact_number'].validators.append(phone_validator)
        add_bootstrap(self)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Another account already uses this email.')
        return email

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if photo and hasattr(photo, 'size') and photo.size > 2 * 1024 * 1024:
            raise ValidationError('Image must be 2 MB or smaller.')
        return photo
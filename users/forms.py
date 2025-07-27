from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.gis.geos import Point
from phonenumber_field.formfields import PhoneNumberField
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from phonenumber_field.phonenumber import PhoneNumber
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('phone', 'first_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Telefon raqam'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ism'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Parol'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Parolni tasdiqlang'})

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError("Ism maydoni to'ldirilishi shart.")
        if len(first_name) < 2:
            raise ValidationError("Ism kamida 2 ta harfdan iborat bo'lishi kerak.")
        return first_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not str(phone).startswith('+'):
            phone = '+' + str(phone)
        return phone

    def clean_password1(self):
        return self.cleaned_data.get('password1')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Parollar mos kelmadi.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    phone = PhoneNumberField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon raqam'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Parol'}))

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not str(phone).startswith('+'):
            phone = '+' + str(phone)
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        password = cleaned_data.get('password')

        if phone and password:
            user = authenticate(
                phone=phone,
                password=password
            )
            if user is None:
                raise ValidationError("Telefon raqam yoki parol noto'g'ri.")
            if not user.is_active:
                raise ValidationError("Bu foydalanuvchi faol emas.")

        return cleaned_data

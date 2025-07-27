from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from users.managers import CustomUserManager


class CustomUser(AbstractUser):
    phone = PhoneNumberField(_('Phone number'), unique=True)
    username = None
    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return str(self.phone)

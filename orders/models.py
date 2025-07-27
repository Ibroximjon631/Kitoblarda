from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

from users.models import CustomUser
from books.models import Book

class PaymentSettings(models.Model):
    card_number = models.CharField(max_length=20, verbose_name=_("To'lov karta raqami"))
    is_active = models.BooleanField(default=True, verbose_name=_("Faol"))

    class Meta:
        verbose_name = _("To'lov sozlamasi")
        verbose_name_plural = _("To'lov sozlamalari")

    def __str__(self):
        return f"To'lov karta raqami: {self.card_number}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('awaiting_confirmation', 'Tasdiqlanishi kutilmoqda'),
        ('confirmed_preparing', 'Tasdiqlangan, yetkazib berishga tayyorlanmoqda'),
        ('awaiting_delivery', 'Yetkazib berilishi kutilmoqda'),
        ('delivered', 'Yetkazib berilgan'),
        ('cancelled', 'Bekor qilindi'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders', verbose_name="Foydalanuvchi")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending', verbose_name="Holat")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Jami summa")
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True, verbose_name="To'lov skrini")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.CharField(max_length=255, verbose_name="Manzil")
    landmark = models.CharField(max_length=255, verbose_name="Mo'ljal")

    class Meta:
        verbose_name = _("Buyurtma")
        verbose_name_plural = _("Buyurtmalar")
        ordering = ['-created_at']

    def __str__(self):
        return f"{_('Buyurtma')} #{self.id} - {self.user.get_full_name()}"

    @property
    def card_number(self):
        try:
            return PaymentSettings.objects.filter(is_active=True).first().card_number
        except:
            return "Karta raqami kiritilmagan"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Buyurtma")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Kitob")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Soni")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")

    class Meta:
        verbose_name = _("Buyurtma elementi")
        verbose_name_plural = _("Buyurtma elementlari")

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

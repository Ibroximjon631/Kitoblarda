from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Order

# Create your tests here.

class OrderModelTest(TestCase):
    def test_order_address_and_landmark(self):
        user = get_user_model().objects.create_user(phone='+998901234567', password='testpass', first_name='Test')
        order = Order.objects.create(user=user, total_amount=10000, address='Toshkent, Chilonzor', landmark='Chilonzor metro')
        self.assertEqual(order.address, 'Toshkent, Chilonzor')
        self.assertEqual(order.landmark, 'Chilonzor metro')

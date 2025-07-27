from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import View, ListView, DetailView, TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from books.models import Book
from .models import Order, OrderItem, PaymentSettings
from .cart import Cart
from django.urls import reverse_lazy, reverse
import logging
from django import forms
from django.http import JsonResponse
logger = logging.getLogger(__name__)
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator

@require_GET
def cart_items_count_view(request):
    cart_data = request.session.get('cart', {})
    total_count = sum(item.get('quantity', 0) for item in cart_data.values())
    return JsonResponse({'count': total_count})


def get_cart(request):
    cart = request.session.get('cart', {})
    return cart

class CartDetailView(TemplateView):
    template_name = 'orders/cart/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        logger.debug(f"Cart in detail view: {cart.cart}")
        context['cart_items'] = cart
        context['total'] = cart.get_total_price()
        return context


class CartAddView(View):
    def post(self, request, book_id):
        cart = Cart(request)
        book = get_object_or_404(Book, id=book_id)

        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        cart.add(book=book, quantity=quantity, update_quantity=False)

        # AJAX so‘rov bo‘lsa JSON qaytaramiz
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'message': f'"{book.title}" savatga qo‘shildi.',
                'book_id': book.id
            })

        # Oddiy POST bo‘lsa redirect
        messages.success(request, f'"{book.title}" savatga qo\'shildi.')
        return redirect('orders:cart_detail')

class CartRemoveView(View):
    def post(self, request, book_id):
        cart = Cart(request)
        book = get_object_or_404(Book, id=book_id)

        cart.remove(book)
        messages.success(request, f'"{book.title}" savatdan olib tashlandi.')
        return redirect('orders:cart_detail')

class OrderCreateForm(forms.Form):
    address = forms.CharField(label="Manzil", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Manzil (ko\'cha, uy)'}))
    landmark = forms.CharField(label="Mo'ljal", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Mo'ljal (yaqin joy)"}))

class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        if len(cart) == 0:
            messages.error(request, 'Sizning savatingiz bo\'sh.')
            return redirect('books:book_list')
        form = OrderCreateForm()
        return render(request, 'orders/order/create.html', {'form': form, 'cart_items': cart, 'total': cart.get_total_price()})

    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        if len(cart) == 0:
            messages.error(request, 'Sizning savatingiz bo\'sh.')
            return redirect('books:book_list')
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            total_amount = cart.get_total_price()
            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                address=form.cleaned_data['address'],
                landmark=form.cleaned_data['landmark']
            )
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    book=item['book'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            request.session['order_id'] = order.id
            messages.success(request, 'Buyurtma muvaffaqiyatli yaratildi. Endi to\'lovni amalga oshiring.')
            return redirect(reverse('orders:payment_process'))
        return render(request, 'orders/order/create.html', {'form': form, 'cart_items': cart, 'total': cart.get_total_price()})

    def form_valid(self, form):
        order = form.save(commit=False)
        order.user = self.request.user
        order.save()

        # Savatchani tozalamang
        # self.request.session['cart'] = {}

        messages.success(self.request, "Buyurtma muvaffaqiyatli yaratildi!")
        return redirect('orders:payment')

class PaymentProcessView(LoginRequiredMixin, View):
    template_name = 'orders/payment.html'

    def get(self, request):
        try:
            order = Order.objects.filter(user=request.user, status='pending').latest('created_at')
            payment_settings = PaymentSettings.objects.filter(is_active=True).first()
            
            if not payment_settings:
                messages.error(request, "To'lov ma'lumotlari topilmadi. Iltimos, administrator bilan bog'laning.")
                return redirect('orders:cart_detail')
            
            context = {
                'order': order,
                'payment_settings': payment_settings
            }
            return render(request, self.template_name, context)
        except Order.DoesNotExist:
            messages.error(request, "Aktiv buyurtma topilmadi.")
            return redirect('orders:cart_detail')
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return redirect('orders:cart_detail')

    def post(self, request):
        try:
            order = Order.objects.filter(user=request.user, status='pending').latest('created_at')
            payment_screenshot = request.FILES.get('payment_screenshot')
            
            if not payment_screenshot:
                messages.error(request, "To'lov skrini yuklanmadi.")
                return redirect('orders:payment_process')
            
            order.payment_screenshot = payment_screenshot
            order.status = 'awaiting_confirmation'
            order.save()
            
            messages.success(request, "To'lov skrini muvaffaqiyatli yuklandi. Buyurtmangiz tekshirilmoqda.")
            return redirect('orders:order_history')
        except Order.DoesNotExist:
            messages.error(request, "Aktiv buyurtma topilmadi.")
            return redirect('orders:cart_detail')
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            return redirect('orders:cart_detail')

class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = 'orders/order/history.html'
    context_object_name = 'orders'
    paginate_by = 10
    login_url = reverse_lazy('users:login')

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'orders/order/detail.html'
    context_object_name = 'order'
    login_url = reverse_lazy('users:login')
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__book')

class OrderConfirmView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.status == 'awaiting_confirmation':
            order.status = 'confirmed_preparing'
            order.save()
            messages.success(request, f'Buyurtma #{order.id} tasdiqlandi.')
        return redirect('admin:orders_order_changelist')

class OrderCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.status == 'awaiting_confirmation':
            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Buyurtma #{order.id} bekor qilindi.')
        return redirect('admin:orders_order_changelist')

class OrderSetAwaitingDeliveryView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.status == 'confirmed_preparing':
            order.status = 'awaiting_delivery'
            order.save()
            messages.success(request, f'Buyurtma #{order.id} yetkazib berishga tayyor deb belgilandi.')
        return redirect('admin:orders_order_changelist')

class OrderSetDeliveredView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.status == 'awaiting_delivery':
            order.status = 'delivered'
            order.save()
            messages.success(request, f'Buyurtma #{order.id} yetkazib berilgan deb belgilandi.')
        return redirect('admin:orders_order_changelist')

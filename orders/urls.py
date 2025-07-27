from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartDetailView.as_view(), name='cart_detail'),
    path('cart/add/<int:book_id>/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/remove/<int:book_id>/', views.CartRemoveView.as_view(), name='cart_remove'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('payment/', views.PaymentProcessView.as_view(), name='payment_process'),
    path('history/', views.OrderHistoryView.as_view(), name='order_history'),
    path('detail/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/confirm/', views.OrderConfirmView.as_view(), name='order_confirm'),
    path('order/<int:pk>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'),
    path('order/<int:pk>/awaiting_delivery/', views.OrderSetAwaitingDeliveryView.as_view(), name='order_awaiting_delivery'),
    path('order/<int:pk>/delivered/', views.OrderSetDeliveredView.as_view(), name='order_delivered'),
    path('cart/count/', views.cart_items_count_view, name='cart_items_count'),
] 

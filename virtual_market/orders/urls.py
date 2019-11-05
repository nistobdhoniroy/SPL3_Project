from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:myid>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:myid>/', views.remove_from_cart, name='remove-from-cart'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('remove-item-from-cart/<int:myid>/', views.remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('add-item-in-cart/<int:myid>/', views.add_single_item_in_cart,
         name='add-single-item-in-cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment')
]

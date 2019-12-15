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
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),

    path('testpayment/dupay', views.DUPayPaymentView.as_view(), name='dupay-payment'),
    path('confirm_order', views.ConfirmOrderView.as_view(), name='confirm_order'),

    path('tracker', views.OrderTracker.as_view(), name='tracker'),
    path('details/<int:order_id>', views.order_details, name='order_details'),

    path('list', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/process', views.OrderUpdateView.as_view(), name='process-order'),
]
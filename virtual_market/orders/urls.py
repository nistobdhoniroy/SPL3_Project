from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:myid>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:myid>/', views.remove_from_cart, name='remove-from-cart'),
]

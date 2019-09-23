from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>', views.store_view, name='store_view'),
    path('product/<int:myid>', views.productView, name='product_view'),
]
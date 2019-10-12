from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('<str:username>', views.store_view, name='store_view'),
    path('product/<int:myid>', views.productView, name='product_view'),
    path('<str:username>/product/new', views.ProductAddView.as_view(), name='add-product'),
    path('<str:username>/product/<int:pk>/update', views.ProductUpdateView.as_view(), name='update-product'),
    path('<str:username>/product/<int:pk>/delete', views.ProductDeleteView.as_view(), name='delete-product'),
    path('<str:username>/product_list', views.dashboardProductListView, name='product_list'),
]

from django.shortcuts import render
from .models import Product
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Create your views here.


def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'store/product_view.html', {'product': product[0]})


def store_view(request, username):
    requested_seller = User.objects.filter(username=username)

    product = Product.objects.filter(seller=requested_seller[0])
    # abc = User.objects.filter(id =user_id)
    return render(request, 'store/store_view.html', {'product': product})


class ProductAddView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['product_name', 'category', 'subcategory', 'price', 'description', 'product_image']

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.publish_date = datetime.datetime.now()
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['product_name', 'category', 'subcategory', 'price', 'description', 'product_image']

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.publish_date = datetime.datetime.now()
        return super().form_valid(form)

    def test_func(self):
        product = self.get_object()
        if self.request.user == product.seller:
            return True
        return False


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model= Product
    success_url='/'
    def test_func(self):
        product= self.get_object()
        if self.request.user == product.seller:
            return True
        return False
    
    
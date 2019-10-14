from django import forms
from django.shortcuts import get_object_or_404

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'price', 'description', 'product_image']


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'price', 'description', 'product_image']


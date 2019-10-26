from django import forms
from django.shortcuts import get_object_or_404

from .models import Product, Category, ProductComment


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(seller=user)


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['parent', 'category_title', 'category_description', 'slug']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Category.objects.filter(seller=user)


class CommentForm(forms.ModelForm):
    class Meta:
        model = ProductComment
        fields = ['content']

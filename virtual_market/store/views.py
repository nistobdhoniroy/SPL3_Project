from django.shortcuts import render, HttpResponse
from .models import Product, Category
from accounts.models import Seller

from django.contrib.auth import get_user_model
User = get_user_model()

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View
)
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, ProductUpdateForm, CategoryForm
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib import messages
from accounts.decorators import seller_required, customer_required

# Create your views here.


def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'store/product_view.html', {'product': product[0]})


def store_view(request, username):
    requested_seller = User.objects.filter(username=username)
    seller = Seller.objects.get(user= requested_seller[0])

    product = Product.objects.filter(seller=requested_seller[0])

    return render(request, 'store/str_view.html', {'product': product, 'seller': seller})


def home_view(request):
    sellers = User.objects.all().exclude(is_superuser=True)
    return render(request, 'store/home.html', {'sellers': sellers})


@method_decorator([login_required, seller_required], name='dispatch')
class CategoryAddView(CreateView):
    # model = Category
    # fields = ['parent', 'category_title', 'category_description', 'slug']
    template_name = 'dashboard/category_form.html'
    form_class = CategoryForm

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.status = True
        form.instance.publish_date = datetime.datetime.now()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CategoryAddView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@method_decorator([login_required, seller_required], name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['parent', 'category_title', 'category_description', 'status']
    context_object_name = 'category'
    template_name = 'dashboard/category_update.html'

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.category_set.all()

    def get_success_url(self):
        return reverse('category_list')


@method_decorator([login_required, seller_required], name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    context_object_name = 'category'
    template_name = "dashboard/category_confirm_delete.html"

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % category.category_title)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.category_set.all()

    def get_success_url(self, **kwargs):
        return reverse_lazy('category_list')


@method_decorator([login_required, seller_required], name='dispatch')
class CategoryListView(ListView):
    model = Category
    ordering = ('id', )
    context_object_name = 'category'
    template_name = 'dashboard/category_list.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return Category.objects.filter(seller=self.request.user)


@method_decorator([login_required, seller_required], name='dispatch')
class ProductAddView(CreateView):
    # model = Product
    # fields = ['name', 'category', 'price', 'description', 'image']
    template_name = 'dashboard/product_form.html'
    form_class = ProductForm

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.instance.publish_date = datetime.datetime.now()
        form.instance.seller = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ProductAddView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@method_decorator([login_required, seller_required], name='dispatch')
class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'category', 'price', 'description', 'image']
    context_object_name = 'product'
    template_name = 'dashboard/product_update.html'

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.product_set.all()

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.publish_date = datetime.datetime.now()
        return super().form_valid(form)

    def test_func(self):
        product = self.get_object()
        if self.request.user == product.seller:
            return True
        return False

    def get_success_url(self):
        return reverse('product_list')


@method_decorator([login_required, seller_required], name='dispatch')
class ProductDeleteView(DeleteView):
    model = Product
    context_object_name = 'product'
    template_name = "dashboard/product_confirm_delete.html"

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % product.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.product_set.all()

    def get_success_url(self, **kwargs):
        return reverse_lazy('product_list')


@login_required
def dashboard(request, username):
    requested_seller = request.user
    product = Product.objects.filter(seller=requested_seller)

    context = {
        'product': product,
        'seller': requested_seller}
    return render(request, 'dashboard/dash_base.html', context)


@login_required
@seller_required
def dashboardProductListView(request):

    product = Product.objects.filter(seller=request.user)
    context = {
                'product': product,
                'accounts': request.user}
    return render(request, 'dashboard/product_list.html', context)

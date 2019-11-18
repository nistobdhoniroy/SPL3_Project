from django.shortcuts import render, HttpResponse, redirect
from .models import Product, Category, ProductRating, ProductComment

from django.http import JsonResponse
import datetime
from django.contrib.auth.decorators import login_required
from .forms import ProductForm, ProductUpdateForm, CategoryForm, CommentForm
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from accounts.decorators import seller_required, customer_required
from django.contrib.auth import get_user_model
from virtual_market.mixins import AjaxRequiredMixin
from accounts.models import Seller
from .custom_functions import get_similar_products
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions


User = get_user_model()

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
    RedirectView
)


# Create your views here.


def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid).first()

    comments = ProductComment.objects.filter(item=product).order_by('-id')

    is_liked = False
    if product.likes.filter(id=request.user.id).exists():
        is_liked = True

    if request.method == 'POST':
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get('content')
            comment = ProductComment.objects.create(item=product, user=request.user, content=content)
            comment.save()

    else:
        comment_form = CommentForm()

    #same_products = Product.objects.filter(name=product.name).exclude(id=myid)

    same_products = get_similar_products(product.name, product.id)

    # print(type(test_same_products))

    context = {
        'product': product,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'total_likes': product.total_likes(),
        'same_products': same_products
    }

    return render(request, 'store/product_detail.html', context )


def store_view(request, username):
    requested_seller = User.objects.filter(username=username)
    seller = Seller.objects.get(user= requested_seller[0])

    product = Product.objects.filter(seller=requested_seller[0])

    return render(request, 'store/str_view.html', {'product': product, 'seller': seller})


def home_view(request):
    #sellers = User.objects.all().exclude(is_superuser=True)
    sellers = Seller.objects.all()
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
class SellerCategoryListView(ListView):
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
def sellerProductListView(request):

    product = Product.objects.filter(seller=request.user)
    context = {
                'product': product,
                'accounts': request.user}
    return render(request, 'dashboard/product_list.html', context)


class ProductRatingAjaxView(View):

    def post(self, *args, **kwargs):
        # if request.is_ajax():
        # raise Http404

        print("Hello I am in ")
        print(self.request.user)
        # if not self.request.user.is_authenticated():
        #     return JsonResponse({}, status=401)
        # credit card required **
        print("I am ok")

        # print("Hello PR1")
        #
        user = self.request.user
        product_id = self.request.POST.get("product_id")
        rating_value = self.request.POST.get("rating_value")
        # rating_value = self.request.POST['rating_value']
        #
        print(user, " Prod ", product_id, " Rating: ", rating_value)
        # print("I am here", product_id)
        # exists = Product.objects.filter(id=product_id).exists()
        # if not exists:
        #     return JsonResponse({}, status=404)
        #
        # try:
        #     product_obj = Product.objects.get(id=product_id)
        # except:
        #     product_obj = Product.objects.filter(id=product_id).first()
        #
        # print("Under Product Object ")
        #
        # # rating_obj, rating_obj_created = ProductRating.objects.get_or_create(
        # #     user=user,
        # #     product=product_obj
        # # )
        #
        # try:
        #     rating_obj = ProductRating.objects.get(user=user, product=product_obj)
        # except ProductRating.MultipleObjectsReturned:
        #     rating_obj = ProductRating.objects.filter(user=user, product=product_obj).first()
        # except:
        #     rating_obj = ProductRating()
        #     rating_obj.user = user
        #     rating_obj.product = product_obj
        #
        # rating_obj.rating = int(rating_value)
        # # myproducts = user.myproducts.products.all()
        # # if product_obj in myproducts:
        # #     rating_obj.verified = True
        #
        # print(rating_obj.rating)
        # print("Hello PR")
        # rating_obj.save()
        #
        data = {
            "success": True
        }
        return JsonResponse(data)


class ProductAPILikeToggle(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,  myid, format=None):
        prod = get_object_or_404(Product, id=myid)
        url_ = prod.get_redirect_url()

        user = self.request.user
        updated = False
        liked = False

        if user.is_authenticated:
            if user in prod.likes.all():
                liked = False
                prod.likes.remove(user)
            else:
                liked = True
                prod.likes.add(user)
            updated = True
        data = {
            "updated": updated,
            "liked": liked
        }
        return Response(data)




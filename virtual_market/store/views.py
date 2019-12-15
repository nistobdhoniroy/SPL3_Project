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
from .custom_functions import get_similar_products, get_real_vendor_similar_prods, recommendation_product
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.db.models import Q, Avg, Count
from orders.models import OrderItem, Order

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

    store = Seller.objects.get(user=product.seller)

    comments = ProductComment.objects.filter(item=product).order_by('-id')

    is_liked = False
    if product.likes.filter(id=request.user.id).exists():
        is_liked = True

    rating_avg = product.productrating_set.aggregate(Avg("rating"), Count("rating"))
    my_rating = 0
    if request.user.is_authenticated:
        rating_obj = ProductRating.objects.filter(user=request.user, product=product)
        if rating_obj.exists():
            my_rating = rating_obj.first().rating

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

    similar_products_real_vendor = get_real_vendor_similar_prods(product.name)

    # THis section for collaborative filtering recommendation system
    product_id = myid
    ratings = ProductRating.objects.filter(product__id=product_id)
    for rating in ratings:
        print(rating.product_id, rating.user.username, rating.rating)

    rating_result = recommendation_product(ratings)

    print(rating_result)

    recommended_products = []
    rating_thresh = 0
    if len(rating_result) > 0:
        print("Result:", rating_result)
        for prod_rate_id in rating_result:
            print(prod_rate_id, " ", rating_result[prod_rate_id])
            if (rating_result[prod_rate_id] > rating_thresh) and (product_id != prod_rate_id):
                print("Recommendation: ", prod_rate_id)
                rec_product = Product.objects.get(id=prod_rate_id)
                recommended_products.append(rec_product)

    # print(recommended_products)
    # print(ratings)

    # This ends here for collaborative filtering recommendation system

    context = {
        'product': product,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'store': store,
        'total_likes': product.total_likes(),
        'rating_avg': rating_avg,
        'my_rating': my_rating,
        'same_products': same_products,
        'similar_products_real_vendor': similar_products_real_vendor,
        'recommended_products': recommended_products
    }

    return render(request, 'store/product_detail.html', context)


def seller_product_view(request, myid):

    product = Product.objects.get(id=myid)

    store = Seller.objects.get(user=product.seller)

    comments = ProductComment.objects.filter(item=product).order_by('-id')

    rating_avg = product.productrating_set.aggregate(Avg("rating"), Count("rating"))
    my_rating = 0
    if request.user.is_authenticated:
        rating_obj = ProductRating.objects.filter(user=request.user, product=product)
        if rating_obj.exists():
            my_rating = rating_obj.first().rating

    product_id = myid
    ratings = ProductRating.objects.filter(product__id=product_id)

    buys = OrderItem.objects.filter(item__id=myid)

    total_buys=0
    for buy in buys:
        total_buys = total_buys + buy.quantity

    print("Total buys:", total_buys)

    context = {
        'product': product,
        'comments': comments,
        'store': store,
        'total_likes': product.total_likes(),
        'rating_avg': rating_avg,
        'my_rating': my_rating,
        'accounts': request.user,
        'total_buys': total_buys
    }

    return render(request, 'dashboard/product_detail_seller.html', context)


def store_view(request, username):
    requested_seller = User.objects.filter(username=username)
    seller = Seller.objects.get(user=requested_seller[0])

    product = Product.objects.filter(seller=requested_seller[0])

    return render(request, 'store/str_view.html', {'product': product, 'seller': seller, 'seller_user': requested_seller[0]})


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
@seller_required
def dashboard(request):
    context = {
        'accounts': request.user,
        "dashboard": "active"
    }
    return render(request, 'dashboard/seller_after_login.html', context)


@method_decorator([login_required, seller_required], name='dispatch')
class SellerProductListView(ListView):
    model = Product
    ordering = ('id', )
    context_object_name = 'product'
    template_name = 'dashboard/product_list.html'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user

        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

#
# @login_required
# @seller_required
# def sellerProductListView(request):
#
#     product = Product.objects.filter(seller=request.user)
#     context = {
#         'product': product,
#         'accounts': request.user,
#         "prod_list": "active"
#     }
#     return render(request, 'dashboard/product_list.html', context)


class ProductRatingAjaxView(View):
    def post(self, request, *args, **kwargs):

        # print(self.request)
        if not request.user.is_authenticated:
            return JsonResponse({}, status=401)
        # credit card required **

        user = request.user
        product_id = request.POST.get("product_id")
        rating_value = request.POST.get("rating_value")
        exists = Product.objects.filter(id=product_id).exists()

        if not exists:
            return JsonResponse({}, status=404)

        try:
            product_obj = Product.objects.get(id=product_id)
        except:
            product_obj = Product.objects.filter(id=product_id).first()

        rating_obj, rating_obj_created = ProductRating.objects.get_or_create(
            user=user,
            product=product_obj
        )

        try:
            rating_obj = ProductRating.objects.get(user=user, product=product_obj)
        except ProductRating.MultipleObjectsReturned:
            rating_obj = ProductRating.objects.filter(user=user, product=product_obj).first()
        except:
            rating_obj = ProductRating()
            rating_obj.user = user
            rating_obj.product = product_obj

        rating_obj.rating = int(rating_value)
        #
        # print(rating_obj.rating)
        # print("Hello PR")
        rating_obj.save()

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


class SearchItem(View):
    def get(self, request, format=None):

        query = request.GET.get('search')
        same_products = get_similar_products(query, 0)
        similar_products_real_vendor = get_real_vendor_similar_prods(query)

        # print(type(test_same_products))

        context = {
            'same_products': same_products,
            'similar_products_real_vendor': similar_products_real_vendor
        }

        print(query)
        return render(request, 'store/search.html', context)




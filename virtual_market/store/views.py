from django.shortcuts import render
from .models import Product
from django.contrib.auth.models import User

# Create your views here.


def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'store/product_view.html', {'product': product[0]})


def store_view(request, username):
    requested_seller = User.objects.filter(username=username)

    product = Product.objects.filter(seller=requested_seller[0])
    #abc = User.objects.filter(id =user_id)
    return render(request, 'store/store_view.html', {'product': product})

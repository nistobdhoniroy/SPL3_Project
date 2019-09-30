from django.shortcuts import render
from .models import Orders, OrderItems, OrderPlacer
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import json
import sys
# Create your views here.


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # order_placer= OrderPlacer(name=name, email=email, address=address, city=city,
        #                           zip_code=zip_code, phone=phone)

        #cart = request.localstorage.get('cart', {})
        #data = items_json.json()
        n = json.dumps(items_json)
        o = json.loads(n)
        print(o[0], o[1])

        # x= type(data)
        # total = 0
        # abc='';
        # for item in data:
        #     abc += item + ' '


        # for id, quantity in cart.items():
        #
        #     product = get_object_or_404(Product, pk=id)
        #     total += quantity * product.price
        #     order__items = OrderItems(
        #         order=order,
        #         item=product,
        #         quantity=quantity
        #     )
        #     order__items.save()
        return HttpResponse(n)

    return render(request, 'orders/checkout.html')

    #     {% for item in items_json %}
    #
    #     {% endfor %}
    #
    #
    #     #order.save()
    #     #update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
    #     #update.save()
    #     thank = True
    #     id = orders.order_id
    #     return render(request, 'orders/checkout.html', {'thank': thank, 'id': id})
    # return render(request, 'orders/checkout.html')

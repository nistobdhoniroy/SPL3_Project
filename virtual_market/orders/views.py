from django.shortcuts import render
from .models import Order, OrderItem, OrderPlacer, OrderUpdate
from store.models import Product
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import json
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

        order_placer = OrderPlacer(name=name, email=email, address=address, city=city,
                                   zip_code=zip_code, phone=phone)

        order_placer.save()
        order = Order(order_placer=order_placer)

        order.save()

        item_data = json.loads(items_json)

        my_list1 = []

        for key in item_data.keys():
            product_id = key[2:]
            product = Product.objects.get(id= product_id)
            quantity = item_data[key][0]
            my_list1.append(product)
            order_item = OrderItem(item=product, quantity=quantity, order=order)
            order_item.save()

        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()

        thank = True
        id = order.order_id
        return render(request, 'orders/checkout.html', {'thank': thank, 'id': id})

    return render(request, 'orders/checkout.html')


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        
        try:
            order_placer=OrderPlacer.objects.filter(email= email)
            return HttpResponse(f'{order_placer}')
            order = Order.objects.filter(order_id=orderId)

            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})

                order_items= OrderItem.objects.filter(order_id= orderId)
                
                items=[]  
                for item in order_items:
                    item_name= item.item.product_name
                    item_quantity= item.quantity
                    items.append({'name': item_name,'quantity': item_quantity })
                
                response = json.dumps([updates, items], default=str)

                return HttpResponse(response)
            else:
                return HttpResponse('Else{}')
        except Exception as e:
            return HttpResponse(f'exception {e}')

    return render(request, 'orders/tracker.html')
from django.shortcuts import redirect
from store.models import Product, Category, ProductRating, ProductComment
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone

@login_required
def add_to_cart(request, myid):
    item = get_object_or_404(Product, id=myid)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    print(order_qs)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order

        if order.items.filter(item__id=item.id).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect('product_view', myid=item.id)
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect('product_view', myid=item.id)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect('product_view', myid=item.id)


@login_required
def remove_from_cart(request, myid):
    item = get_object_or_404(Product, id=myid)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            print(order_item)

            print(order.items)
            order.items.remove(order_item)
            print(order.items)
            order.save()
            messages.info(request, "This item was removed from your cart.")
            return redirect('product_view', myid=item.id)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('product_view', myid=item.id)
    else:
        messages.info(request, "You do not have an active order")
        return redirect('product_view', myid=item.id)

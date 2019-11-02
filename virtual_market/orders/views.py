from django.shortcuts import redirect
from store.models import Product
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm


@login_required
def add_to_cart(request, myid):
    item = get_object_or_404(Product, id=myid)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

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

            order.items.remove(order_item)

            messages.info(request, "This item was removed from your cart.")
            return redirect('product_view', myid=item.id)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('product_view', myid=item.id)
    else:
        messages.info(request, "You do not have an active order")
        return redirect('product_view', myid=item.id)


class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'orders/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def remove_single_item_from_cart(request, myid):
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
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product_view", myid=id)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product_view", myid=id)

@login_required
def add_single_item_in_cart(request, myid):
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
            if order_item.quantity > 0:
                order_item.quantity += 1
                order_item.save()
            else:
                order.items.add(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product_view", myid=id)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product_view", myid=id)


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(request, "orders/checkout.html", context)

    def post(self, request,  *args, **kwargs):
        form = CheckoutForm(request.POST or None)
        print("The form is post")
        if form.is_valid():
            print(form.cleaned_data)
            # payment = request.POST.get("payment_option")
            # print(payment)
            print("The form is valid")

            return redirect('checkout')
        print("Where I am")
        return redirect('checkout')

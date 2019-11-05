from django.shortcuts import redirect
from store.models import Product
from .models import Order, OrderItem, BillingAddress, Payment
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm

import stripe
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"




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
        try:
            order=Order.objects.get(user= request.user, ordered=False)

            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionalities for the following
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                billing_address = BillingAddress(
                    user=request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    zip=zip,
                    # same_billing_address=same_billing_address,
                    # save_info=save_info,
                    payment_option=payment_option
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                print(form.cleaned_data)
                print("The form is valid")
                return redirect('checkout')
            messages.warning(request, "Failed Checkout")
            return redirect('checkout')
        except ObjectDoesNotExist:
            messages.error(request, "You do not have an active order")
            return redirect("order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "orders/payment.html")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int( order.get_total()*100 )


        try:
            charge= stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order.ordered = True
            order.payment = payment
            order.save()
            messages.success(self.request, "Your order was successful")
            return redirect("home_view")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("home_view")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("home_view")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("home_view")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("home_view")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("home_view")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("home_view")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("home_view")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")




from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from store.models import Product
from .models import Order, OrderItem, BillingAddress, Payment, OrderToSellers
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.generic import View, ListView, UpdateView
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm
import json
from accounts.decorators import seller_required, customer_required
from django.utils.decorators import method_decorator

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


# class OrderSummaryView(View):
#     def get(self, *args, **kwargs):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             context = {
#                 'object': order
#             }
#             return render(self.request, 'orders/order_summary.html', context)
#         except ObjectDoesNotExist:
#             messages.warning(self.request, "You do not have an active order")
#             return redirect("/")

class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            order_total = order.get_total()
            # print(order_total)

            seller_list = set()
            for items in order.items.all():
                seller_list.add(items.item.seller)

            # print(order.items.all())

            # order_list = {}
            # price_list = {}
            order_list_price_list = {}
            for single_seller in seller_list:
                # print(single_seller)
                product_order_list = []
                total_seller_price = 0
                for items in order.items.all():
                    if items.item.seller == single_seller:
                        # print(items)
                        total_seller_price += items.item.price * items.quantity
                        product_order_list.append(items)
                # price_list[single_seller] = total_seller_price
                # order_list[single_seller] = product_order_list
                order_list_price_list[single_seller] = [product_order_list, total_seller_price]
            # print(order_list)
            # print(price_list)
            # print(order_list_price_list)

            context = {
                'object': order_list_price_list,
                'order_total': order_total,
            }
            return render(self.request, 'orders/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("home_view")


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

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST or None)
        try:
            order = Order.objects.get(user=request.user, ordered=False)

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


# class PaymentView(View):
#     def get(self, *args, **kwargs):
#         return render(self.request, "orders/payment.html")
#
#     def post(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         token = self.request.POST.get('stripeToken')
#         amount = int( order.get_total()*100 )
#
#
#         try:
#             charge= stripe.Charge.create(
#                 amount=amount,
#                 currency="usd",
#                 source=token,
#             )
#             payment = Payment()
#             payment.stripe_charge_id = charge['id']
#             payment.user = self.request.user
#             payment.amount = order.get_total()
#             payment.save()
#
#             order.ordered = True
#             order.payment = payment
#             order.save()
#             messages.success(self.request, "Your order was successful")
#             return redirect("home_view")
#
#         except stripe.error.CardError as e:
#             body = e.json_body
#             err = body.get('error', {})
#             messages.warning(self.request, f"{err.get('message')}")
#             return redirect("home_view")
#
#         except stripe.error.RateLimitError as e:
#             # Too many requests made to the API too quickly
#             messages.warning(self.request, "Rate limit error")
#             return redirect("home_view")
#
#         except stripe.error.InvalidRequestError as e:
#             # Invalid parameters were supplied to Stripe's API
#             print(e)
#             messages.warning(self.request, "Invalid parameters")
#             return redirect("home_view")
#
#         except stripe.error.AuthenticationError as e:
#             # Authentication with Stripe's API failed
#             # (maybe you changed API keys recently)
#             messages.warning(self.request, "Not authenticated")
#             return redirect("home_view")
#
#         except stripe.error.APIConnectionError as e:
#             # Network communication with Stripe failed
#             messages.warning(self.request, "Network error")
#             return redirect("home_view")
#
#         except stripe.error.StripeError as e:
#             # Display a very generic error to the user, and maybe send
#             # yourself an email
#             messages.warning(
#                 self.request, "Something went wrong. You were not charged. Please try again.")
#             return redirect("home_view")
#
#         except Exception as e:
#             # send an email to ourselves
#             messages.warning(
#                 self.request, "A serious error occurred. We have been notifed.")
#             return redirect("home_view")
#
#         messages.warning(self.request, "Invalid data received")
#         return redirect("/payment/stripe/")
#

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "orders/payment.html")

    def post(self, *args, **kwargs):
        cart = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(cart.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = cart.get_total()
            payment.save()

            cart.ordered = True
            cart.payment = payment
            cart.save()

            cart_total = cart.get_total()
            print(cart_total)

            seller_list = set()
            for items in cart.items.all():
                seller_list.add(items.item.seller)

            order_list_price_list = {}
            for single_seller in seller_list:
                product_order_list = []
                total_seller_price = 0
                for items in cart.items.all():
                    if items.item.seller == single_seller:
                        # print(items)
                        total_seller_price += items.item.price * items.quantity
                        product_order_list.append(items)
                order_list_price_list[single_seller] = [product_order_list, total_seller_price]

            for key, value in order_list_price_list.items():
                items = value[0]
                seller_amount = value[1]
                print("Another Seller ", key, ": ")
                items_list = []
                for item in items:
                    # item_data = {}
                    # item_data['pid'] = item.item.id
                    # item_data["name"] = item.item.name
                    # item_data["quantity"] = item.quantity
                    # item_data["price"] = int(item.item.price)
                    #
                    # single_item_json = json.dumps(item_data)
                    # print(single_item_json)
                    #
                    # items_list.append(single_item_json)
                    #
                    price = int(item.item.price)
                    item_list = {item.item.id, item.item.name, item.quantity, price}

                    items_list.append(item_list)
                    # print(items_list)
                    # print(item.item.name, item.quantity, item.item.id, item.item.price)
                # print("I am items: ", items)
                # print(items_list)

                # item_json = json.dumps(items_list)
                #
                # print("Items JSON: ", item_json)

                # print("I am amount: ", amount)

                # print(items_list, " ", amount, " ", cart, " ", self.request.user, " ", key)

                try:
                    order_to_seller = OrderToSellers(amount=seller_amount, ordered=True,
                                                     order=cart, status='P', customer=self.request.user, seller=key)
                    order_to_seller.save()
                    print("Hello")
                except:
                    print("Could not make order")

            # print(order_list)
            # print(price_list)
            print(order_list_price_list)

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


class OrderTracker(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(id=8)
        print(order)
        order_all_sellers = OrderToSellers.objects.filter(order=order)
        print(order_all_sellers)

        for individual_order_seller in order_all_sellers:
            items = order.items.filter(item__seller=individual_order_seller.seller)
            # print("The Seller is: ", individual_order_seller.seller)
            # print(items)
        return render(self.request, "orders/tracker.html")

    def post(self, *args, **kwargs):
        orderId = self.request.POST.get('orderId', '')
        email = self.request.POST.get('email', '')

        print("In post")
        print(orderId)

        try:
            order = Order.objects.get(id=orderId)
            print(order)

            order_all_sellers = OrderToSellers.objects.filter(order=order)
            print(order_all_sellers)

            for individual_order_seller in order_all_sellers:
                items = order.items.filter(item__seller=individual_order_seller.seller)

            order_data_list = [order, order_all_sellers]
            print(order_data_list)

            response = json.dumps(order_data_list)
            print(response)

            # if len(order) > 0:

                # order_all_sellers = OrderToSellers.objects.filter(order=order)
                # print("Order post tracker")
                #
                # print("Hello:", order_all_sellers)
                # # print("Hello2:", order_all_sellers)
                # # order_data_list.append(order)
                # # order_data_list.append(order_all_sellers)
                # # print("Order Data List: ", order_data_list)
                #
                # # response = json.dumps(order_data_list)
                # #
                # # print(response)
                # for individual_order_seller in order_all_sellers:
                #     items = order.items.filter(item__seller=individual_order_seller.seller)
                #     print(items)
                # update = OrderUpdate.objects.filter(order_id=orderId)
                # updates = []
                # for item in update:
                #     updates.append({'text': item.update_desc, 'time': item.timestamp})
                #     response = json.dumps([updates, order[0].items_json], default=str)
            response = "ABC"
            return HttpResponse(response)
            # else:
            #     return HttpResponse('{}')
        except Exception as e:
            print(e)
            return HttpResponse('{}')
        pass


@method_decorator([login_required, seller_required], name='dispatch')
class OrderListView(ListView):
    model = OrderToSellers
    ordering = ('ordered_date', )
    context_object_name = 'order_to_seller'
    template_name = 'orders/order_dashboard/order_list.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return OrderToSellers.objects.filter(seller=self.request.user)


@method_decorator([login_required, seller_required], name='dispatch')
class OrderUpdateView(UpdateView):
    model = OrderToSellers
    fields = ['status']
    context_object_name = 'order_to_seller'
    template_name = 'orders/order_dashboard/order_update.html'

    def get_context_data(self, **kwargs):
        kwargs['accounts'] = self.request.user

        # print(self.kwargs['pk'])
        this_order = OrderToSellers.objects.get(id=self.kwargs['pk'])
        cart_id = this_order.order.id

        order = Order.objects.get(id=cart_id)
        items = order.items.filter(item__seller=self.request.user)
        kwargs['order_items'] = items

        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('order-list')

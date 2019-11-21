from django.db import models
from store.models import Product
from django.conf import settings
from accounts.models import User

# Create your models here.


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        'BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)

    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class OrderToSellers(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
        ('S', 'Shipped'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    items_json = models.CharField(max_length=5000, null=True, blank=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    amount = models.FloatField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    def __str__(self):
        return "Order:%s -Customer: %s -Seller:%s" %(self.order.id, self.customer, self.seller)


from django.db import models

# Create your models here.

class UserAddress(models.Model):
    BILLING = 'billing'
    SHIPPING = 'shipping'
    ADDRESS_TYPES = (
        (BILLING, 'Billing'),
        (SHIPPING, 'Shipping')
        )
    #user = models.ForeignKey(UserCheckout)
    type = models.CharField(max_length=100, choices=ADDRESS_TYPES)
    address = models.CharField(max_length=300)
    state =  models.CharField(max_length=100)
    zipcode = models.PositiveIntegerField()

    def __unicode__(self):
        return self.address

    def get_full_address(self):
        return '{0}, {1}, {2}'.format(self.address, self.state, self.zipcode)

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    billing_address = models.ForeignKey(UserAddress, related_name='billing_address')
    shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address')
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    phone = models.CharField(max_length=111, default="")


class OrderUpdate(models.Model):
    update_id  = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."

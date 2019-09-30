from django.db import models
from store.models import Product

# Create your models here.


class OrderPlacer(models.Model):
    name = models.CharField(max_length=90)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    phone = models.CharField(max_length=111, default="")
    email = models.CharField(max_length=111)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.address

    def get_full_address(self):
        return '{0}, {1}, {2}'.format(self.address, self.city, self.zipcode)


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_placer = models.OneToOneField(OrderPlacer, on_delete=models.CASCADE)
    timestamp = models.DateField(auto_now_add=True)


class OrderItems(models.Model):
    order = models.ForeignKey(Orders, null=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True)

    def __str__(self):
        return "{0} {1} @ {2}".format(self.quantity, self.item.product_name, self.item.price)


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:7] + "..."

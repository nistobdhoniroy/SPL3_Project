from django.db import models

# Create your models here.


class OtherProduct(models.Model):
    title = models.CharField(max_length=500)
    link = models.CharField(max_length=500)
    price = models.CharField(max_length=100)
    seller = models.CharField(max_length=100)

    def __str__(self):
        return self.title + "-" + self.seller

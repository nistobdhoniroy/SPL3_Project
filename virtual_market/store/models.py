from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    category_title = models.CharField(max_length=50, default="")
    category_description = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.category_title


class SubCategory(models.Model):
    sub_category_title = models.CharField(max_length=50, default="")
    sub_category_description = models.CharField(max_length=200, default="")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category_id = models.AutoField

    def __str__(self):
        return self.sub_category_title


class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)
    price = models.IntegerField(default=0)
    description = models.CharField(max_length=300)
    publish_date = models.DateField()
    product_image = models.ImageField(upload_to='store/product_images', default="")

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        return reverse("product_view", kwargs={"myid": self.pk})



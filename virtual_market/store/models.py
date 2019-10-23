from django.db import models
from accounts.models import User
from django.urls import reverse


class Category(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    category_title = models.CharField(max_length=50, default="")
    category_description = models.CharField(max_length=200, default="")
    slug = models.SlugField(unique=True, blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    publish_date = models.DateField()
    status = models.BooleanField()

    def __str__(self):
        full_path = [self.category_title]
        k = self.parent
        if k is not None:
            full_path.append(k.category_title)
            k = k.parent
        return '-->'.join(full_path[::-1])

    def get_absolute_url(self):
        return reverse("category_list")


class Product(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,  null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank= True)
    description = models.CharField(max_length=300)
    publish_date = models.DateField()
    image = models.ImageField(upload_to='store/product_images', default="")
    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("product_view", kwargs={"myid": self.pk})

    def get_absolute_url(self):
        return reverse("product_list")


from django.db import models
from accounts.models import User
from django.urls import reverse
from django.conf import settings
from django.utils import timezone


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
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="likes", blank=True)

    def __str__(self):
        return self.name

    def total_likes(self):
        return self.likes.count()

    # def get_absolute_url(self):
    #     return reverse("product_view", kwargs={"myid": self.pk})

    def get_absolute_url(self):
        return reverse("product_list")

    def get_redirect_url(self):
        return reverse("product_view", kwargs={"myid": self.pk})

    # def get_like_url(self):
    #     return reverse("like_product", kwargs={"myid": self.pk})

    def get_api_like_url(self):
        return reverse("like_product", kwargs={"myid": self.pk})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            'myid': self.id
        })

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={
            'myid': self.id
        })


class ProductRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)
    verified = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" %(self.rating)


class ProductComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return "%s-%s" %(self.item, self.content)

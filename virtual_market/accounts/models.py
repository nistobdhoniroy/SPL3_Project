from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from django.core.validators import RegexValidator

from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.


class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    store_name = models.CharField(max_length=100, default='test')
    store_location = models.CharField(max_length=200, default='test')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17,
                                    blank=True, default='99999999999999')  # validators should be a list
    store_logo = models.ImageField(default="default.jpg", upload_to="profile_pics")

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self,  *args, **kwargs):
        super(Seller, self).save(*args, **kwargs)
        img = Image.open(self.store_logo.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.store_logo.path)

#
# class Customer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     fullname = models.CharField(max_length=100)
#     address = models.CharField(max_length=200)
#     phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
#                                  message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
#     phone_number = models.CharField(validators=[phone_regex], max_length=17,
#                                     blank=True)  # validators should be a list
#     photo = models.ImageField(default="default.jpg", upload_to="profile_pics")
#
#     def __str__(self):
#         return f'{self.user.username} Profile'
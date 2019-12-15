from django.db import models
from django.conf import settings
# Create your models here.


class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(max_length=500)

    def __str__(self):
        return self.user.username
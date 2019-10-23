from django.contrib import admin
from .models import Seller, User

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active', 'is_seller', 'is_customer')

admin.site.register(User, UserAdmin)
admin.site.register(Seller)
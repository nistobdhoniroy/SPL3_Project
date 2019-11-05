from django.contrib import admin
from .models import Order, OrderItem, Payment, BillingAddress

# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'ordered', 'ordered_date')


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(BillingAddress)

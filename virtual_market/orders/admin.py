from django.contrib import admin
from .models import Order, OrderItem, OrderPlacer, OrderUpdate

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderPlacer)
admin.site.register(OrderUpdate)
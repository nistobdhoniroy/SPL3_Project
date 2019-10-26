from django.contrib import admin
from django.template.defaultfilters import slugify

from .models import Product, Category, ProductRating, ProductComment
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['category_title']
    list_display = ('category_title', 'status', 'parent', 'seller')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(ProductRating)
admin.site.register(ProductComment)
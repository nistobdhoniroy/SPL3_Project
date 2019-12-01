from django.contrib import admin
from django.template.defaultfilters import slugify

from .models import Product, Category, ProductRating, ProductComment
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['category_title']
    list_display = ('category_title', 'status', 'parent', 'seller')


class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(ProductRating, RatingAdmin)
admin.site.register(ProductComment)
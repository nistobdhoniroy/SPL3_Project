from django import template
from ..models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            print('I am in cart item count')
            return qs[0].items.count()
        print("I am not")
        return 0

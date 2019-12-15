from django.shortcuts import render
from .models import Contact

# Create your views here.


def contact(request):
    if request.method == "POST":
        user = request.user
        desc = request.POST.get('desc', '')

        message = Contact(user=request.user, message=desc)
        message.save()

    return render(request, 'market/contact.html')
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .models import Profile
from django.views.generic import DetailView


# Create your views here.

def register(request):
    if request.method == 'POST':
        form= UserRegisterForm(request.POST)
        print(form.errors)
        if form.is_valid():
            seller= form.save(commit= False)
            seller.is_active = False
            seller.save()
            # username = form.cleaned_data.get('username')
            # messages.success(request, f'Account created for {username}.  You are now able to login')
            # return redirect('login')
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('acc_active_email.html', {
                'seller': seller,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(seller.pk)),
                'token':account_activation_token.make_token(seller),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')   
    else:
        form= UserRegisterForm()
    return render(request, 'seller/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        seller = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        seller = None
    if seller is not None and account_activation_token.check_token(seller, token):
        seller.is_active = True
        seller.save()
        login(request, seller)
        # return redirect('home')
        return render(request, 'seller/register_activation.html')
    else:
        return HttpResponse('Activation link is invalid!')
  

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated.')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context={
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'seller/profile.html', context)


def view_profile(request, username):
    seller = User.objects.get(username=username)
    return render(request, 'seller/seller_profile.html', {"seller":seller})


def seller_home(request):
    context={
        'sellers': User.objects.all()
    }
    return render(request, 'seller/seller_home.html', context)


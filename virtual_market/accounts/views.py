from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomerSignUpForm, SellerSignUpForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from accounts.models import User
from django.core.mail import EmailMessage
from .models import Seller
from django.views.generic import CreateView, DetailView, View


# Create your views here.

def register(request):

    return render(request, 'accounts/register.html')


class CustomerSignUpView(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'accounts/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        mail_subject = 'Activate your Customer account.'
        message = render_to_string('acc_active_email.html', {
            'accounts': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        return HttpResponse('Please confirm your email address to complete the registration')


class SellerSignUpView(CreateView):
    model = User
    form_class = SellerSignUpForm
    template_name = 'accounts/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'seller'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        mail_subject = 'Activate your Seller account.'
        message = render_to_string('acc_active_email.html', {
            'accounts': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        return HttpResponse('Please confirm your email address to complete the registration')


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
        return render(request, 'accounts/register_activation.html')
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
        'p_form': p_form,
        'accounts': request.user,
    }
    return render(request, 'dashboard/dashboard.html', context)


def view_profile(request):
    user = request.user
    return render(request, 'accounts/seller_profile.html', {"accounts":user})


def seller_home(request):
    context={
        'sellers': User.objects.all()
    }
    return render(request, 'accounts/seller_home.html', context)


class SellerProfile(CreateView):
    model = Seller
    fields = ['store_name', 'store_location', 'store_logo']


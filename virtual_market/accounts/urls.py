from django.conf.urls import url
from django.urls import path,include
from accounts import views as seller_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', seller_views.register, name='register'),
    path('register/customer', seller_views.CustomerSignUpView.as_view(template_name='accounts/signup-form.html'), name='register_customer' ),
    path('register/seller', seller_views.SellerSignUpView.as_view(template_name='accounts/signup-form.html'), name='register_seller' ),
    path('login/', auth_views.LoginView.as_view(template_name= 'accounts/login.html'), name='login'),
    
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        seller_views.activate, name='activate'),

    path('logout/', auth_views.LogoutView.as_view(template_name= 'accounts/logout.html'), name='logout'),  
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(template_name= 'accounts/password_reset.html'), 
        name='password_reset'),
    path('password-reset/done', 
        auth_views.PasswordResetDoneView.as_view(template_name= 'accounts/password_reset_done.html'), 
        name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>',
        auth_views.PasswordResetConfirmView.as_view(template_name= 'accounts/password_reset_confirm.html'), 
        name='password_reset_confirm'),
    path('password-reset/complete', 
        auth_views.PasswordResetDoneView.as_view(template_name= 'accounts/password_reset_complete.html'), 
        name='password_reset_complete'),
    #path('profile/', seller_views.profile, name='profile'),
    #url(r'profile/(?P<username>[a-zA-Z0-9]+)$', seller_views.view_profile, name='view-profile'),

    path('profile/', seller_views.view_profile, name='view_profile'),
    # path('', seller_views.seller_home, name='seller_home'),
]

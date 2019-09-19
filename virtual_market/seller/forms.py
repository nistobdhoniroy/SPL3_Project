from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email= forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model= User
        fields= ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This Email is currently in use. Please Try Again!')
        return email


class UserUpdateForm(forms.ModelForm):
    email= forms.EmailField()

    class Meta:
        model= User
        fields= ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['store_name','store_location','store_logo']
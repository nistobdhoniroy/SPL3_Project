from django import forms

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'DUPAY')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Street Address',
        "id": 'address'
    }))
    apartment_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Apartment Address',
        "id": 'address-2'
    }))

    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        "id": 'zip'
    }))

    same_billing_address = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    save_info = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

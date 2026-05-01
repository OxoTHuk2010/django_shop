from django import forms


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.Textarea, max_length=1000)
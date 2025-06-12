from django import forms
from .models import Order, Payment 
 

class OrderForm(forms.ModelForm):
    COUNTRY_CHOICES = [
        ('', 'Select Country'),
        ('Bangladesh', 'Bangladesh'),
        ('India', 'India'),
    ]

    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        required=True
    )
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address_line_1', 'country', 'state', 'city', 'order_note']
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        
        # প্রতিটি ফিল্ডে required অ্যাট্রিবিউট যোগ করুন
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'First Name',
            'required': 'required'  # HTML required অ্যাট্রিবিউট
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Last Name',
            'required': 'required'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email',
            'placeholder': 'Email',
            'required': 'required'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Phone',
            'required': 'required'
        })
        self.fields['address_line_1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Address',
            'required': 'required'
        })
        self.fields['state'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'State',
            'required': 'required'
        })
        self.fields['city'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'City',
            'required': 'required'
        })
        self.fields['order_note'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Notes',
            'rows': 3
        })


# Payment Form
class PaymentForm(forms.ModelForm):
   class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(attrs={'class': 'form-check-input form-check-inline'}),
        }
        labels = {
            'payment_method': '',
        }

   def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['payment_method'].choices = Payment.PAYMENT_METHOD_CHOICES
        self.initial['payment_method'] = None
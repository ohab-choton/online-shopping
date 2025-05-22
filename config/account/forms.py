from django import forms
from .models import UserAccount
from django.contrib.auth.forms import PasswordResetForm
import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password'}))
    class Meta:
        model= UserAccount
        fields= ['first_name','last_name','phone_number','email','password']

    def clean(self):
        cleaned_data=super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )
        
    
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone_number) != 11:
            raise forms.ValidationError("Phone number must be exactly 11 digits.")
        return phone_number
    

#reset password send link via mail
class ResetPasswordForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
class BackgroundEmailSender(threading.Thread):
    def __init__(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        self.subject_template_name = subject_template_name
        self.email_template_name = email_template_name
        self.context = context
        self.from_email = from_email
        self.to_email = to_email
        self.html_email_template_name = html_email_template_name
        threading.Thread.__init__(self)

    def run(self):
        subject = render_to_string(self.subject_template_name, self.context).strip()
        body = render_to_string(self.email_template_name, self.context)
        html_message = render_to_string(self.html_email_template_name, self.context) if self.html_email_template_name else None

        email_message = EmailMultiAlternatives(subject, strip_tags(body), self.from_email, [self.to_email])
        if html_message:
            email_message.attach_alternative(html_message, 'text/html')
        email_message.send()


class ResetPasswordConfirmForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Password" )
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password" )

    def __init__(self, *args, **kwargs):
        self.user=kwargs.pop('user')
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    # Correct Placement of clean() Outside Meta
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 != new_password2:
            raise forms.ValidationError("New Password and Confirm Password do not match.")  # ✅ Correct error handling
        return cleaned_data
    
    def save(self, commit=True):
        """ Update the user's password """
        
        self.user.set_password(self.cleaned_data["new_password1"])
        
        if commit:
            self.user.save()
        return self.user
from django.shortcuts import render, redirect
from .forms import RegistrationForm,ResetPasswordForm, ResetPasswordConfirmForm, BackgroundEmailSender
from .models import UserAccount
from django.contrib import messages,auth
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView

from django.core.mail import send_mail

# Create your views here.

def get_register(request):
    if request.method == 'POST':
        form=RegistrationForm(request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@')[0]
            user=UserAccount.objects.create_user(first_name=first_name,last_name=last_name,  email=email,username=username,password=password)
            user.phone_number=phone_number
            user.save()
            messages.success(request, 'Registration successful')
            return redirect('login')

    else:
        form=RegistrationForm()

    context={
        'form':form
    }
    return render(request, 'account/register.html',context)



def get_login(request):
    # Check if user is already logged in and is admin/staff
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        # Admin is trying to access regular login, redirect to admin
        messages.info(request, 'You are logged in as admin. Please use admin panel.')
        return redirect('/admin/')
    
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=auth.authenticate(email=email,password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                messages.error(request, 'You are not allowed to login as a staff or superuser')
                return redirect('login')
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('index')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'account/login.html')

@login_required(login_url='login')
def get_logout(request):
    auth.logout(request)
    messages.success(request, 'Logout successful')
    return redirect('login')


#custom password reset for template arrangement
class EmailToSendResetPassword(PasswordResetView):
    template_name = "account/password-reset.html"
    form_class = ResetPasswordForm
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        """Start email sending in a thread instead of blocking"""
        opts = {
            'use_https': self.request.is_secure(),
            'request': self.request,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'html_email_template_name': self.html_email_template_name,
            'from_email': self.from_email,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)  # calls form.save(), which sends mail

        return super().form_valid(form)

    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        """Overridden to use threaded sender"""
        BackgroundEmailSender(
            subject_template_name, email_template_name, context,
            from_email, to_email, html_email_template_name
        ).start()

class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = "account/password_reset_confirm.html"
    form_class = ResetPasswordConfirmForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        messages.success(self.request, "Password reset successfully!")
        return super().form_valid(form)

   



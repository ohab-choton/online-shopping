from django.urls import path
from account.views import EmailToSendResetPassword, ResetPasswordConfirmView
from django.contrib.auth.views import PasswordResetDoneView


from . import views



urlpatterns = [
    path('register/',views.get_register , name='register'),
    path('login/',views.get_login , name='login'),
    path('logout/',views.get_logout , name='logout'),
    


    path('password_reset/', EmailToSendResetPassword.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
    
   


    
    
]

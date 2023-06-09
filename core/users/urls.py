from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView

from . import views

app_name = "users"
print(settings.STATIC_ROOT)
print(settings.STATIC_URL)
urlpatterns = [
    path('signup/', views.register, name='register'),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
         views.activate, name='activate'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('reset-password/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('reset-password/confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                          success_url='/users/reset-password/complete/'),
         name='password_reset_confirm'),
    path('reset-password/complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

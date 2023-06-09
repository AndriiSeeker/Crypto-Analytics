import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cloudinary
from cloudinary.uploader import upload
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.hashers import make_password

from .forms import RegisterForm, LoginForm, ProfileForm, UserForm, PasswordChangeForm, UpdateAvatarFrom
from .models import User, Profile
from .tokens import account_activation_token


def send_email(message, to_email, ) -> None:
    with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_HOST_PORT) as server:
        try:
            from_email = settings.EMAIL_HOST_USER
            from_email_password = settings.EMAIL_HOST_PASSWORD
            server.login(from_email, from_email_password)
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = 'Confirm registration'

            msg.attach(MIMEText(message, 'html'))

            print(msg)
            server.send_message(msg)
        except Exception as err:
            print(err)


def activate(request, uidb64, token):
    user_model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user_model.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        return redirect(to="users:login")
    else:
        messages.error(request, 'Activation link is invalid! Try again')


def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username already exist')
            return redirect(to="users:register")
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email is taken, choose another one')
            return redirect(to="users:register")
        else:
            if password1 == password2:
                user = User.objects.create_user(
                    first_name=first_name, last_name=last_name, username=username, email=email,
                    password=password1)
                user.save()
                current_site = get_current_site(request)
                message = render_to_string('users/activate_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = email
                send_email(message, to_email)
                messages.success(request, "Please confirm your email address to complete the registration")
            else:
                messages.error(request, "Passwords don't match")
    return render(request, 'users/register.html', {"form": form})


def login_user(request):
    form = LoginForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                if user.is_email_verified:
                    login(request, user)
                    return redirect(to='cryptocurrency:home')
                else:
                    messages.error(request, 'Please confirm your email to log in')
            else:
                messages.error(request, 'Your account is disabled')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(to='cryptocurrency:home')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    html_email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:login')
    # success_message = "An email with instructions to reset your password has been sent to %(email)s."
    subject_template_name = 'users/password_reset_subject.txt'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def post(self, request):
        post_data = request.POST or None
        file_data = request.FILES or None
        user = request.user
        profile = Profile.objects.get(user=user)

        if 'update_user' in request.POST:
            first_name = post_data.get("first_name")
            last_name = post_data.get("last_name")
            username = post_data.get("username")
            email = post_data.get("email")
            bio = post_data.get("bio")

            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.save()

            profile.bio = bio
            profile.save()
            user_updated_successfully = True
            if user_updated_successfully:
                messages.success(request, 'User information updated successfully!')
            else:
                messages.error(request, 'Failed to update user info.')
            return redirect(to='users:profile')

        if 'update_password' in request.POST:
            current_password = post_data.get('current_password')
            new_password = post_data.get('new_password')

            if check_password(current_password, user.password):
                hashed_new_password = make_password(new_password)
                user.password = hashed_new_password
                user.save()
                update_session_auth_hash(request, user)
                password_updated_successfully = True
                if password_updated_successfully:
                    messages.success(request, 'Password updated successfully!')
                else:
                    messages.error(request, 'Failed to update password.')
            else:
                messages.error(request, "Wrong password")
            return redirect(to='users:profile')

        if 'update_photo' in request.POST:
            username = user.username
            image_file = file_data.get('image')

            if image_file:
                cloudinary.config(
                    cloud_name=os.environ.get('CLOUDINARY_NAME'),
                    api_key=os.environ.get('CLOUDINARY_API_KEY'),
                    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
                    secure=True
                )

                r = cloudinary.uploader.upload(image_file, public_id=f'Crypto/{username}',
                                               overwrite=True)
                image_url = cloudinary.CloudinaryImage(f'Crypto/{username}') \
                    .build_url(width=150, height=150, crop='fill', version=r.get('version'))

                # Save the image URL to the user's profile or wherever you need to store it
                profile = Profile.objects.get(user=user)
                profile.avatar = image_url
                profile.save()

                photo_updated_successfully = True
                if photo_updated_successfully:
                    messages.success(request, 'Avatar updated successfully!')
                else:
                    messages.error(request, 'Failed to update Avatar')
            else:
                messages.error(request, 'Failed to get image')
            return redirect(to='users:profile')

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)
        user_form = UserForm(instance=user)
        first_name = user.first_name
        last_name = user.last_name
        username = user.username

        profile = Profile.objects.get(user=request.user)
        bio = profile.bio
        initial_data = {
            'bio': bio
        }
        profile_form = ProfileForm(initial=initial_data)
        avatar_url = profile.avatar

        change_password_form = PasswordChangeForm()
        update_avatar = UpdateAvatarFrom()

        context = self.get_context_data(
            user_form=user_form,
            profile_form=profile_form,
            change_password_form=change_password_form,
            update_avatar=update_avatar,
            first_name=first_name,
            last_name=last_name,
            username=username,
            bio=bio,
            avatar=avatar_url
        )

        return self.render_to_response(context)

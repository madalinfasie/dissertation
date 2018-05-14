import datetime, random, hashlib
import pytz
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from .forms import UserForm, ForgotPasswordForm, ChangePasswordForm
from .models import UserProfile, UserPassChange


def send_reset_pass_request(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            # check if email is valid
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                user = User.objects.get(email=form.cleaned_data['email'])
                # EMAIL CONFIRMATION
                salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
                pass_key = hashlib.sha1((salt + user.username).encode('utf-8')).hexdigest()
                key_expires = datetime.datetime.today() + datetime.timedelta(2)

                # Create and save their profile
                try:
                    new_profile = UserPassChange.objects.get(user=user)
                except:
                    new_profile = None

                if new_profile is None:
                    new_profile = UserPassChange(user=user,
                                                 pass_key=pass_key,
                                                 key_expires=key_expires)
                    new_profile.save()
                else:
                    new_profile.pass_key = pass_key
                    new_profile.key_expires = key_expires
                    new_profile.save()

                # Send an email with the confirmation link
                email_subject = 'BlitzNews - Reset Your Password'
                email_body = """Hello, %s,\n\n
To change your password, click this link within 48 hours: \n\n
http://testblitz.com:8000/users/password/change/%s""" % (user.username,
                                                         new_profile.pass_key)

                
                send_mail(email_subject, email_body, 'messager@localhost.com', [user.email])

                return HttpResponseRedirect('/users/login/')
            else:
                custom_err = "This e-mail is not valid."
                return render(request, 'register/password_send_req.html',
                              {'form': form, 'custom_err': custom_err})
    else:
        form = ForgotPasswordForm()

    return render(request, 'register/password_send_req.html', {'form': form})


def change_password(request, pass_key):
    pwd_request = get_object_or_404(UserPassChange,
                                    pass_key=pass_key)
    if pwd_request.key_expires < datetime.datetime.now(pytz.utc):
        return render(request, 'register/password_change.html', {'validlink': False})

    user = pwd_request.user
    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            user_ch = form.save()
            update_session_auth_hash(request, user_ch)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('/users/login/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'register/password_change.html', {'form': form, 'validlink': True})


def register_user(request):
    if request.method == 'POST':
        register_form = UserForm(request.POST)
        if register_form.is_valid():
            # check if username or email are not already taken
            if User.objects.filter(username=register_form.cleaned_data['username']).exists() or \
                    User.objects.filter(email=register_form.cleaned_data['email']).exists():
                if User.objects.filter(username=register_form.cleaned_data['username']).exists():
                    custom_err = "This username it's already taken."
                    return render(request, 'register/register.html',
                                  {'register_form': register_form, 'custom_err': custom_err})
                if User.objects.filter(email=register_form.cleaned_data['email']).exists():
                    custom_err = "This e-mail it's already in use."
                    return render(request, 'register/register.html',
                                  {'register_form': register_form, 'custom_err': custom_err})
            else:
                # create new user
                user = User.objects.create_user(register_form.cleaned_data['username'],
                                                register_form.cleaned_data['email'],
                                                register_form.cleaned_data['password'])
                user.first_name = register_form.cleaned_data['first_name']
                user.last_name = register_form.cleaned_data['last_name']
                user.save()


                # EMAIL CONFIRMATION
                # Without key (use the link to deactivate the account)
                # Send an email with the confirmation link
                email_subject = 'Your new BlitzNews account confirmation'
                email_body = "Hello, %s, and thanks for signing up for an \
                                BlitzNews account!\n\n" % (user.username)

                send_mail(email_subject, email_body, 'messager@localhost.com', [user.email], fail_silently=False)

                # # With key
                # salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
                # activation_key = hashlib.sha1((salt + user.username).encode('utf-8')).hexdigest()
                # key_expires = datetime.datetime.today() + datetime.timedelta(2)
                #
                # # Create and save their profile
                # new_profile = UserProfile(user=user,
                #                           activation_key=activation_key,
                #                           key_expires=key_expires)
                # new_profile.save()
                #
                # # Send an email with the confirmation link
                # email_subject = 'Your new BlitzNews account confirmation'
                # email_body = "Hello, %s, and thanks for signing up for an \
                # BlitzNews account!\n\nTo activate your account, click this link within 48 \
                #         hours:\n\nhttp://127.0.0.1:8000/users/confirm/%s" % (user.username,
                #                                                              new_profile.activation_key)
                #
                # send_mail(email_subject, email_body, 'messager@localhost.com', [user.email], fail_silently=False)

                return HttpResponseRedirect('/')
    else:
        register_form = UserForm()

    return render(request, 'register/register.html', {'register_form': register_form})


def success(request):
    return HttpResponseRedirect('/')


# confirm registration
def confirm(request, activation_key):
    if request.user.is_authenticated():
        return render(request, 'register/confirm.html', {'has_account': True})

    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)

    if user_profile.used_key:
        return render(request, 'register/confirm.html', {'used_key':True})

    if user_profile.key_expires < datetime.datetime.now(pytz.utc):
        return render(request, 'register/confirm.html', {'expired': True})

    user_account = user_profile.user
    user_account.is_active = True
    user_account.save()

    user_profile.used_key = True
    user_profile.save()

    return render(request, 'register/confirm.html', {'success': True})

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout, update_session_auth_hash
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View


import logging

logger = logging.getLogger("Django Starter Project")

import json
from operator import itemgetter

# Dates and
from django.utils import timezone
from datetime import datetime, timedelta

# Settings
from django.conf import settings

# Models
from accounts.models import *
from files.models import *
from django.db.models import Q

# Utils
from core.utils import *

# Accounts
from accounts.forms import *

# Forms
from accounts.forms import *

# Tasks
from files.tasks import *

# Messaging
from messaging.tasks import *

import time
from django.contrib.auth import authenticate, login


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(
                "items",
            )
        else:
            form = UserLoginForm()
            hide_login = True
            return render(request, self.template_name, locals())

    def post(self, request):
        form = UserLoginForm(request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")

        if form.is_valid():
            user = get_object_or_404(CustomUser, email=email)

            if user.is_verified: 
                auth_obj = authenticate(
                    request=request, username=user.username, password=password
                )
                if auth_obj:
                    login(request, auth_obj)
                    return redirect(
                        "items",
                    )
            else:
                context = {
                    "email": user.email,
                    "render_kind": "account_verification",
                    "hide_signup": True,
                }

                return render(request, "accounts/confirmation.html", context)

        else:
            hide_login = True
            return render(request, self.template_name, locals())


class UserRegistrationView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(
                "home",
            )
        else:
            form = SignUpForm()
            hide_signup = True
            return render(request, "accounts/register.html", locals())

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():

            # Save the new user
            user = form.save()

            # Create the user extras
            user_extras = UserExtras()
            user_extras.display_name = user.first_name
            user_extras.save()
            user.user_extras = user_extras
            user.save()

            # Create a unique verification link
            verification_key = uuid.uuid4().hex
            verification_link = f"{settings.BASE_URL}create-account?key={verification_key}"

            MailLinkModel.objects.create(
                user=user, key=verification_key, link_type="sign_up"
            )

            # Send verification email to the user
            message = f"""
            Hello {user.first_name.title()},\n
            Thanks so much for signing up for Django Starter Project!\n
            Use the link below to confirm your account:\n
            {verification_link}\n
            If you didn't sign up for Django Starter Project, please ignore this email.\n
            Sincerely,\n
            Django Starter Project Support
            """
            send_general_email.delay(user.email, "Verify your Django Starter Project account", message)

            # Send email alert to admin
            to = "hello@djangostarterproject.com"
            subject = "[Django Starter Project] New Sign Up"
            message = "Hey - someone signed up"
            if user:
                message = message + " | User: " + user.email
            send_general_email.delay(to, subject, message)

            context = {
                "email": user.email,
                "render_kind": "signup",
                "hide_signup": True,
            }

            return render(request, "accounts/confirmation.html", context)
        else:
            hide_signup = True
            return render(request, "accounts/register.html", locals())


class VerifyUserLinkView(View):

    def get(self, request):
        get_key = request.GET.get("key")
        link_obj = get_object_or_404(MailLinkModel, key=get_key)

        if link_obj:
            
            if not link_obj.is_delete:

                user = get_object_or_404(CustomUser, pk=link_obj.user_id)
                if link_obj.link_type == "sign_up":
                    user.is_verified = True
                    user.save()


                    link_obj.is_delete = True
                    link_obj.save()

                    user_name = user.get_full_name()

                    return render(
                        request,
                        "accounts/confirmation.html",
                        {"render_kind": "signup_confirmed", "hide_signup": True},
                    )
                elif link_obj.link_type == "reset_password":
                    request.session["forgot_password_user_pk"] = user.pk

                    link_obj.is_delete = True
                    link_obj.save()
                    return redirect("create_new_password")
            
            else:
                return render(
                        request,
                        "accounts/confirmation.html",
                        {"render_kind": "invalid_key", "hide_signup": True},
                    )

        return render(
            request,
            "accounts/confirmation.html",
            {"render_kind": "invalid_key", "hide_signup": True},
        )

class ResendAccountVerificationEmail(View):
    def post(self, request):
        
        data = json.loads(request.body)
        email = data.get('email')

        try:
            # Fetch user based on the email
            user = CustomUser.objects.get(email=email)
              
            existing_mail_links = MailLinkModel.objects.filter(user=user, link_type='sign_up', is_delete=False)

            for existing_mail_link in existing_mail_links:
                existing_mail_link.is_delete = True
                existing_mail_link.save()
            
            # Create a new verification link
            new_verification_key = uuid.uuid4().hex
            new_verification_link = f"{settings.BASE_URL}create-account?key={new_verification_key}"
            MailLinkModel.objects.create(
                user=user, key=new_verification_key, link_type="sign_up"
            )

            # Send verification email to the user
            message = f"""
            Hello {user.first_name.title()},\n
            Thanks so much for signing up for Django Starter Project!\n
            Use the link below to confirm your account:\n
            {new_verification_link}\n
            If you didn't sign up for Django Starter Project, please ignore this email.\n
            Sincerely,\n
            Django Starter Project Support
            """
            send_general_email.delay(user.email, "Verify your Django Starter Project account", message)


            context = {
                "email": user.email,
                "render_kind": "signup",
                "hide_signup": True,
            }

            return render(request, "accounts/confirmation.html", context)

        except ObjectDoesNotExist:
            context = {
                "message_title": "Resend Verification Failed",
                "message_body": "No account found with the provided email address. Please verify your email and try again.",
                "message_type": "error",
            }
            return render(request, "accounts/custom-message.html", context)

        except Exception as e:
            context = {
                "message_title": "Resend Verification Failed",
                "message_body": "An unexpected error occurred. Please try again later or contact support if the problem persists.",
                "message_type": "error",
            }
            return render(request, "accounts/custom-message.html", context)


class ResetPasswordView(View):
    template_name = "accounts/password-reset.html"

    def get(self, request):
        form = UserPasswordResetForm()
        return render(request, self.template_name, {'form': form, 'hide_signup': True})

    def post(self, request):
        form = UserPasswordResetForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data.get("email")
            try:
                user = CustomUser.objects.get(email=email)
            except ObjectDoesNotExist:
                form.add_error('email', 'No account found with this email')
                return render(request, self.template_name, {'form': form, 'hide_signup': True})

            user_email = user.email
            user_name = user.get_full_name()

            key = uuid.uuid4().hex
            link = f"{settings.BASE_URL}forgot-password?key={key}"

            MailLinkModel.objects.create(
                user=user, link_type="reset_password", key=key
            )

            message = f"""
            Hello {user_name},\n
            We received a request to change the password for the account with the email {user_email}\n
            Use the link below to reset your password:\n
            {link}\n
            If you don't want to reset your password or you did not request this change, you can ignore this email.\n
            Sincerely,\n
            Django Starter Project Support
            """

            send_general_email.delay(user_email, "Reset your Django Starter Project password", message)

            context = {
                "email": user_email,
                "render_kind": "reset_password",
                "hide_signup": True,
            }

            # messages.success(request, 'Verification email has been sent')
            return render(request, "accounts/confirmation.html", context)

        return render(request, self.template_name, {'form': form, 'hide_signup': True})


class ResendPasswordResetVerificaitonEmail(View):

    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')

        try:
            # Fetch user based on the email
            user = CustomUser.objects.get(email=email)
              
            existing_mail_links = MailLinkModel.objects.filter(
                            user=user, link_type="reset_password", is_delete=False
                )
            
            for existing_mail_link in existing_mail_links:
                existing_mail_link.is_delete = True
                existing_mail_link.save()

            key = uuid.uuid4().hex
            link = f"{settings.BASE_URL}forgot-password?key={key}"

            MailLinkModel.objects.create(
                user=user, link_type="reset_password", key=key
            )

            user_email = user.email
            user_name = user.get_full_name()

            message = f"""
            Hello {user_name},\n
            We received a request to change the password for the account with the email {user_email}\n
            Use the link below to reset your password:\n
            {link}\n
            If you don't want to reset your password or you did not request this change, you can ignore this email.\n
            Sincerely,\n
            Django Starter Project Support
            """

            send_general_email.delay(user_email, "Reset your Django Starter Project password", message)

            context = {
                "email": user.email,
                "render_kind": "signup",
                "hide_signup": True,
            }

            return render(request, "accounts/confirmation.html", context)

        except ObjectDoesNotExist:
            context = {
                "message_title": "Resend Verification Failed",
                "message_body": "No account found with the provided email address. Please verify your email and try again.",
                "message_type": "error",
            }
            return render(request, "accounts/custom-message.html", context)

        except Exception as e:
            context = {
                "message_title": "Resend Verification Failed",
                "message_body": "An unexpected error occurred. Please try again later or contact support if the problem persists.",
                "message_type": "error",
            }
            return render(request, "accounts/custom-message.html", context)


class CreateNewPasswordView(View):
    template_name = "accounts/password-reset-form.html"

    def get(self, request):
        user_pk = request.session.get("forgot_password_user_pk")
        user = get_object_or_404(CustomUser, pk=user_pk)

        form = UserSetPasswordForm(user=user)
        return render(request, self.template_name, locals())

    def post(self, request):
        user_pk = request.POST.get("user_id")
        user = get_object_or_404(CustomUser, pk=user_pk)
        form = UserSetPasswordForm(data=request.POST, user=user)

        if form.is_valid():
            form.save()
            request.session.pop("forgot_password_user_pk")

        else:
            return render(request, self.template_name, locals())

        user_email = user.email
        user_name = user.get_full_name()
        
        message = f"""
        Hello {user_name},\n
        Your Django Starter Project password for the account with the email {user_email} has changed. \n
        If you did not reset your password or you did not request this change, please get in touch with support as soon as possible.\n
        Sincerely,\n
        Django Starter Project Support
        """
        send_general_email.delay(user_email, "Your Django Starter Project password has changed", message)

        return render(
            request,
            "accounts/confirmation.html",
            {"render_kind": "password_updated", "hide_signup": True},
        )



# Password Change (User Already Logged In)
class VerifyCurrentPasswordView(View):
    template_name = "accounts/verify-current-password.html"

    def get(self, request):
        form = VerifyCurrentPasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = VerifyCurrentPasswordForm(request.POST, user=request.user)
        user = request.user

        if form.is_valid():

            # Create and send the email with the change password link
            existing_mail_links = MailLinkModel.objects.filter(
                user=user, link_type="change_password", is_delete=False
            )

            for existing_mail_link in existing_mail_links:
                existing_mail_link.is_delete = True
                existing_mail_link.save()

            key = uuid.uuid4().hex
            link = f"{settings.BASE_URL}change-password?key={key}"

            MailLinkModel.objects.create(
                user=user, key=key, link_type="change_password"
            )

            message = f"""
            Hello {request.user.get_full_name()},\n
            We received a request to change the password for the account with the email {request.user.email}\n
            Use the link below to change your password:\n
            {link}\n
            If you don't want to change your password or you did not request this change, you can ignore this email.\n
            Sincerely,\n
            Django Starter Project Support
            """
            send_general_email.delay(request.user.email, "Confirm your password change", message)

            context ={
                "email": request.user.email,
                "render_kind": "change_password",
                "hide_signup": True,
            }
            
            return render(request, "accounts/confirmation.html", context)
        
        messages.error(request, 'The current password is incorrect. Please try again.')
        return render(request, self.template_name, {'form': form})


class ResendPasswordChangeVerificaitonEmail(View):

    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')

        
        user = request.user
        if user:
            # Create and send the email with the change password link
            existing_mail_links = MailLinkModel.objects.filter(
                user=user, link_type="change_password", is_delete=False
            )

            for existing_mail_link in existing_mail_links:
                existing_mail_link.is_delete = True
                existing_mail_link.save()

            key = uuid.uuid4().hex
            link = f"{settings.BASE_URL}change-password?key={key}"

            MailLinkModel.objects.create(
                user=user, key=key, link_type="change_password"
            )

            message = f"""
            Hello {request.user.get_full_name()},\n
            We received a request to change the password for the account with the email {request.user.email}\n
            Use the link below to change your password:\n
            {link}\n
            If you don't want to change your password or you did not request this change, you can ignore this email.\n
            Sincerely,\n
            Django Starter Project Support
            """
            send_general_email.delay(request.user.email, "Confirm your password change", message)

            context ={
                "email": request.user.email,
                "render_kind": "change_password",
                "hide_signup": True,
            }
            
            return render(request, "accounts/confirmation.html", context)
        
        else:
            context = {
                "message_title": "Password Reset Request Failed",
                "message_body": "No active session found. Please log in to proceed with the password reset request.",
                "message_type": "error",
            }
            return render(request, "accounts/custom-message.html", context)


class ChangePasswordView(View):
    template_name = "accounts/change-password-form.html"

    def get(self, request):
        key = request.GET.get("key")
        link_obj = get_object_or_404(MailLinkModel, key=key, link_type="change_password")
        
        if link_obj.is_delete:
            return render(
                        request,
                        "accounts/confirmation.html",
                        {"render_kind": "invalid_key", "hide_signup": True},
                    )

        form = UserSetPasswordForm(user=link_obj.user)

        link_obj.is_delete = True
        link_obj.save()

        return render(request, self.template_name, {'form': form, 'link_obj': link_obj})

    def post(self, request):
        key = request.GET.get("key")
        link_obj = get_object_or_404(MailLinkModel, key=key, link_type="change_password")
        form = UserSetPasswordForm(data=request.POST, user=link_obj.user)
        if form.is_valid():
            form.save()

            # Authenticate and log in user with the new password
            auth_user = authenticate(username=link_obj.user.username, password=request.POST['new_password1'])
            if auth_user:
                login(request, auth_user)
                return redirect('home')

            else:
                return redirect('login')

        return render(request, self.template_name, {'form': form})

class VerifyEmailChangeView(View):
    template_name = "accounts/verify-current-password.html"  # Reuse the existing template

    def get(self, request):
        form = VerifyCurrentPasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = VerifyCurrentPasswordForm(request.POST, user=request.user)
        if form.is_valid():
            # If password verification is successful, redirect to email change form
            request.session['password_verified'] = datetime.datetime.now().timestamp()
            return redirect('email_change_form')
        return render(request, self.template_name, {'form': form})

class EmailChangeFormView(View):
    template_name = "accounts/email-change-form.html"
    SESSION_TIMEOUT = 600 # 10 minutes

    def get(self, request):
        verification_time = request.session.get('password_verified')
        if not verification_time or (datetime.datetime.now().timestamp() - verification_time > self.SESSION_TIMEOUT):
            return redirect('verify_curr_password_for_email_update')
        
        form = EmailChangeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        verification_time = request.session.get('password_verified')
        if not verification_time or (datetime.datetime.now().timestamp() - verification_time > self.SESSION_TIMEOUT):
            return redirect('verify_curr_password_for_email_update')
        

        form = EmailChangeForm(request.POST)
        user = request.user

        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            
            key = uuid.uuid4().hex
            link = f"{settings.BASE_URL}change-email?key={key}"
            MailLinkModel.objects.create(
                user=request.user, link_type="email_change", key=key, new_email=new_email
            )

            message = f"""
            Hello {request.user.get_full_name()},\n
            We received a request to change the email address associated with your account to {new_email}.
            Please use the link below to confirm this change:\n
            {link}\n
            If you did not request this change, no action is needed, and you can disregard this email.
            Sincerely,\n
            Django Starter Project Support
            """
            send_general_email.delay(new_email, "Confirm your email address change", message)

            # Clear the session variable after initiating the change
            request.session.pop('password_verified', None)

            context = {
                "email": new_email,
                "render_kind": "email_change",
                "hide_signup": True,
            }

            return render(request, "accounts/confirmation.html", context)
            
        return render(request, self.template_name, {'form': form})


class ResendEmailChangeVerificaitonEmail(View):
    def post(self, request):
        data = json.loads(request.body)
        new_email = data.get('email')
        
        user = request.user

        if user:
            existing_mail_links = MailLinkModel.objects.filter(
                user=user, link_type="email_change", is_delete=False
            )
            for existing_mail_link in existing_mail_links:
                existing_mail_link.is_delete = True
                existing_mail_link.save()
            
            key = uuid.uuid4().hex
            link = f"{settings.BASE_URL}change-email?key={key}"
            MailLinkModel.objects.create(
                user=request.user, link_type="email_change", key=key, new_email=new_email
            )

            message = f"""
            Hello {request.user.get_full_name()},\n
            We received a request to change the email address associated with your account to {new_email}.
            Please use the link below to confirm this change:\n
            {link}\n
            If you did not request this change, no action is needed, and you can disregard this email.
            Sincerely,\n
            Django Starter Project Support
            """
            send_general_email.delay(new_email, "Confirm your email address change", message)

            # Clear the session variable after initiating the change
            request.session.pop('password_verified', None)

            context = {
                "email": new_email,
                "render_kind": "email_change",
                "hide_signup": True,
            }

            return render(request, "accounts/confirmation.html", context)

        else:
            context = {
                "message_title": "Email Change Request Failed",
                "message_body": "No active session found. Please log in to proceed with the email change request.",
                "message_type": "error",
            }
            return render(request, "accounts/custom-message.html", context)



class UpdateEmailView(View):

    def get(self, request):
        key = request.GET.get("key")
        link_obj = get_object_or_404(MailLinkModel, key=key, link_type="email_change")

        if link_obj and not link_obj.is_delete:
            user = link_obj.user
            user.email = link_obj.new_email
            user.save()

            link_obj.is_delete = True
            link_obj.save()

            login(request, user)  # Re-login the user to update the session

            message = f"""
            Hello {request.user.get_full_name()},\n
            Your account email has been updated to {user.email}.
            If you did not request this change, please get in touch with us as soon as possible.
            Sincerely,\n
            Django Starter Project Support
            """
            send_general_email.delay(user.email, "Your email has been changed", message)

            context = {
                'message_title': 'Email Update Successful',
                'message_body': 'Your email has been successfully updated. You can go back to home page.'
            }
            return render(request, 'accounts/custom-message.html', context)

        context = {
            'message_title': 'Email Update Failed',
            'message_body': 'The link used is invalid or expired. Please try the email update process again.'
        }
        return render(request, 'accounts/custom-message.html', context)



@require_http_methods(["GET"])
@login_required(login_url="login")
def account_logout(request):
    logout(request)
    return redirect("login")


@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            # Handle the case where name is empty or not valid
            context = {
                'error': 'Name cannot be empty.',
                'user': request.user
            }
            return render(request, "accounts/profile.html", context)
        # Update the user's name
        request.user.first_name = name
        request.user.save()

        # Redirect to profile page with a success message
        return redirect('profile')

    context = {
        'user': request.user
    }

    return render(request, "accounts/profile.html", context)


@require_http_methods(["GET"])
@login_required(login_url="login")
def profile_billing(request):

    context = {
        'user': request.user
    }

    return render(request, "accounts/profile-billing.html", context)


@require_http_methods(["GET"])
@login_required(login_url="login")
def profile_settings(request):

    context = {
        'user': request.user
    }

    return render(request, "accounts/profile-settings.html", context)


@require_http_methods(["POST"])
@login_required(login_url="login")
def ajax_update_profile_photo(request):
    
    user = request.user

    # TODO check the required params here
    data = json.loads(request.body)
    file_to_save = None
    if "file_to_save" in data:
        file_to_save = data["file_to_save"]
    if file_to_save == None:
        return JsonResponse(
            {"error": "Missing the 'file_to_save' parameter."}, status=400
        )

    original_name = file_to_save["file_original_name"]
    file_type = file_to_save["file_type"]
    file_extension = file_to_save["file_extension"]
    file_size = file_to_save["file_size"]
    file_size_mb = file_to_save["file_size_mb"]
    file_name = "private/uploads/" + randomlongstr() + "." + file_extension
    url = file_to_save["url"]
    S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
    root_url = "https://%s.s3.amazonaws.com/private/" % S3_BUCKET
    save_url = url.replace(root_url, "")

    # Create a new user file
    media_file = File()
    media_file.file = save_url
    media_file.display_id = randomstr()
    media_file.file_name = file_name
    media_file.original_name = original_name
    media_file.display_name = original_name
    media_file.file_type = file_type
    media_file.file_size = file_size
    media_file.file_size_mb = file_size_mb
    media_file.file_display_type = "image"
    splited_name = file_name.split(".")
    media_file.file_extension = "." + splited_name[-1]
    media_file.user = request.user
    media_file.save()

    user.profile_photo = media_file
    user.save()

    # Background processing for thumbnails if the file is an image
    process_thumbnails.delay(media_file.id)

    response_object = {
        "message": "Profile photo saved successfully",
        "url": media_file.file.url,
        "file_to_save": file_to_save,
    }

    return JsonResponse(response_object, status=200)


@require_http_methods(["POST"])
@login_required(login_url="login")
def ajax_remove_profile_photo(request):

    user = request.user

    # TODO check the required params here
    user.profile_photo = None
    user.save()

    response_object = {
        "message": "Profile photo removed",
    }

    return JsonResponse(response_object, status=200)

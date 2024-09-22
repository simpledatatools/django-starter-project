from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm,
    UserChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *
from accounts.models import *


# ================================================================================
# app FORMS
# ================================================================================


class SignUpForm(UserCreationForm):
    error_messages = {
        "password_mismatch": _(
            "The password and confirm password fields didn’t match."
        ),
    }

    first_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
                "placeholder": "First Name",
                }
        ),
        label="",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
                "placeholder": "Email",
                }
        ),
        label="",
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Password",
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
            },
        ),
        label="",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Confirm password",
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
            }
        ),
        label="",
    )

    class Meta:
        model = CustomUser
        fields = ("first_name", "email", "password1", "password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email").lower().strip()
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(
                "Email already exists, please use unique email address"
            )

        cleaned_data["email"] = email
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = self.cleaned_data.get("email").lower().strip()
        # user.is_active = True
        if commit:
            user.save()
        return user


class UpdatePasswordForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs[
            "class"
        ] = "form-control form-control-solid"
        self.fields["new_password1"].widget.attrs[
            "class"
        ] = "form-control form-control-solid"
        self.fields["new_password2"].widget.attrs[
            "class"
        ] = "form-control form-control-solid"


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Your email",
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = ["email"]

    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)


class UpdateProfileForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control form-control-solid"}),
    )
    last_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control form-control-solid"}),
    )
    password = None

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
                "placeholder": "Email",
                "required": "required",
            }),
    )
    password = forms.CharField(
        label="",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
                "placeholder": "Password",
                "required": "required",
            }),
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        email = email.lower().strip()
        cleaned_data["email"] = email

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError("Email does not exist! Please create an account before logging in.")

        if not user.check_password(password):
            raise ValidationError("Invalid Password")


        return self.cleaned_data


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "New password",
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
            }
        ),
        strip=False,
    )

    new_password2 = forms.CharField(
        label="",
        required=True,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Confirm new password",
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
            }
        ),
    )

class VerifyCurrentPasswordForm(forms.Form):
    curr_password = forms.CharField(
        label="",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter current password",
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(VerifyCurrentPasswordForm, self).__init__(*args, **kwargs)

    def clean_curr_password(self):
        curr_password = self.cleaned_data.get('curr_password')
        if not authenticate(username=self.user.username, password=curr_password):
            raise forms.ValidationError("The current password is incorrect.")
        return curr_password
    

class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(
        label="New Email",
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter new email",
            "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
        })
    )

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if CustomUser.objects.filter(email=new_email).exists():
            raise ValidationError("This email is already in use. Please choose a different one.")
        return new_email


# class ResendAccountVerificationEmail(forms.Form):
#     account_email = forms.EmailField(
#         label="Email",
#         required=True,
#         widget=forms.EmailInput(attrs={
#             "placeholder": "Enter your email",
#             "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#38B0CC] focus:border-transparent",
#         })
#     )

#     def clean_new_email(self):
#         new_email = self.cleaned_data.get('new_email')
#         if CustomUser.objects.filter(email=new_email).exists():
#             raise ValidationError("This email is already in use. Please choose a different one.")
#         return new_email

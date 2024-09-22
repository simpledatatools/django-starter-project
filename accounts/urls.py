from django.urls import path
from accounts.views import accounts as accounts

urlpatterns = [
    # Accounts
    path("login/", accounts.LoginView.as_view(), name="login"),
    path("signup/", accounts.UserRegistrationView.as_view(), name="sign_up"),
    path(
        "create-account/", accounts.VerifyUserLinkView.as_view(), name="create_account"
    ),
    path(
        "resend-verification-email/", 
        accounts.ResendAccountVerificationEmail.as_view(), 
        name="resend_verification_email"),
    path(
        "reset-password/", accounts.ResetPasswordView.as_view(), name="reset_password"
    ),
    path(
        "resend-password-reset-email/", 
        accounts.ResendPasswordResetVerificaitonEmail.as_view(), 
        name="resend_password_reset_email"
    ),
    path(
        "forgot-password/",
        accounts.VerifyUserLinkView.as_view(),
        name="forgot_password",
    ),
    path(
        "create-new-password/",
        accounts.CreateNewPasswordView.as_view(),
        name="create_new_password",
    ),
    path(
        "verify-current-password/",
        accounts.VerifyCurrentPasswordView.as_view(),
        name="verify_curr_password",
    ),
    path(
        "resend-password-change-email/", 
        accounts.ResendPasswordChangeVerificaitonEmail.as_view(), 
        name="resend_password_change_email"
    ),
    path(
        "change-password/",
        accounts.ChangePasswordView.as_view(),
        name="change_password",
    ),
    path(
        "verify-current-password-for-email",
        accounts.VerifyEmailChangeView.as_view(),
        name="verify_curr_password_for_email_update"
    ),
    path(
        "change-email-form/",
        accounts.EmailChangeFormView.as_view(),
        name="email_change_form",
    ),
    path(
        "resend-email-change-email/", 
        accounts.ResendEmailChangeVerificaitonEmail.as_view(), 
        name="resend_email_change_email"
    ),
    path(
        "change-email/",
        accounts.UpdateEmailView.as_view(),
        name="change_email",
    ),
    path("logout/", accounts.account_logout, name="logout"),
    path("profile/", accounts.profile, name="profile"),
    path("profile/settings/", accounts.profile_settings, name="profile_settings"),
    path("profile/billing/", accounts.profile_billing, name="profile_billing"),
    

    # path(
    #     "ajax/profile/update/", accounts.ajax_update_profile, name="ajax_update_profile"
    # ),
    path(
        "ajax/profile/photo/update/",
        accounts.ajax_update_profile_photo,
        name="ajax_update_profile_photo",
    ),
    path(
        "ajax/profile/photo/remove/",
        accounts.ajax_remove_profile_photo,
        name="ajax_remove_profile_photo",
    ),
]

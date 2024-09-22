from django.urls import path
from api.views import user_views as views


urlpatterns = [
    # Login
    path("login/", views.MyTokenObtainPairView.as_view(), name="api_token_obtain_pair"),
    # Logout
    path("logout/", views.LogoutView.as_view(), name="api_logout"),
    # Token Refresh
    path(
        "token-refresh/", views.CustomTokenRefreshView.as_view(), name="api_token_refresh"
    ),
    # Sign up
    path("signup/", views.registerUser, name="api_register"),
    path("verify-account/", views.verifyAccount, name="api_verify_account"),
    path(
        "verify-account-resend/",
        views.verifyAccountResend,
        name="api_verify_account_resend",
    ),
    # login for web
    path("web-login/", views.MyWebTokenObtainPairView.as_view(), name="web_api_token_obtain_pair"),
    # Sign up for web
    path("web-signup/", views.registerWebUser, name="api_web_register"),
    path(
        "web-verify-account/<str:key>/",
        views.verifyWebAccount,
        name="api_web_verify_account",
    ),
    path(
        "web-verify-account-resend/",
        views.verifyWebAccountResend,
        name="api_web_verify_account_resend",
    ),
    # Resetting password
    path(
        "password-reset-request/",
        views.passwordResetRequest,
        name="api_password_reset_request",
    ),
    path(
        "password-reset-request-resend/",
        views.passwordResetRequestResend,
        name="api_password_reset_request_resend",
    ),
    path(
        "verify-password-reset/",
        views.verifyPasswordReset,
        name="api_verify_password_reset",
    ),
    path("password-reset/", views.passwordReset, name="api_password_reset"),
    # Resetting password using email
    path(
        "web-password-reset-request/",
        views.webPasswordResetRequest,
        name="api_web_password_reset_request",
    ),
    path(
        "web-verify-password-reset/<str:key>/",
        views.webVerifyPasswordReset,
        name="api_web_verify_password_reset",
    ),
    path("web-password-reset/", views.webPasswordReset, name="api_web_password_reset"),
    # Update profile
    path("profile/", views.getUserProfile, name="api_user_profile"),
    path("profile/update/", views.updateUserProfile, name="api_update_user_profile"),
    path(
        "profile/update/photo/",
        views.updateUserProfilePhoto,
        name="api_update_user_profile_photo",
    ),
    # Change password
    path(
        "password-change-request/", 
        views.passwordChangeRequest,
        name="api_password_change_request"),
    path("password-change-request-resend/", 
         views.passwordChangeRequestResend, 
         name="api_password_change_request_resend"),
    path("verify-password-change/", 
         views.verifyPasswordChange, 
         name="api_verify_password_change"),
    path("password-change/", 
         views.passwordChange, 
         name="api_password_change"),

    # Web Change password
    path("web-password-change-request/", 
         views.webPasswordChangeRequest, 
         name="api_password_change_request"),
    path("web-verify-password-change/<str:key>", 
         views.webVerifyPasswordChange, 
         name="api_verify_password_change"),
    path("web-password-change/", 
         views.webPasswordChange, 
         name="api_password_change"),

    # Change email
    path(
        "email-change-request/",
        views.emailChangeRequest,
        name="api_email_change_request",
    ),
    path(
        "email-change-to-request/",
        views.emailChangeToRequest,
        name="api_email_change_to_request",
    ),
    path(
        "email-change-to-request-resend/",
        views.emailChangeToRequestResend,
        name="api_email_change_to_request_resend",
    ),
    path(
        "verify-email-change/", 
        views.verifyEmailChange, 
        name="api_verify_email_change"
    ),

    # Web Email Change
    path(
        "web-email-change-request/",
        views.webEmailChangeRequest,
        name="api_web_email_change_request",
    ),
    path(
        "web-email-change-to-request/",
        views.webEmailChangeToRequest,
        name="api_web_email_change_to_request",
    ),
    path(
        "web-verify-email-change/<str:key>",
        views.webVerifyEmailChange,
        name="api_web_verify_email_change"
    ),
]

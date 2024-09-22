import datetime
from django.shortcuts import render
from django.contrib.auth import authenticate
import jwt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import CustomUser
from api.serializers.user_serializers import UserSerializer, UserSerializerWithToken

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from django.contrib.auth.hashers import make_password
from rest_framework import status

from accounts.models import *
from messaging.tasks import *
from core.utils import *
from files.models import *
from files.tasks import *

from drf_spectacular.utils import extend_schema, extend_schema_view

from django.conf import settings
import logging

logger = logging.getLogger("Django Starter Project")

# ---------------------------------------------------------------------------------------------------
# Logging in
# ---------------------------------------------------------------------------------------------------


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            # Consider adding a mechanism to limit automatic verification code resends
            self.handle_verification_process()

            return {"success": False, "message": "User is not active"}

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return {"success": True, "user": data}

    def handle_verification_process(self):
        user_email = self.user.email
        existing_verify_codes = VerifyCode.objects.filter(
            user=self.user, code_type="register", status="pending"
        )
        existing_verify_codes.update(
            status="used"
        )  # Updating records in a single query

        code = randomverifycode()
        VerifyCode.objects.create(user=self.user, code=code, code_type="register")
        subject = "Your new verification code is " + str(code)
        message = "Thanks so much for signing up. Your new verification code is " + str(
            code
        )
        if settings.LIVE == "True":
            send_general_email.delay(user_email, subject, message)
        else:
            logger.info(message)


@extend_schema_view(
    post=extend_schema(exclude=True)
)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyWebTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            # Consider adding a mechanism to limit automatic verification code resends
            self.handle_verification_process()

            return {"success": False, "message": "User is not active"}

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return {"success": True, "user": data}

    def handle_verification_process(self):
        user_email = self.user.email
        # existing_verify_codes = VerifyCode.objects.filter(
        #     user=self.user, code_type="register", status="pending"
        # )
        # existing_verify_codes.update(
        #     status="used"
        # )  # Updating records in a single query

        # code = randomverifycode()
        # VerifyCode.objects.create(user=self.user, code=code, code_type="register")
        # subject = "Your new verification code is " + str(code)
        # message = "Thanks so much for signing up. Your new verification code is " + str(
        #     code
        # )
        existing_mail_links = MailLinkModel.objects.filter(
            user=self.user, link_type="register", is_delete=False
        )

        for existing_mail_link in existing_mail_links:
            existing_mail_link.is_delete = True
            existing_mail_link.save()
        
        new_verification_key = uuid.uuid4().hex
        new_verification_link = f"{settings.FRONTEND_URL}/verify-account/{new_verification_key}"

        MailLinkModel.objects.create(
            user=self.user, key=new_verification_key, link_type="register"
        )

        # Send new verification email
        subject = "Verify Your Account"
        message = (
            f"Please verify your account by clicking this link: {new_verification_link}"
        )
        if settings.LIVE == "True":
            send_general_email.delay(user_email, subject, message)
        else:
            logger.info(message)

@extend_schema_view(
    post=extend_schema(exclude=True)
)
class MyWebTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyWebTokenObtainPairSerializer

# ---------------------------------------------------------------------------------------------------
# Logging out
# ---------------------------------------------------------------------------------------------------

@extend_schema_view(
    post=extend_schema(exclude=True)
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logger.info(request.data)
            refresh_token = request.data["refresh_token"]
            if not refresh_token:
                return Response(
                    {"message": "No refresh token provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"message": str(e)}
            )


# ---------------------------------------------------------------------------------------------------
# Token Refresh endpoint
# ---------------------------------------------------------------------------------------------------

@extend_schema_view(
    post=extend_schema(exclude=True)
)
class CustomTokenRefreshView(TokenRefreshView):
    # customization in the future can go here
    pass


# ---------------------------------------------------------------------------------------------------
# Registration and sign up
# ---------------------------------------------------------------------------------------------------

@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])

def registerUser(request):
    data = request.data

    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if not all([email, name, password]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = data["email"].strip().lower()
    existing_user = CustomUser.objects.filter(email=email)
    if existing_user:
        message = "A user with that email already exists"
        response = {"success": False, "message": message}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    else:
        try:
            user = CustomUser.objects.create(
                first_name=data["name"],
                username=data["email"].strip().lower(),
                email=data["email"].strip().lower(),
                password=make_password(data["password"]),
            )

            # Create the user extras
            user_extras = UserExtras()
            user_extras.display_name = user.first_name
            user_extras.save()
            user.user_extras = user_extras
            user.save()

            user_email = user.email
            user_name = user.get_full_name()

            code = randomverifycode()

            verify_code = VerifyCode()
            verify_code.user = user
            verify_code.code = code
            verify_code.code_type = "register"
            verify_code.save()

            to = user_email
            subject = "Your verification code is " + str(code)
            message = "Thanks so much for signing up. Your verification code is " + str(
                code
            )
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            # Send email alert to app traffic
            to = "hello@djangostarterproject.com"
            subject = "[Django Starter Project] New Sign Up"
            message = "Hey - someone signed up"
            if user:
                message = message + " | User: " + user.email
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {"success": True, "message": "Sign up successful"}
            logger.info(response)
            return Response(response)

        except Exception as e:
            logger.info(e)
            message = "There was a problem with the sign up"
            response = {"success": False, "message": message}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------------------------------
# Verifying an account (initial registration)
# ---------------------------------------------------------------------------------------------------


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def verifyAccount(request):

    data = request.data

    email = data.get("email")
    code = data.get("code")

    if not all([email, code]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = data["email"].strip().lower()
    code = data["code"].strip()
    user = CustomUser.objects.filter(email=email).first()

    # Check the verify table
    verify_code = VerifyCode.objects.filter(
        user=user, code=code, code_type="register", status="pending"
    ).first()

    if verify_code:
        # Set the verify record to expired
        verify_code.status = "used"
        verify_code.save()
        # Get the user
        user = verify_code.user
        user.is_verified = True  # Set their account to active
        user.save()
        # Return the token
        serializer = UserSerializerWithToken(user, many=False)

        response = {"success": True, "user": serializer.data}
        logger.info(response)
        return Response(response)

    else:
        used_verify_code = VerifyCode.objects.filter(
            user__email=email, code=code, code_type="register", status="used"
        ).first()
        message = ""
        if used_verify_code:
            message = "Code has already been used"
        else:
            message = "Code is invalid"
        response = {"success": False, "message": message}
        logger.info(response)
        return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def verifyAccountResend(request):

    data = request.data

    email = data.get("email")

    if not all([email]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = data["email"].strip().lower()
    user = CustomUser.objects.filter(email=email, is_verified=False).first()

    if user:

        user_email = user.email
        user_name = user.get_full_name()

        # Remove any previous records
        existing_verify_codes = VerifyCode.objects.filter(
            user=user, code_type="register", status="pending"
        )
        for existing_verify_code in existing_verify_codes:
            existing_verify_code.status = "used"
            existing_verify_code.save()

        code = randomverifycode()

        verify_code = VerifyCode()
        verify_code.user = user
        verify_code.code = code
        verify_code.code_type = "register"
        verify_code.save()

        to = user_email
        subject = "Your new verification code is " + str(code)
        message = "Thanks so much for signing up. Your new verification code is " + str(
            code
        )
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

    response = {
        "success": True,
        "message": "Account verification code sent if the user exists and is not verified",
    }
    logger.info(response)
    return Response(response)


# ---------------------------------------------------------------------------------------------------
# Registration and sign up for web app
# ---------------------------------------------------------------------------------------------------


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def registerWebUser(request):
    data = request.data
    email = data.get("email", "").strip().lower()
    name = data.get("name")
    password = data.get("password")

    if not all([email, name, password]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if CustomUser.objects.filter(email=email).exists():
        return Response(
            {"success": False, "message": "A user with that email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = CustomUser.objects.create(
            username=email,
            email=email,
            password=make_password(password),
            first_name=name,
        )

        # Create the user extras
        user_extras = UserExtras()
        user_extras.display_name = user.first_name
        user_extras.save()
        user.user_extras = user_extras
        user.save()

        # Create a unique verification link
        verification_key = uuid.uuid4().hex
        verification_link = f"{settings.FRONTEND_URL}/verify-account/{verification_key}"

        MailLinkModel.objects.create(
            user=user, key=verification_key, link_type="register"
        )

        # Send verification email
        subject = "Verify Your Account"
        message = (
            f"Please verify your account by clicking this link: {verification_link}"
        )
        if settings.LIVE == "True":
            send_general_email.delay(user.email, subject, message)
        else:
            logger.info(message)

        # Send email alert to app traffic
        to = "hello@djangostarterproject.com"
        subject = "[Django Starter Project] New Sign Up"
        message = "Hey - someone signed up"
        if user:
            message = message + " | User: " + user.email
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

        return Response({"success": True, "message": "Sign up successful."})

    except Exception as e:
        logger.ingo(e)
        return Response(
            {"success": False, "message": "There was a problem with the sign up"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ---------------------------------------------------------------------------------------------------
# Verifying an account (initial registration for web)
# ---------------------------------------------------------------------------------------------------

@extend_schema(exclude=True)
@api_view(["GET"])
@permission_classes([AllowAny])
def verifyWebAccount(request, key):

    mail_link = MailLinkModel.objects.filter(
        key=key, link_type="register", is_delete=False, user__is_verified=False
    ).first()
    if mail_link:
        user = mail_link.user
        user.is_verified = True
        user.save()
        mail_link.is_delete = True
        mail_link.save()

        serializer = UserSerializerWithToken(user, many=False)
        response = {'success': True, 'user': serializer.data}

        logger.info(response)
        return Response(response)

    else:
        used_mail_link = MailLinkModel.objects.filter(
            key=key, link_type="register", is_delete=True, user__is_verified=True
        ).first()
        message = ""
        if used_mail_link:
            message = "Verification link has already been used!"
        else:
            message = "Invalid verification link!"

        response = {"success": False, "message": message}
        logger.info(response)
        return Response(response)


# ---------------------------------------------------------------------------------------------------
# Email Verification resend
# ---------------------------------------------------------------------------------------------------


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def verifyWebAccountResend(request):
    data = request.data
    email = data.get("email", "").strip().lower()

    if not email:
        return Response(
            {"success": False, "message": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = CustomUser.objects.filter(email=email, is_verified=False).first()
    if user:
        existing_mail_links = MailLinkModel.objects.filter(
            user=user, link_type="register", is_delete=False
        )
        for existing_mail_link in existing_mail_links:
            existing_mail_link.is_delete = True
            existing_mail_link.save()

        # Create a new verification link
        new_verification_key = uuid.uuid4().hex
        new_verification_link = f"{settings.FRONTEND_URL}/verify-account/{new_verification_key}"
        MailLinkModel.objects.create(
            user=user, key=new_verification_key, link_type="register"
        )

        # Send new verification email
        subject = "Verify Your Account"
        message = (
            f"Please verify your account by clicking this link: {new_verification_link}"
        )
        if settings.LIVE == "True":
            send_general_email.delay(email, subject, message)
        else:
            logger.info(message)

        response = {
            "success": True,
            "message": "A new verification email has been sent. Please check your inbox.",
        }
        return Response(response)
    else:
        response = {
            "success": False,
            "message": "No unverified user found with that email or user is already verified.",
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------------------------------
# Password reset (user not logged in)
# ---------------------------------------------------------------------------------------------------

@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def passwordResetRequest(request):
    data = request.data

    email = data.get("email")

    if not all([email]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = data["email"].strip().lower()

    user = CustomUser.objects.filter(email=email).first()
    if user:

        # Remove any previous records
        existing_verify_codes = VerifyCode.objects.filter(
            user=user, code_type="password_reset", status="pending"
        )
        for existing_verify_code in existing_verify_codes:
            existing_verify_code.status = "used"
            existing_verify_code.save()

        # Generate new code
        code = randomverifycode()
        verify_code = VerifyCode()
        verify_code.user = user
        verify_code.code = code
        verify_code.code_type = "password_reset"
        verify_code.save()

        to = user.email
        subject = "Your password reset code is " + str(code)
        message = "Your password reset code is " + str(code)
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)
        
    response = {
        "success": True,
        "message": "Password reset code sent if the email exists",
    }
    logger.info(response)
    return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def passwordResetRequestResend(request):
    data = request.data

    email = data.get("email")

    if not all([email]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = data["email"].strip().lower()

    user = CustomUser.objects.filter(email=email).first()
    if user:

        # Remove any previous records
        existing_verify_codes = VerifyCode.objects.filter(
            user=user, code_type="password_reset", status="pending"
        )
        for existing_verify_code in existing_verify_codes:
            existing_verify_code.status = "used"
            existing_verify_code.save()

        # Generate new code
        code = randomverifycode()
        verify_code = VerifyCode()
        verify_code.user = user
        verify_code.code = code
        verify_code.code_type = "password_reset"
        verify_code.save()

        to = user.email
        subject = "Your new password reset code is " + str(code)
        message = "Your new password reset code is " + str(code)
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

    response = {
        "success": True,
        "message": "Password reset code sent if the email exists",
    }
    logger.info(response)
    return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def verifyPasswordReset(request):

    data = request.data

    email = data.get("email")
    code = data.get("code")

    if not all([email, code]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = data["email"].strip().lower()
    code = data["code"].strip()
    user = CustomUser.objects.filter(email=email).first()

    # Check the verify table
    verify_code = VerifyCode.objects.filter(
        user=user, code=code, code_type="password_reset", status="pending"
    ).first()

    if verify_code:

        # Set the verify record to expired
        key = randomverylongstr()
        verify_code.status = "used"
        verify_code.key = key
        verify_code.save()

        # Get the user
        user = verify_code.user
        user.is_verified = True  # Set their account to active just in case this is someone who never verified
        user.save()

        # Return the token
        response = {"success": True, "key": key}
        logger.info(response)
        return Response(response)

    else:

        used_verify_code = VerifyCode.objects.filter(
            user__email=email, code=code, code_type="password_reset", status="used"
        ).first()
        message = ""
        if used_verify_code:
            message = "Code has already been used"
        else:
            message = "Code is invalid"
        response = {"success": False, "message": message}
        logger.info(response)
        return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def passwordReset(request):
    data = request.data

    email = data.get("email")
    code = data.get("code")
    key = data.get("key")
    password = data.get("password")

    if not all([email, code]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = data["email"].strip().lower()
    code = data["code"].strip()
    key = data["key"]
    password = data["password"]
    user = CustomUser.objects.filter(email=email).first()

    # Check the verify table
    verify_code = VerifyCode.objects.filter(
        user=user, code=code, key=key, code_type="password_reset"
    ).first()

    if verify_code:

        # Reset the password
        user.set_password(password)
        user.save()

        to = user.email
        subject = "Your password has been reset"
        message = "Your password has been reset. If this was not you, please reset your password, then reach out to support right away."
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

        # Return the token
        response = {"success": True, "message": "Password reset successfully"}
        logger.info(response)
        return Response(response)

    else:

        message = "Code is invalid"
        response = {"success": False, "message": message}
        logger.info(response)
        return Response(response)


# ---------------------------------------------------------------------------------------------------
# Password reset for web (user not logged in)
# This itself could also be used for a resend, so we won't have a resend view
# ---------------------------------------------------------------------------------------------------


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def webPasswordResetRequest(request):
    data = request.data
    email = data.get("email", "").strip().lower()

    if not email:
        return Response(
            {"success": False, "message": "Email is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = CustomUser.objects.filter(email=email).first()
    if user:
        existing_mail_links = MailLinkModel.objects.filter(
            user=user, link_type="reset_password", is_delete=False
        )
        for existing_mail_link in existing_mail_links:
            existing_mail_link.is_delete = True
            existing_mail_link.save()

        # Create a new unique link
        reset_key = uuid.uuid4().hex
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{reset_key}"
        
        MailLinkModel.objects.create(
            user=user, key=reset_key, link_type="reset_password"
        )

        # Send the password reset email
        subject = "Password Reset Request"
        message = (
            f"Please click the following link to reset your password: {reset_link}"
        )
        if settings.LIVE == "True":
            send_general_email.delay(user.email, subject, message)
        else:
            logger.info(message)

        return Response(
            {
                "success": True,
                "message": "Please check your email for the password reset link.",
            }
        )
    else:
        return Response(
            {"success": False, "message": "No user found with that email address"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(exclude=True)
@api_view(["GET"])
@permission_classes([AllowAny])
def webVerifyPasswordReset(request, key):

    mail_link = MailLinkModel.objects.filter(
        key=key, link_type="reset_password", is_delete=False
    ).first()
    if mail_link:
        mail_link.is_delete = True
        mail_link.save()

        user = mail_link.user
        user.is_verified = True  # Set their account to active just in case this is someone who never verified
        user.save()

        response = {
            "success": True,
            "message": "Please reset your password.",
            "key": key,
        }
        logger.info(response)
        return Response(response)

    else:
        used_mail_link = MailLinkModel.objects.filter(
            key=key, link_type="reset_password", is_delete=True
        ).first()
        message = ""
        if used_mail_link:
            message = "Reset link has already been used"
        else:
            message = "Invalid or expired reset link!"

        response = {"success": False, "message": message}
        logger.info(response)
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def webPasswordReset(request):
    data = request.data
    key = data.get("key")
    new_password = data.get("password")

    if not all([key, new_password]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    mail_link = MailLinkModel.objects.filter(
        key=key, link_type="reset_password"
    ).first()

    if mail_link:

        user = mail_link.user
        # Update the user's password
        user.set_password(new_password)
        user.save()

        subject = "Your password has been reset"
        message = "Your password has been reset. If this was not you, please reset your password, then reach out to support right away."
        if settings.LIVE == "True":
            send_general_email.delay(user.email, subject, message)
        else:
            logger.info(message)

        response = {
            "success": True,
            "message": "Your password has been reset successfully.",
        }
        logger.info(response)
        return Response(response)

    else:
        response = {"success": False, "message": "Invalid or expired reset link"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------------------------------


@extend_schema(exclude=True)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)

    data = request.data
    if "name" in data:
        user.first_name = data["name"]

    user.save()

    return Response(serializer.data)


@extend_schema(exclude=True)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateUserProfilePhoto(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)

    data = request.data
    if "file_data" in data:
        file_data = data["file_data"]
        media_file = File()
        media_file.file = file_data["path"]
        media_file.display_id = randomstr()
        media_file.file_name = file_data["file_name"]
        media_file.original_name = file_data["original_name"]
        media_file.display_name = file_data["original_name"]
        media_file.file_type = file_data["file_type"]
        media_file.file_size = None
        media_file.file_size_mb = None
        media_file.file_display_type = "image"
        media_file.file_extension = file_data["file_extension"]
        media_file.user = request.user
        media_file.save()

        user.profile_photo = media_file
        user.save()

    return Response({"success": True, "user": serializer.data})


@extend_schema(exclude=True)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


# ---------------------------------------------------------------------------------------------------
# Change password (user logged in)
# ---------------------------------------------------------------------------------------------------


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def passwordChangeRequest(request):

    data = request.data
    user = request.user

    current_password = data.get("current_password")

    if not all([current_password]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user is not None:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user is not None:
            # Password is correct

            # Remove any previous records
            existing_verify_codes = VerifyCode.objects.filter(
                user=user, code_type="password_change", status="pending"
            )
            for existing_verify_code in existing_verify_codes:
                existing_verify_code.status = "used"
                existing_verify_code.save()

            # Generate new code
            code = randomverifycode()
            verify_code = VerifyCode()
            verify_code.user = user
            verify_code.code = code
            verify_code.code_type = "password_change"

            verify_code.save()

            to = user.email
            subject = "Your password change verification code is " + str(code)
            message = "Your password change verification code is " + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {"success": True, "message": "Password change code was sent."}
        else:
            # Password is incorrect
            response = {
                "success": False,
                "message": "User is not authenticated or does not exist.",
            }
    else:
        # User is not logged in or does not exist
        response = {
            "success": False,
            "message": "User is not authenticated or does not exist.",
        }

    logger.info(response)
    return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def passwordChangeRequestResend(request):

    data = request.data
    user = request.user

    current_password = data.get("current_password")

    if not all([current_password]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user is not None:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user is not None:
            # Password is correct

            # Remove any previous records
            existing_verify_codes = VerifyCode.objects.filter(
                user=user, code_type="password_change", status="pending"
            )
            for existing_verify_code in existing_verify_codes:
                existing_verify_code.status = "used"
                existing_verify_code.save()

            # Generate new code
            code = randomverifycode()
            verify_code = VerifyCode()
            verify_code.user = user
            verify_code.code = code
            verify_code.code_type = "password_change"
            verify_code.save()

            to = user.email
            subject = "Your password change verification code is " + str(code)
            message = "Your password change verification code is " + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {"success": True, "message": "Password change code was sent."}
        else:
            # Password is incorrect
            response = {
                "success": False,
                "message": "User is not authenticated or does not exist.",
            }
    else:
        # User is not logged in or does not exist
        response = {
            "success": False,
            "message": "User is not authenticated or does not exist.",
        }

    logger.info(response)
    return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verifyPasswordChange(request):

    data = request.data

    code = data.get("code")

    if not all([code]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code = data["code"].strip()
    user = request.user

    # Check the verify table
    verify_code = VerifyCode.objects.filter(
        user=user, code=code, code_type="password_change", status="pending"
    ).first()

    if verify_code:

        # Set the verify record to expired
        key = randomverylongstr()
        verify_code.status = "used"
        verify_code.key = key
        verify_code.save()

        # Return the token
        response = {"success": True, "key": key}
        logger.info(response)
        return Response(response)

    else:

        used_verify_code = VerifyCode.objects.filter(
            user=user, code=code, code_type="password_change", status="used"
        ).first()
        message = ""
        if used_verify_code:
            message = "Code has already been used"
        else:
            message = "Code is invalid"
        response = {"success": False, "message": message}
        logger.info(response)
        return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def passwordChange(request):
    data = request.data

    code = data.get("code")
    key = data.get("key")
    password = data.get("password")

    if not all([code, key, password]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code = data["code"].strip()
    key = data["key"]
    password = data["password"]
    user = request.user

    # Check the verify table
    verify_code = VerifyCode.objects.filter(
        user=user, code=code, key=key, code_type="password_change"
    ).first()

    if verify_code:

        # Reset the password
        user.set_password(password)
        user.save()

        to = user.email
        subject = "Your password has been changed"
        message = "Your password has been changed. If this was not you, please reset your password, then reach out to support right away."
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

        # Return the token
        serializer = UserSerializerWithToken(user, many=False)
        user_serializer = serializer.data
        response = {
            "success": True,
            "message": "Password changed successfully",
            "user": user_serializer,
        }
        logger.info(response)
        return Response(response)

    else:

        message = "Code is invalid"
        response = {"success": False, "message": message}
        logger.info(response)
        return Response(response)


# ---------------------------------------------------------------------------------------------------
# Change password web(user logged in)
# ---------------------------------------------------------------------------------------------------

# The resend view has exactly the same logic as the intial request, 
# so we can use the initial request view for the resend purpose too.
@extend_schema(exclude=True)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webPasswordChangeRequest(request):
    data = request.data
    user = request.user
    current_password = data.get('current_password')

    if not current_password:
        return Response({'success': False, 'message': 'Current password is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if user:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user:
            # Password is correct, proceed with generating a password change link
            
            # Invalidate any previous links
            existing_mail_links = MailLinkModel.objects.filter(user=user, link_type='change_password', is_delete=False)
            for link in existing_mail_links:
                link.is_delete = True
                link.save()

            # Create a new unique link for password change
            change_key = uuid.uuid4().hex
            change_link = f"{settings.FRONTEND_URL}/change-password/{change_key}"
            
            # Save the new link in the database
            MailLinkModel.objects.create(
                user=user,
                key=change_key,
                link_type='change_password'
            )

            # Send the password change email
            subject = 'Password Change Request'
            message = f'Please click the following link to change your password: {change_link}'
            if settings.LIVE == "True":
                send_general_email.delay(user.email, subject, message)
            else:
                logger.info(message)

            return Response({'success': True, 'message': 'Please check your email to confirm your password change request.'})
        else:
            # Current password is incorrect
            return Response({'success': False, 'message': 'Incorrect password.'})
    else:
        # User not authenticated
        return Response({'success': False, 'message': 'Authentication required.'})


@extend_schema(exclude=True)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def webVerifyPasswordChange(request, key):

    if not key:
        return Response({'success': False, 'message': 'Missing or invalid key.'}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    mail_link = MailLinkModel.objects.filter(user=user, key=key, link_type='change_password', is_delete=False).first()

    logger.info(mail_link)

    if mail_link:
        mail_link.is_delete = True
        mail_link.save()

        response = {'success': True, 'message': 'Please proceed to change your password.', 'key': key}
        logger.info(response)
        return Response(response)

    else:
        # Determine if the link has been used or is invalid
        used_mail_link = MailLinkModel.objects.filter(user=user, key=key, link_type='change_password', is_delete=True).first()
        message = ""
        if used_mail_link:
            message = "Link has already been used"
        else:
            message = "Link is invalid"
        
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)
# ---------------------------------------------------------------------------------------------------
# Change password web(user logged in)
# ---------------------------------------------------------------------------------------------------

# The resend view has exactly the same logic as the intial request, 
# so we can use the initial request view for the resend purpose too.
@extend_schema(exclude=True)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webPasswordChangeRequest(request):
    data = request.data
    user = request.user
    current_password = data.get('current_password')

    if not current_password:
        return Response({'success': False, 'message': 'Current password is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if user:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user:
            # Password is correct, proceed with generating a password change link
            
            # Invalidate any previous links
            existing_mail_links = MailLinkModel.objects.filter(user=user, link_type='change_password', is_delete=False)
            for link in existing_mail_links:
                link.is_delete = True
                link.save()

            # Create a new unique link for password change
            change_key = uuid.uuid4().hex
            change_link = f"{settings.FRONTEND_URL}/change-password/{change_key}"
            
            # Save the new link in the database
            MailLinkModel.objects.create(
                user=user,
                key=change_key,
                link_type='change_password'
            )

            # Send the password change email
            subject = 'Password Change Request'
            message = f'Please click the following link to change your password: {change_link}'
            if settings.LIVE == "True":
                send_general_email.delay(user.email, subject, message)
            else:
                logger.info(message)

            return Response({'success': True, 'message': 'Please check your email to confirm your password change request.'})
        else:
            # Current password is incorrect
            return Response({'success': False, 'message': 'Incorrect password.'})
    else:
        # User not authenticated
        return Response({'success': False, 'message': 'Authentication required.'})


@extend_schema(exclude=True)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def webVerifyPasswordChange(request, key):

    if not key:
        return Response({'success': False, 'message': 'Missing or invalid key.'}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    mail_link = MailLinkModel.objects.filter(user=user, key=key, link_type='change_password', is_delete=False).first()

    logger.info(mail_link)

    if mail_link:
        mail_link.is_delete = True
        mail_link.save()

        response = {'success': True, 'message': 'Please proceed to change your password.', 'key': key}
        logger.info(response)
        return Response(response)

    else:
        # Determine if the link has been used or is invalid
        used_mail_link = MailLinkModel.objects.filter(user=user, key=key, link_type='change_password', is_delete=True).first()
        message = ""
        if used_mail_link:
            message = "Link has already been used"
        else:
            message = "Link is invalid"
        
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)


@extend_schema(exclude=True)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webPasswordChange(request):
    data = request.data

    key = data.get('key')
    new_password = data.get('password')

    if not all([key, new_password]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    mail_link = MailLinkModel.objects.filter(user=user, key=key, link_type='change_password').first()

    if mail_link:
        # Reset the password
        user.set_password(new_password)
        user.save()

        to = user.email
        subject = 'Your password has been changed'
        message = 'Your password has been changed. If this was not you, please contact support immediately.'
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

        # Return the new token to update the user's session without requiring a new login
        serializer = UserSerializerWithToken(user, many=False)
        user_serializer = serializer.data
        response = {'success': True, 'message': 'Password changed successfully', 'user': user_serializer}
        logger.info(response)
        return Response(response)

    else:
        message = "Invalid or expired link"
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)


@extend_schema(exclude=True)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webPasswordChange(request):
    data = request.data

    key = data.get('key')
    new_password = data.get('password')

    if not all([key, new_password]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    mail_link = MailLinkModel.objects.filter(user=user, key=key, link_type='change_password').first()

    if mail_link:
        # Reset the password
        user.set_password(new_password)
        user.save()

        to = user.email
        subject = 'Your password has been changed'
        message = 'Your password has been changed. If this was not you, please contact support immediately.'
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

        # Return the new token to update the user's session without requiring a new login
        serializer = UserSerializerWithToken(user, many=False)
        user_serializer = serializer.data
        response = {'success': True, 'message': 'Password changed successfully', 'user': user_serializer}
        logger.info(response)
        return Response(response)

    else:
        message = "Invalid or expired link"
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)

# ---------------------------------------------------------------------------------------------------
# Change email (user logged in)
# ---------------------------------------------------------------------------------------------------


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def emailChangeRequest(request):
    data = request.data
    user = request.user

    current_password = data.get("current_password")

    if not all([current_password]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user is not None:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user is not None:
            # Password is correct

            # Remove any previous records
            existing_verify_codes = VerifyCode.objects.filter(
                user=user, code_type="email_change", status="pending"
            )
            for existing_verify_code in existing_verify_codes:
                existing_verify_code.status = "used"
                existing_verify_code.save()

            # Generate new code
            key = randomverylongstr()
            verify_code = VerifyCode()
            verify_code.user = user
            verify_code.key = key  # Only set the key here on this one, not the code
            verify_code.code_type = "email_change"
            verify_code.save()

            response = {
                "success": True,
                "message": "Valid.",
                "email": user.email,
                "key": key,
            }

        else:
            # Password is incorrect
            response = {
                "success": False,
                "message": "User is not authenticated or does not exist.",
            }
    else:
        # User is not logged in or does not exist
        response = {
            "success": False,
            "message": "User is not authenticated or does not exist.",
        }

    logger.info(response)
    return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def emailChangeToRequest(request):
    data = request.data
    user = request.user

    key = data.get("key")
    new_email = data.get("new_email")

    if not all([key, new_email]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    key = data["key"]
    new_email = data["new_email"].strip().lower()

    # Check if that email is already registered
    existing_users = CustomUser.objects.filter(email=new_email).exclude(
        email=user.email
    )
    if existing_users:
        # Email is already taken / and account with that email already exists
        response = {"success": False, "message": "Email is already registered."}
    else:
        # Verify the key and get the existing verify code
        existing_verify_code = VerifyCode.objects.filter(
            user=user, key=key, code_type="email_change", status="pending"
        ).first()
        if existing_verify_code:

            code = randomverifycode()
            existing_verify_code.code = code
            existing_verify_code.email = new_email
            existing_verify_code.save()

            to = new_email
            subject = "Your email change verification code is " + str(code)
            message = "Your email change verification code is " + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {"success": True, "message": "Password change code was sent."}

        else:
            response = {"success": False, "message": "Invalid request."}

    logger.info(response)
    return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def emailChangeToRequestResend(request):

    data = request.data
    user = request.user

    key = data.get("key")
    new_email = data.get("new_email")

    if not all([key, new_email]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    key = data["key"]
    new_email = data["new_email"].strip().lower()

    # Check if that email is already registered
    existing_users = CustomUser.objects.filter(email=new_email).exclude(
        email=user.email
    )
    if existing_users:
        # Email is already taken / and account with that email already exists
        response = {"success": False, "message": "Email is already registered."}
    else:
        # Verify the key and get the existing verify code
        existing_verify_code = VerifyCode.objects.filter(
            user=user,
            key=key,
            email=new_email,
            code_type="email_change",
            status="pending",
        ).first()
        if existing_verify_code:

            code = randomverifycode()
            existing_verify_code.code = code
            existing_verify_code.save()

            to = new_email
            subject = "Your email change verification code is " + str(code)
            message = "Your email change verification code is " + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {"success": True, "message": "Password change code was sent."}

        else:
            response = {"success": False, "message": "Invalid request."}

    logger.info(response)
    return Response(response)


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verifyEmailChange(request):

    data = request.data

    code = data.get("code")
    key = data.get("key")
    new_email = data.get("new_email")

    if not all([key, new_email]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    code = data["code"].strip()
    key = data["key"]
    new_email = data["new_email"].strip().lower()

    user = request.user

    # Check the verify table
    verify_code = VerifyCode.objects.filter(
        user=user,
        code=code,
        key=key,
        email=new_email,
        code_type="email_change",
        status="pending",
    ).first()

    if verify_code:

        # Set the verify record to expired
        key = randomverylongstr()
        verify_code.status = "used"
        verify_code.key = key
        verify_code.save()

        # Get the user
        user.email = new_email
        user.username = new_email
        user.save()

        # Return the token
        serializer = UserSerializerWithToken(user, many=False)
        user_serializer = serializer.data
        response = {
            "success": True,
            "message": "Email changed successfully",
            "user": user_serializer,
        }
        logger.info(response)
        return Response(response)

    else:

        used_verify_code = VerifyCode.objects.filter(
            user=user,
            code=code,
            key=key,
            email=new_email,
            code_type="email_change",
            status="used",
        ).first()
        message = ""
        if used_verify_code:
            message = "Code has already been used"
        else:
            message = "Code is invalid"
        response = {"success": False, "message": message}
        logger.info(response)
        return Response(response)
    

# ---------------------------------------------------------------------------------------------------
# Change email in web(user logged in)
# ---------------------------------------------------------------------------------------------------
@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def webEmailChangeRequest(request):
    data = request.data
    user = request.user

    logger.info(user)

    current_password = data.get("current_password")

    if not all([current_password]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user is not None:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user is not None:
            # Password is correct
            
            # Generate a token
            payload = {
                'user_id': user.id,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10) # Token expires 10 minutes.
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            response = {
                "success": True,
                "message": "Valid.",
                "email": user.email,
                "token": token
            }

        else:
            # Password is incorrect
            response = {
                "success": False,
                "message": "User is not authenticated or does not exist.",
            }
    else:
        # User is not logged in or does not exist
        response = {
            "success": False,
            "message": "User is not authenticated or does not exist.",
        }

    logger.info(response)
    return Response(response)


# This here can also be used for emailChangeToRequestResend
@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def webEmailChangeToRequest(request):
    data = request.data
    user = request.user

    token = data.get("token")
    new_email = data.get("new_email").strip().lower()

    if not all([token, new_email]):
        return Response(
            {"success": False, "message": "Missing required parameters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload['user_id'] != user.id:
            return Response({"success": False, "message": "Invalid request."}, status=400)
        
        # Check if that email is already registered
        existing_users = CustomUser.objects.filter(email=new_email).exclude(
            email=user.email
        )

        if existing_users:
            # Email is already taken / and account with that email already exists
            response = {"success": False, "message": "Email is already registered."}
        else:
            # Invalidate any previous links
            existing_mail_links = MailLinkModel.objects.filter(user=user, link_type='email_change', is_delete=False)
            for link in existing_mail_links:
                link.is_delete = True
                link.save()

            # Generate new code
            change_key = uuid.uuid4().hex
            
            # Save the new link in the database
            MailLinkModel.objects.create(
                user=user,
                key=change_key,
                link_type='email_change',
                new_email=new_email
            )

            change_link = f"{settings.FRONTEND_URL}/change-email/{change_key}"

            to = new_email
            subject = 'Email Change Request'
            message = f'Please click the following link to change your email: {change_link}'

            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {
                "success": True,
                "message": "A confirmation link for your email change has been sent. Please check your inbox to proceed."
            }


            # else:
            #     response = {"success": False, "message": "Invalid request."}

        logger.info(response)
        return Response(response)
    
    except jwt.ExpiredSignatureError:
        return Response({"success": False, "message": "Token expired."}, status=401)
    except jwt.InvalidTokenError:
        return Response({"success": False, "message": "Invalid token."}, status=400)


@extend_schema(exclude=True)
@api_view(["GET"])
def webVerifyEmailChange(request, key):
    # Retrieve the mail link with the key and not deleted
    mail_link = MailLinkModel.objects.filter(key=key, link_type='email_change', is_delete=False).first()

    if not mail_link:

        used_mail_link = MailLinkModel.objects.filter(key=key, link_type='email_change', is_delete=True).first()

        message = ""
        if used_mail_link:
            message = "Verification link has already been used"
        else:
            message = "Invalid verification link"
        
        return Response({'success': False, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    user = mail_link.user
    if user:
        # Update the user's email
        user.email = mail_link.new_email
        user.username = mail_link.new_email
        user.save()

        # Mark the link as used
        mail_link.is_delete = True
        mail_link.save()

        serializer = UserSerializerWithToken(user, many=False)
        user_data = serializer.data
        response = {'success': True, 'message': 'Email changed successfully.', 'user': user_data}
        logger.info(response)
        return Response(response)
    else:
        response = {'success': False, 'message': 'User not found.'}
        logger(response)
        return Response(response, status=404)


import logging
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model
from django.conf import settings
from ninja.errors import HttpError
from ninja_extra import api_controller, route, exceptions
from ninja_jwt.tokens import RefreshToken, UntypedToken
from ninja_jwt.token_blacklist.models import BlacklistedToken
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.settings import api_settings
from ninja_jwt.exceptions import ValidationError
from users.schemas import (
    LoginOutSchema,
    LoginInputSchema,
    VerifyUserInput,
    ForgotPasswordInput,
    ResetPasswordInput
)
from utils.helpers import USER_VERIFY_ACCOUNT, USER_FORGOT_PASSWORD, verify_hashed_text
from utils.email import (
    send_successful_password_reset_email,
    send_successful_verification_email,
    send_password_reset_email
)


User = get_user_model()


@api_controller('auth', tags=['Auth'])
class AuthController(NinjaJWTDefaultController):

    @route.post('/login', response=LoginOutSchema, url_name="token_obtain_pair")
    def obtain_token(self, user_token: LoginInputSchema, response: HttpResponse):
        token_data = user_token.get_response_schema_init_kwargs()
        response.set_cookie(
            key="refresh_token",
            value=str(token_data["refresh"]),
            path='/',
            httponly=True,
            secure=True,
            samesite="None",
            max_age=api_settings.REFRESH_TOKEN_LIFETIME
        )
        response.set_cookie(
            key="access_token",
            value=str(token_data["access"]),
            path='/',
            httponly=True,
            secure=True,
            samesite="None",
            max_age=api_settings.ACCESS_TOKEN_LIFETIME
        )
        
        data = {
            "status": "success",
            "message": "User successfully logged in.",
            "user": token_data["user"]
        }

        return data
    

    @route.post('/refresh', url_name="token_refresh", response={204: None})
    def refresh_token(self, request: HttpRequest, response: HttpResponse):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            raise exceptions.ValidationError('refresh token is missing from cookie')
        
        refresh = RefreshToken(refresh_token)
        data = {}

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

            response.set_cookie(
                key="refresh_token",
                value=str(data["refresh"]),
                path='/',
                httponly=True,
                secure=True,
                samesite="None",
                max_age=api_settings.REFRESH_TOKEN_LIFETIME
            )

        response.set_cookie(
            key="access_token",
            value=str(data["access"]),
            path='/',
            httponly=True,
            secure=True,
            samesite="None",
            max_age=api_settings.ACCESS_TOKEN_LIFETIME
        )

        return 204, None
    

    @route.post('/verify', url_name='token_verify', response={204:None})
    def verify_token(self, request: HttpRequest):
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            raise exceptions.ValidationError('access token is missing from cookie')
        
        token = UntypedToken(str(access_token))

        if (
            api_settings.BLACKLIST_AFTER_ROTATION
            and "ninja_jwt.token_blacklist" in settings.INSTALLED_APPS
        ):
            jti = token.get(api_settings.JTI_CLAIM)
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                raise ValidationError("Token is blacklisted")
        
        return 204, None
    

    @route.post('logout', url_name='logout')
    def logout(self, response: HttpResponse):
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return self.create_response(
            message={
                'status': 'success',
                'message': 'User logged out successfully.'
            },
            status_code=200
        )


    @route.post('/verify-user', url_name='verify_user')
    def verify_user(self, payload: VerifyUserInput):
        user = self.get_object_or_exception(User, error_message="User does not exist.", pk=payload.uid)
        user_token = user.get_context_string(context=USER_VERIFY_ACCOUNT)

        # Verify token
        try:
            token_valid = verify_hashed_text(user_token, payload.token)
        except Exception as verify_exec:
            logging.exception(verify_exec)
            token_valid = False
        
        if not token_valid:
            raise HttpError(status_code=400, message='The link is either expired or not valid.')
        
        user.is_active = True
        user.is_verified = True
        user.set_password(payload.new_password)
        user.save()

        # Send successful verification email to user
        send_successful_verification_email(user)

        return self.create_response(
            message={
                'status': 'success',
                'message': 'User verified successfully.'
            },
            status_code=200
        )
    

    @route.post('/forgot-password', url_name='forgot_password')
    def forgot_password(self, payload: ForgotPasswordInput):
        user = self.get_object_or_exception(User, error_message="User with email does not exist.", email=payload.email)

        if not user.is_verified:
            raise HttpError(status_code=400, message='Your account is not verified. Please check your email inbox to verify your account, or reach admin.')
        if not user.is_active:
            raise HttpError(status_code=403, message='This account is deactivated. Reach out to Admin.')
        
        # Send password-reset email to user
        send_password_reset_email(user)

        return self.create_response(
            message={
                'status': 'success',
                'message': 'Email has been sent to your inbox.'
            },
            status_code=200
        )


    @route.post('reset-password', url_name='reset_password')
    def reset_password(self, payload: ResetPasswordInput):
        user = self.get_object_or_exception(User, error_message="User does not exist.", pk=payload.uid)
        # Verify user account is verified
        if not user.is_verified:
            raise HttpError(status_code=400, detail='Invalid request.')
        # Verify user account is active
        if not user.is_active:
            raise HttpError(status_code=400, detail='Invalid request.')
        
        user_token = user.get_context_string(context=USER_FORGOT_PASSWORD)
        
        # Verify token
        try:
            token_valid = verify_hashed_text(user_token, payload.token)
        except Exception as verify_exec:
            logging.exception(verify_exec)
            token_valid = False
        
        if not token_valid:
            raise HttpError(status_code=400, message='The link is either expired or not valid.')
        
        user.set_password(payload.new_password)
        user.save()

        # Send password-reset confirmation mail
        send_successful_password_reset_email(user)

        return self.create_response(
            message={
                'status': 'success',
                'message': 'Password reset successful.'
            },
            status_code=200
        )
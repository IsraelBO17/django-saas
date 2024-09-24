from typing import List
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from ninja import Schema, ModelSchema
import ninja_jwt.exceptions as exceptions
from ninja_jwt.schema import TokenObtainPairInputSchema
from pydantic import EmailStr, model_validator, field_validator
from utils.helpers import is_password_strong_enough


User = get_user_model()

class PermissionSchema(ModelSchema):
    class Meta:
        model = Permission
        fields = ['id','name']


class GroupSchema(Schema):
    permissions: List[PermissionSchema] = []
    class Meta:
        model = Group
        fields = ['id','name','permissions']


class UserInSchema(Schema):
    email: EmailStr

    @field_validator('email')
    def validate_email_uniqueness(cls, value, values):
        try:
            User.objects.get(email=value)
            raise exceptions.ValidationError('Email already exists')
        except User.DoesNotExist:
            return value


class UserOutSchema(ModelSchema):
    groups: List[GroupSchema] = []
    class Meta:
        model = User
        fields = ['id','email','is_staff','is_active','is_verified','date_joined']


class LoginOutSchema(Schema):
    status: str
    message: str
    user: UserOutSchema


class LoginInputSchema(TokenObtainPairInputSchema):
    def get_response_schema_init_kwargs(self) -> dict:
        token_data = super().get_response_schema_init_kwargs()
        token_data.update(user=UserOutSchema.from_orm(self._user))
        return token_data


class PasswordCheckMixin:
    @model_validator(mode='after')
    def check_passwords_match(self):
        pw1 = self.new_password
        if not is_password_strong_enough(pw1):
            raise exceptions.ValidationError('password is not strong enough. Please provide a strong password.')
        pw2 = self.re_new_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise exceptions.ValidationError('passwords do not match')
        return self


class VerifyUserInput(Schema, PasswordCheckMixin):
    token: str
    uid: str
    new_password: str
    re_new_password: str


class ForgotPasswordInput(Schema):
    email: EmailStr


class ResetPasswordInput(Schema, PasswordCheckMixin):
    token: str
    uid: str
    new_password: str
    re_new_password: str


class ChangePasswordInput(Schema, PasswordCheckMixin):
    current_password: str
    new_password: str
    re_new_password: str

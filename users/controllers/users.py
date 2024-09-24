import logging
from typing import List
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.utils import Error
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.exceptions import ValidationError
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.token_blacklist.models import OutstandingToken
from core.permission import IsSuperAdmin
from users.schemas import (
    UserInSchema,
    UserOutSchema,
    ChangePasswordInput
)
from utils.email import send_deactivation_email, send_verification_email


User = get_user_model()

@api_controller('users', tags=['User'], permissions=[IsSuperAdmin])
class UserController(ControllerBase):

    def _get_user_or_404(self, id: str):
        user = self.get_object_or_exception(User, error_message="User does not exist.", pk=id)
        return user

    def _handle_exception(self, exc):
        if isinstance(exc, Error):
            logging.exception(exc)
            error_details = {'type': type(exc).__name__, 'message': 'Unable to perform operation.'}
            raise ValidationError(error_details, 422)
        raise exc

    @route.post('/register')
    def register_user(self, payload: UserInSchema):
        try:
            email = payload.email
            user = User.objects.create_user(email)

            user_group = Group.objects.get(name='employee')
            user_group.user_set.add(user)
            message = {
                'status': 'success',
                'message': f'User with id "{user.id}" created successfully.',
                'data': UserOutSchema(**user.__dict__)
            }
        except Exception as exc:
            self._handle_exception(exc)

        # Send verification email to user
        send_verification_email(user)

        return self.create_response(message=message, status_code=200)
    
    @route.get('/', response=List[UserOutSchema])
    def get_all_users(self):
        users = User.objects.all()
        return users
    
    @route.get('/current-user', response=UserOutSchema, permissions=[IsAuthenticated])
    def get_authenticated_user(self):
        user = self.context.request.user
        return user
    
    @route.post('/change-password', permissions=[IsAuthenticated])
    def change_user_password(self, payload: ChangePasswordInput):
        user = self.context.request.user

        if not user.check_password(payload.current_password):
            raise ValidationError('Current password is incorrect.')
        
        user.set_password(payload.new_password)
        user.save()

        # Send change-password email to user
        
        return self.create_response(
            message={
                'status': 'success',
                'message': 'Password successfully changed.'
            },
            status_code=200
        )
    
    @route.get('/{id}', response=UserOutSchema)
    def get_user(self, id: str):
        user = self._get_user_or_404(id)
        return user
    
    @route.delete('/{id}')
    def delete_user(self, id: str):
        user = self._get_user_or_404(id)
        
        try:
            # Delete user from database
            user.delete()
        except Exception as exc:
            self._handle_exception(exc)

        return self.create_response(message={'message':'User successfully deleted.'}, status_code=200)
    
    @route.post('/deactivate/{id}')
    def deactivate_user(self, id: str):
        user = self._get_user_or_404(id)
        
        # Logs user out
        outstanding_token_objs = OutstandingToken.objects.filter(user_id=user.id)
        for token_obj in outstanding_token_objs:
            token = RefreshToken(token_obj.token)
            token.blacklist()

        # Deactivate user
        user.is_active = False
        user.save()

        # Send deactivation email to user
        send_deactivation_email(user)

        return self.create_response(
            message={
                'status': 'success',
                'message': 'User is successfully deactivated.'
            },
            status_code=200
        )
    
    @route.post('/activate/{id}')
    def reactivate_user(self, id: str):
        user = self._get_user_or_404(id)

        user.is_active = True
        user.save()

        # Send reactivation email to user

        return self.create_response(
            message={
                'status': 'success',
                'message': 'User has been successfully reactivated.'
            }
        )


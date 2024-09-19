from typing import List
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from ninja.errors import HttpError
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
from users.schemas import (
    UserInSchema,
    UserOutSchema,
    ChangePasswordInput
)
from users.permissions import IsSuperAdmin
from utils.email import (
    send_deactivation_email,
    send_verification_email
)


User = get_user_model()


class CustomJWTAuth(JWTAuth):
    def authenticate(self, request: HttpRequest, token: str):
        token = request.COOKIES.get('access_token')
        return self.jwt_authenticate(request, token)


@api_controller('users', auth=CustomJWTAuth(), tags=['User'], permissions=[IsSuperAdmin])
class UserController(ControllerBase):

    @route.post('/register', response=UserOutSchema)
    def register_user(self, payload: UserInSchema):
        email = payload.email
        user = User.objects.create_user(email)

        user_group = Group.objects.get(name='user')
        user_group.user_set.add(user)

        # Send verification email to user
        send_verification_email(user)

        return user
    
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
            raise HttpError(status_code=400, message='Current password is incorrect.')
        
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
        user = self.get_object_or_exception(User, error_message="User does not exist.", pk=id)
        return user
    
    @route.delete('/{id}')
    def delete_user(self, id: str):
        user = self.get_object_or_exception(User, error_message="User does not exist.", pk=id)

        # Logs user out
        user.delete()

        return self.create_response(message={'message':'User successfully deleted.'}, status_code=200)
    
    @route.post('/deactivate/{id}')
    def deactivate_user(self, id: str):
        user = self.get_object_or_exception(User, error_message="User does not exist.", pk=id)
        
        # Logs user out
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


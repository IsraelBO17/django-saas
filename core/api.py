from django.http import HttpRequest
from ninja_extra import NinjaExtraAPI
from ninja.errors import ValidationError, HttpError
from ninja_extra.exceptions import APIException
from ninja_jwt.authentication import JWTAuth
from users.controllers.auth import AuthController
from users.controllers.users import UserController
from organizations.controllers.job_title import JobTitleController
from organizations.controllers.salary_grade import SalaryGradeController
from organizations.controllers.department import DepartmentController
from organizations.controllers.employment_type import EmploymentTypeController
from organizations.controllers.job_level import JobLevelController


class CustomJWTAuth(JWTAuth):
    def authenticate(self, request: HttpRequest, token: str):
        token = request.COOKIES.get('access_token')
        return self.jwt_authenticate(request, token)

api = NinjaExtraAPI(auth=CustomJWTAuth())
api.register_controllers(AuthController)
api.register_controllers(UserController)
api.register_controllers(JobTitleController)
api.register_controllers(SalaryGradeController)
api.register_controllers(DepartmentController)
api.register_controllers(EmploymentTypeController)
api.register_controllers(JobLevelController)


@api.exception_handler(APIException)
def generic_api_exception_handler(request, exc: APIException):
    status = exc.default_code
    message = exc.detail

    return api.create_response(
        request,
        {
            "status": status,
            "detail": message
        },
        status=exc.status_code
    )

@api.exception_handler(ValidationError)
def ninja_validation_error_handler(request, exc: ValidationError):
    status = "validation error"
    errors = []

    for error in exc.errors:
        message = error['msg']
        errors.append({'field': error['loc'][2], 'message': message})
    
    return api.create_response(
        request,
        {
            "status": status,
            "errors": errors
        },
        status=400
    )

@api.exception_handler(HttpError)
def ninja_http_error_handler(request, exc: HttpError):
    status = "error"
    return api.create_response(
        request,
        {
            'status': status,
            'message': exc.message
        },
        status=exc.status_code
    )

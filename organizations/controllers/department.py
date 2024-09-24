import logging
from typing import List
from django.db.utils import Error
from ninja import PatchDict
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.exceptions import ValidationError
from core.permission import IsSuperAdmin
from organizations.models import Department
from organizations.schemas import DepartmentInputSchema, DepartmentResponse


@api_controller('departments', tags=['Department'], permissions=[IsSuperAdmin])
class DepartmentController(ControllerBase):

    def _get_department_or_404(self, id: str) -> Department:
        department = self.get_object_or_exception(Department, error_message="Department does not exist.", pk=id)
        return department

    def _handle_exception(self, exc):
        if isinstance(exc, Error):
            logging.exception(exc)
            error_details = {'type': type(exc).__name__, 'message': 'Unable to perform operation.'}
            raise ValidationError(error_details, 422)
        raise exc
    
    @route.post('/create')
    def create_department(self, payload: DepartmentInputSchema):
        try:
            department = Department.objects.create(**payload.model_dump())
            message = {
                'status': 'success',
                'message': f'Department with id "{department.id}" created successfully.',
                'data': DepartmentResponse(**department.__dict__)
            }
            return self.create_response(message=message, status_code=200)
        except Exception as exc:
            self._handle_exception(exc)
    
    @route.get('/', response=List[DepartmentResponse])
    def get_all_departments(self):
        departments = Department.objects.all()
        return departments
    
    @route.patch('update/{id}', response=DepartmentResponse)
    def update_department(self, id: str, payload: PatchDict[DepartmentInputSchema]):
        try:
            department = self._get_department_or_404(id)
            for attr, value in payload.items():
                setattr(department, attr, value)
            department.save()
            return department
        except Exception as exc:
            self._handle_exception(exc)
    
    @route.get('/{id}', response=DepartmentResponse)
    def get_department(self, id: str):
        department = self._get_department_or_404(id)
        return department
    
    @route.delete('/{id}')
    def delete_department(self, id: str):
        try:
            department = self._get_department_or_404(id)
            department.delete()
            return self.create_response(
                message={'message': 'Department successfully deleted.'},
                status_code=200
            )
        except Exception as exc:
            self._handle_exception(exc)


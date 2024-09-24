import logging
from typing import List
from django.db.utils import Error
from ninja import PatchDict
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.exceptions import ValidationError
from core.permission import IsSuperAdmin
from organizations.models import EmploymentType
from organizations.schemas import EmploymentTypeInputSchema, EmploymentTypeResponse


@api_controller('employment-types', tags=['Employment Type'], permissions=[IsSuperAdmin])
class EmploymentTypeController(ControllerBase):

    def _get_employment_type_or_404(self, id: str) -> EmploymentType:
        employment_type = self.get_object_or_exception(EmploymentType, error_message="Employment Type does not exist.", pk=id)
        return employment_type

    def _handle_exception(self, exc):
        if isinstance(exc, Error):
            logging.exception(exc)
            error_details = {'type': type(exc).__name__, 'message': 'Unable to perform operation.'}
            raise ValidationError(error_details, 422)
        raise exc
    
    @route.post('/create')
    def create_employment_type(self, payload: EmploymentTypeInputSchema):
        try:
            employment_type = EmploymentType.objects.create(**payload.model_dump())
            message = {
                'status': 'success',
                'message': f'Employment Type with id "{employment_type.id}" created successfully.',
                'data': EmploymentTypeResponse(**employment_type.__dict__)
            }
            return self.create_response(message=message, status_code=200)
        except Exception as exc:
            self._handle_exception(exc)
    
    @route.get('/', response=List[EmploymentTypeResponse])
    def get_all_employment_types(self):
        employment_types = EmploymentType.objects.all()
        return employment_types
    
    @route.patch('update/{id}', response=EmploymentTypeResponse)
    def update_employment_type(self, id: str, payload: PatchDict[EmploymentTypeInputSchema]):
        try:
            employment_type = self._get_employment_type_or_404(id)
            for attr, value in payload.items():
                setattr(employment_type, attr, value)
            employment_type.save()
            return employment_type
        except Exception as exc:
            self._handle_exception(exc)

    @route.get('/{id}', response=EmploymentTypeResponse)
    def get_employment_type(self, id: str):
        employment_type = self._get_employment_type_or_404(id)
        return employment_type
    
    @route.delete('/{id}')
    def delete_employment_type(self, id: str):
        try:
            employment_type = self._get_employment_type_or_404(id)
            employment_type.delete()
            return self.create_response(
                message={'message': 'Employment Type successfully deleted.'},
                status_code=200
            )
        except Exception as exc:
            self._handle_exception(exc)


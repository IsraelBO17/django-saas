import logging
from typing import List
from django.db.utils import Error
from ninja import PatchDict
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.exceptions import ValidationError
from core.permission import IsSuperAdmin
from organizations.models import SalaryGrade
from organizations.schemas import SalaryGradeInputSchema, SalaryGradeResponse


@api_controller('salary-grades', tags=['Salary Grade'], permissions=[IsSuperAdmin])
class SalaryGradeController(ControllerBase):

    def _get_salary_grade_or_404(self, id: str) -> SalaryGrade:
        salary_grade = self.get_object_or_exception(SalaryGrade, error_message="Salary Grade does not exist.", pk=id)
        return salary_grade

    def _handle_exception(self, exc):
        if isinstance(exc, Error):
            logging.exception(exc)
            error_details = {'type': type(exc).__name__, 'message': 'Unable to perform operation.'}
            raise ValidationError(error_details, 422)
        raise exc
    
    @route.post('/create')
    def create_salary_grade(self, payload: SalaryGradeInputSchema):
        try:
            salary_grade = SalaryGrade.objects.create(**payload.model_dump())
            message = {
                'status': 'success',
                'message': f'Salary Grade with id "{salary_grade.id}" created successfully.',
                'data': SalaryGradeResponse(**salary_grade.__dict__)
            }
            return self.create_response(message=message, status_code=200)
        except Exception as exc:
            self._handle_exception(exc)
    
    @route.get('/', response=List[SalaryGradeResponse])
    def get_all_salary_grades(self):
        job_titles = SalaryGrade.objects.all()
        return job_titles
    
    @route.patch('update/{id}', response=SalaryGradeResponse)
    def update_salary_grade(self, id: str, payload: PatchDict[SalaryGradeInputSchema]):
        try:
            salary_grade = self._get_salary_grade_or_404(id)
            for attr, value in payload.items():
                setattr(salary_grade, attr, value)
            salary_grade.save()
            return salary_grade
        except Exception as exc:
            self._handle_exception(exc)

    @route.get('/{id}', response=SalaryGradeResponse)
    def get_salary_grade(self, id: str):
        salary_grade = self._get_salary_grade_or_404(id)
        return salary_grade
    
    @route.delete('/{id}')
    def delete_salary_grade(self, id: str):
        try:
            salary_grade = self._get_salary_grade_or_404(id)
            salary_grade.delete()
            return self.create_response(
                message={'message': 'Salary Grade successfully deleted.'},
                status_code=200
            )
        except Exception as exc:
            self._handle_exception(exc)


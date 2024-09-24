import logging
from typing import List
from django.db.utils import Error
from ninja import PatchDict
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.exceptions import ValidationError
from core.permission import IsSuperAdmin
from organizations.models import JobLevel
from organizations.schemas import JobLevelInSchema, JobLevelResponse


@api_controller('job-levels', tags=['Job Level'], permissions=[IsSuperAdmin])
class JobLevelController(ControllerBase):

    def _get_job_level_or_404(self, id: str) -> JobLevel:
        job_level = self.get_object_or_exception(JobLevel, error_message="Job Level does not exist.", pk=id)
        return job_level

    def _handle_exception(self, exc):
        if isinstance(exc, Error):
            logging.exception(exc)
            error_details = {'type': type(exc).__name__, 'message': 'Unable to perform operation.'}
            raise ValidationError(error_details, 422)
        raise exc
    
    @route.post('/create')
    def create_job_level(self, payload: JobLevelInSchema):
        try:
            job_level = JobLevel.objects.create(**payload.model_dump())
            message = {
                'status': 'success',
                'message': f'Job Level with id "{job_level.id}" created successfully.',
                'data': JobLevelResponse(**job_level.__dict__)
            }
            return self.create_response(message=message, status_code=200)
        except Exception as exc:
            self._handle_exception(exc)
    
    @route.get('/', response=List[JobLevelResponse])
    def get_all_job_levels(self):
        job_levels = JobLevel.objects.all()
        return job_levels
    
    @route.patch('update/{id}', response=JobLevelResponse)
    def update_job_level(self, id: str, payload: PatchDict[JobLevelInSchema]):
        try:
            job_level = self._get_job_level_or_404(id)
            for attr, value in payload.items():
                setattr(job_level, attr, value)
            job_level.save()
            return job_level
        except Exception as exc:
            self._handle_exception(exc)

    @route.get('/{id}', response=JobLevelResponse)
    def get_job_level(self, id: str):
        job_level = self._get_job_level_or_404(id)
        return job_level
    
    @route.delete('/{id}')
    def delete_job_level(self, id: str):
        try:
            job_level = self._get_job_level_or_404(id)
            job_level.delete()
            return self.create_response(
                message={'message': 'Job Level successfully deleted.'},
                status_code=200
            )
        except Exception as exc:
            self._handle_exception(exc)


import logging
from typing import List
from django.db.utils import Error
from ninja import PatchDict
from ninja_extra import api_controller, route, ControllerBase
from ninja_extra.exceptions import ValidationError
from core.permission import IsSuperAdmin
from organizations.models import JobTitle
from organizations.schemas import JobTitleInputSchema, JobTitleResponse


@api_controller('job-titles', tags=['Job Title'], permissions=[IsSuperAdmin])
class JobTitleController(ControllerBase):

    def _get_job_title_or_404(self, id: str) -> JobTitle:
        job_title = self.get_object_or_exception(JobTitle, error_message="Job Title does not exist.", pk=id)
        return job_title

    def _handle_exception(self, exc):
        if isinstance(exc, Error):
            logging.exception(exc)
            error_details = {'type': type(exc).__name__, 'message': 'Unable to perform operation.'}
            raise ValidationError(error_details, 422)
        raise exc
    
    @route.post('/create')
    def create_job_title(self, payload: JobTitleInputSchema):
        try:
            job_title = JobTitle.objects.create(**payload.model_dump())
            message = {
                'status': 'success',
                'message': f'Job Title with id "{job_title.id}" created successfully.',
                'data': JobTitleResponse(**job_title.__dict__)
            }
            return self.create_response(message=message, status_code=200)
        except Exception as exc:
            self._handle_exception(exc)
    
    @route.get('/', response=List[JobTitleResponse])
    def get_all_job_titles(self):
        job_titles = JobTitle.objects.all()
        return job_titles
    
    @route.patch('update/{id}', response=JobTitleResponse)
    def update_job_title(self, id: str, payload: PatchDict[JobTitleInputSchema]):
        try:
            job_title = self._get_job_title_or_404(id)
            for attr, value in payload.items():
                setattr(job_title, attr, value)
            job_title.save()
            return job_title
        except Exception as exc:
            self._handle_exception(exc)

    @route.get('/{id}', response=JobTitleResponse)
    def get_job_title(self, id: str):
        job_title = self._get_job_title_or_404(id)
        return job_title
    
    @route.delete('/{id}')
    def delete_job_title(self, id: str):
        try:
            job_title = self._get_job_title_or_404(id)
            job_title.delete()
            return self.create_response(
                message={'message': 'Job Title successfully deleted.'},
                status_code=200
            )
        except Exception as exc:
            self._handle_exception(exc)


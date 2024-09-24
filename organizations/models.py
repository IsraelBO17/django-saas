import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class JobTitle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('job title'), max_length=150, unique=True)
    supervisor = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('department name'), max_length=150, unique=True)
    head_dpt = models.OneToOneField('users.User', on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.name


class EmploymentType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('employment type'), max_length=150, unique=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.name


class SalaryGrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('salary grade'), max_length=150, unique=True)
    pay = models.FloatField(_('salary amount'))
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.name


class JobLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('job level'), max_length=150, unique=True)
    salary_grade = models.ForeignKey('SalaryGrade', on_delete=models.SET_NULL, null=True)
    annual_leave = models.PositiveSmallIntegerField(_('amount of annual leave'), null=True, blank=True)
    study_leave = models.PositiveSmallIntegerField(_('amount of study leave'), null=True, blank=True)
    casual_leave = models.PositiveSmallIntegerField(_('amount of casual leave'), null=True, blank=True)
    maternity_leave = models.PositiveSmallIntegerField(_('amount of maternity leave'), null=True, blank=True)
    paternity_leave = models.PositiveSmallIntegerField(_('amount of paternity leave'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return self.name



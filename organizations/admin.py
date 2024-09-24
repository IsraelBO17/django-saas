from django.contrib import admin
from .models import JobTitle, Department, EmploymentType, SalaryGrade, JobLevel


admin.site.register(JobTitle)
admin.site.register(Department)
admin.site.register(EmploymentType)
admin.site.register(SalaryGrade)
admin.site.register(JobLevel)

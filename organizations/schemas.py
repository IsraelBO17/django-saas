from datetime import datetime
from typing import Optional
from ninja import Schema
from pydantic import UUID4

from users.schemas import UserOutSchema


class JobTitleInputSchema(Schema):
    name: str
    supervisor: Optional[UUID4] = None

class JobTitleResponse(Schema):
    id: UUID4
    name: str
    supervisor: Optional[UserOutSchema] = None
    created_at: datetime

class DepartmentInputSchema(Schema):
    name: str
    head_dpt: Optional[UUID4] = None

class DepartmentResponse(Schema):
    id: UUID4
    name: str
    head_dpt: Optional[UserOutSchema] = None
    created_at: datetime

class EmploymentTypeInputSchema(Schema):
    name: str

class EmploymentTypeResponse(Schema):
    id: UUID4
    name: str
    created_at: datetime

class SalaryGradeInputSchema(Schema):
    name: str
    pay: float | int

class SalaryGradeResponse(Schema):
    id: UUID4
    name: str
    pay: float
    updated_at: datetime
    created_at: datetime

class JobLevelInSchema(Schema):
    name: str
    salary_grade: Optional[UUID4] = None
    annual_leave_days: Optional[int] = None
    study_leave_days: Optional[int] = None
    casual_leave_days: Optional[int] = None
    maternity_leave_days: Optional[int] = None
    paternity_leave_days: Optional[int] = None

class JobLevelResponse(Schema):
    id: UUID4
    name: str
    salary_grade: Optional[SalaryGradeResponse] = None
    annual_leave_days: Optional[int] = None
    study_leave_days: Optional[int] = None
    casual_leave_days: Optional[int] = None
    maternity_leave_days: Optional[int] = None
    paternity_leave_days: Optional[int] = None
    created_at: datetime

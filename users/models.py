import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_(
            "Designates whether this user is verified as an employee."
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_context_string(self, context: str):
        return f'{context}{self.password[-6:]}{self.updated_at.strftime("%m%d%Y%H%M%S")}'.strip()
    

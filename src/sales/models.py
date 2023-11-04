import os
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator


def upload_path(instance, filename):
    return os.path.join(str(instance.__class__.__name__).lower() + '/', filename)


class Sale(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 0, 'PENDING'
        STARTED = 1, 'STARTED'
        SUCCESS = 2, 'SUCCESS'
        FAILURE = 3, 'FAILURE'

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=Status.choices, default=Status.PENDING)
    task_id = models.UUIDField(default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=upload_path, validators=[FileExtensionValidator(allowed_extensions=['xls', 'xlsx', 'csv'])])

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class SaleError(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='errors')
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

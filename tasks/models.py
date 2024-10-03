from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    sub_category = models.ForeignKey('self', on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=50)

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Task(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, null=True)
    is_completed = models.BooleanField(default=False)
    status = models.ForeignKey(Status, on_delete=models.PROTECT, null=True)
    due_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True)
    sub_task = models.ForeignKey('self', on_delete=models.PROTECT, null=True)
    task_category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, related_name='tasks')
    tags = models.ManyToManyField(Tag, related_name='tasks')

    def __str__(self):
        return self.name

class TaskAssignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments')
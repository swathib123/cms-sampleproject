from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError

# Custom User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('supervisor', 'Supervisor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

# Manager model
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')

    def __str__(self):
        return f"{self.user.username} - Manager"

# Supervisor model
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')

    def __str__(self):
        return f"{self.user.username} - Supervisor"

# Project model
class Project(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    timeline = models.DateField()
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, related_name='projects')

    def clean(self):
        if self.budget <= 0:
            raise ValidationError("Budget must be a positive value.")

    def __str__(self):
        return self.name

# Task model
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # Description is optional
    start_date = models.DateField(default=timezone.now)  # Set a default value
    end_date = models.DateField()
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, related_name='tasks')
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be earlier than start date.")

    def save(self, *args, **kwargs):
        self.clean()  # Call clean method before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Task: {self.name} for Project: {self.project.name}"

    class Meta:
        ordering = ['start_date']  # Order tasks by start date

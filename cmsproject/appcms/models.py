 
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
 
# Custom User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('supervisor', 'Supervisor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
 
# Manager model
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
 
    def __str__(self):
        return self.user.username
 
# Supervisor model
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')
 
    def __str__(self):
        return self.user.username
 
# Project model
class Project(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    timeline = models.DateField()
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True)
 
    def __str__(self):
        return self.name
 
# Task model
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    phase = models.CharField(max_length=100)
 
    def __str__(self):
        return self.name
 
# Other models (Material, Labor, Document, Incident) can be added similarly.
 
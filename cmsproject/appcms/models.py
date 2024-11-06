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
    department = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

# Supervisor model
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')

# Project model
class Project(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    timeline = models.DateField()
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True)
    manager = models.ForeignKey(Manager,on_delete=models.CASCADE, null=True)


class Resource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
class Worker(models.Model):
    name = models.CharField(max_length=100)
    aadhar_number = models.CharField(max_length=12, unique=True)  # Assuming Aadhar number is unique
    is_working = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Task(models.Model):
    name = models.CharField(max_length=100)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField()
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='tasks/images/', null=True, blank=True)
    supervisor = models.ForeignKey(Supervisor, related_name='tasks', on_delete=models.CASCADE)
    description = models.TextField() 

    def __str__(self):
        return self.name
    
class Task1(models.Model):
    name = models.CharField(max_length=255)
    resource = models.ForeignKey(Resource,null=True, blank=True, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField()
    worker = models.ForeignKey(Worker, null=True, blank=True, on_delete=models.SET_NULL)
    project_id = models.CharField(max_length=255)
    supervisor_id = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='tasks/', null=True, blank=True)
    description = models.TextField()

    def save(self, *args, **kwargs):
        # Update resource quantity when task is saved
        if self.worker and not self.worker.is_working:
            self.worker = None  # If worker is not working, set to None

        # Reduce resource quantity
        if self.resource:
            self.resource.quantity -= self.quantity_used
            self.resource.save()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Task2(models.Model):
    name = models.CharField(max_length=255)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField()
    worker = models.ForeignKey(Worker, null=True, blank=True, on_delete=models.SET_NULL)
    project_id = models.CharField(max_length=255)
    supervisor_id = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='tasks/', null=True, blank=True)
    description = models.TextField()

    def save(self, *args, **kwargs):
        # Ensure that the task has a valid resource before saving
        if not self.resource:
            raise ValueError("A valid resource is required for the task.")
        # Check if resource has enough quantity
        if self.resource.quantity < self.quantity_used:
            raise ValueError(f"Insufficient quantity for resource {self.resource.name}.")
        
        # Update resource quantity
        self.resource.quantity -= self.quantity_used
        self.resource.save()

        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

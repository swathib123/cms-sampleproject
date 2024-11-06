from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import transaction

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

    def __str__(self):
        return self.name

# Resource model
class Resource(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def reduce_quantity(self, amount):
        if self.quantity < amount:
            raise ValueError(f"Insufficient quantity. Available: {self.quantity}, Requested: {amount}")
        self.quantity -= amount
        self.save()

    def restore_quantity(self, amount):
        self.quantity += amount
        self.save()


# Worker model
class Worker(models.Model):
    name = models.CharField(max_length=100)
    aadhar_number = models.CharField(max_length=12, unique=True)  # Assuming Aadhar number is unique
    is_working = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Task2 model
# If Task1 is still in the file, remove it.
from django.db import transaction

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
        # Ensure that the task has a valid resource
        if not self.resource:
            raise ValueError("A valid resource is required for the task.")

        # Ensure the resource has a `quantity` field, and check the quantity
        if not hasattr(self.resource, 'quantity'):
            raise ValueError(f"Resource {self.resource.name} does not have a 'quantity' field.")
        
        # Check if the resource has enough quantity
        if self.resource.quantity < self.quantity_used:
            raise ValueError(f"Insufficient quantity for resource {self.resource.name}. Available: {self.resource.quantity}, Required: {self.quantity_used}")

        # Use atomic transaction to ensure that resource quantity is properly updated
        with transaction.atomic():
            # Reduce the resource quantity
            self.resource.quantity -= self.quantity_used
            self.resource.save()

            # Call the superclass save method to save the task
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

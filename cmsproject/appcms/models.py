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

    def __str__(self):
        return f"{self.user.username} - {self.department}"

# Supervisor model
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')

    def __str__(self):
        return f"{self.user.username}"

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
    # Define the available resource types
    MATERIAL = 'material'
    EQUIPMENT = 'equipment'
    LABOR = 'labor'
    
    RESOURCE_TYPES = [
        (MATERIAL, 'Material'),
        (EQUIPMENT, 'Equipment'),
        (LABOR, 'Labor'),
    ]
    
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        default=MATERIAL,  # Default to 'Material' type
    )

    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"

    def reduce_quantity(self, amount):
        """ Reduces the resource quantity and saves it atomically """
        if self.quantity < amount:
            raise ValueError(f"Insufficient quantity. Available: {self.quantity}, Requested: {amount}")
        self.quantity -= amount
        self.save()

    def restore_quantity(self, amount):
        """ Restores the resource quantity and saves it atomically """
        self.quantity += amount
        self.save()

# Worker model
class Worker(models.Model):
    name = models.CharField(max_length=100)
    aadhar_number = models.CharField(max_length=12, unique=True)  # Assuming Aadhar number is unique
    is_working = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Task model
class Task(models.Model):
    name = models.CharField(max_length=255)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField()
    worker = models.ForeignKey(Worker, null=True, blank=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='tasks/', null=True, blank=True)
    description = models.TextField()

    def save(self, *args, **kwargs):
        """ Ensure that sufficient resource quantity is available and save the task atomically """
        # Ensure that the task has a valid resource
        if not self.resource:
            raise ValueError("A valid resource is required for the task.")

        # Check if the resource has enough quantity
        if self.resource.quantity < self.quantity_used:
            raise ValueError(f"Insufficient quantity for resource {self.resource.name}. Available: {self.resource.quantity}, Required: {self.quantity_used}")

        # Use atomic transaction to ensure that resource quantity is properly updated
        with transaction.atomic():
            # Reduce the resource quantity
            self.resource.reduce_quantity(self.quantity_used)

            # Call the superclass save method to save the task
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Document model
class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('blueprint', 'Blueprint'),
        ('contract', 'Contract'),
        ('inspection_report', 'Inspection Report'),
        ('video', 'Video'),
        ('image', 'Image'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"
#.............."end".............................
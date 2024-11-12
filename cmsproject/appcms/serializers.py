from rest_framework import serializers
from .models import User, Manager, Supervisor, Project, Task, Resource, Worker, Document

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}  # Make password write-only

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user


# Manager Serializer
class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ('id', 'user', 'department', 'phone_number')


# Supervisor Serializer
class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ('id', 'user')


# Project Serializer
class ProjectSerializer(serializers.ModelSerializer):
    supervisor = SupervisorSerializer(read_only=True)  # For displaying supervisor details
    supervisor_id = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), write_only=True)  # For incoming supervisor ID

    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        supervisor_id = validated_data.pop('supervisor_id', None)  # Remove supervisor_id from validated data

        project = Project.objects.create(**validated_data)  # Create the project instance

        if supervisor_id:
            project.supervisor = Supervisor.objects.get(id=supervisor_id)  # Assign the supervisor based on ID

        project.save()
        return project


# Resource Serializer
class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'quantity']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value


# Worker Serializer
class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['id', 'name', 'aadhar_number', 'is_working']

    def validate_aadhar_number(self, value):
        if len(str(value)) != 12:
            raise serializers.ValidationError("Aadhar number must be exactly 12 digits long.")
        return value


# Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['name', 'resource', 'quantity_used', 'worker', 'project', 'supervisor', 'start_date', 'end_date', 'image', 'description']

    def validate(self, data):
        resource = data.get('resource')
        quantity_used = data.get('quantity_used')

        if not resource:
            raise serializers.ValidationError("Resource is required.")
        
        if quantity_used is None or quantity_used <= 0:
            raise serializers.ValidationError("Quantity used must be a positive integer.")

        if resource.quantity < quantity_used:
            raise serializers.ValidationError(
                f"Insufficient quantity for resource {resource.name}. Available: {resource.quantity}, Requested: {quantity_used}"
            )
        
        return data


# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='manager.phone_number', required=False)  # Optional phone number field

    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'phone_number')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if instance.role == 'manager':  # If the user is a manager, get their phone number
            manager = instance.manager_profile  # Assuming manager_profile is a related field on the User model
            data['phone_number'] = manager.phone_number if manager else None

        return data


# Document Serializer
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'project', 'title', 'document_type', 'file', 'created_at']

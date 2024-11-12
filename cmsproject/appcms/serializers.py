from rest_framework import serializers
from .models import User, Manager, Supervisor, Project, Task, Resource, Worker, Document, Media


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
    supervisor = SupervisorSerializer(read_only=True)  # Display supervisor details
    supervisor_id = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), write_only=True)  # For incoming supervisor ID

    class Meta:
        model = Project
        fields = ['id', 'name', 'location', 'budget', 'timeline', 'supervisor', 'supervisor_id']

    def validate(self, data):
        # Validate supervisor_id if provided
        supervisor_id = data.get('supervisor_id')
        if supervisor_id:
            try:
                Supervisor.objects.get(id=supervisor_id)  # Check if supervisor exists
            except Supervisor.DoesNotExist:
                raise serializers.ValidationError("Supervisor not found.")
        return data


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
        fields = ['id', 'name', 'resource', 'quantity_used', 'worker', 'project', 'supervisor', 'start_date', 'end_date', 'image', 'description']

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
class ProjectSerializer(serializers.ModelSerializer):
    supervisor = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all())

    class Meta:
        model = Project
        fields = ['id', 'name', 'supervisor', 'location', 'budget', 'timeline']

    def validate(self, data):
        # Validate supervisor_id if provided
        supervisor_id = data.get('supervisor_id')
        if supervisor_id:
            try:
                Supervisor.objects.get(id=supervisor_id)  # Check if supervisor exists
            except Supervisor.DoesNotExist:
                raise serializers.ValidationError("Supervisor not found.")
        return data
        

# Document Serializer
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'project', 'title', 'document_type', 'file', 'created_at']


# Media Serializer
class MediaSerializer(serializers.ModelSerializer):
    # Optional: You can use the related model fields for convenience
    supervisor_id = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), write_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(queryset=Manager.objects.all(), write_only=True)
    
    class Meta:
        model = Media
        fields = ['id', 'project', 'supervisor', 'manager', 'image', 'video', 'description', 'created_at']

    def validate(self, data):
        # Ensure either image or video is provided
        if not data.get('image') and not data.get('video'):
            raise serializers.ValidationError("Either image or video must be provided.")
        
        # Optional: Add file validation (file size, type, etc.)
        if data.get('image'):
            if not data['image'].name.endswith(('.jpg', '.jpeg', '.png')):
                raise serializers.ValidationError("Image must be in JPG, JPEG, or PNG format.")
        if data.get('video'):
            if not data['video'].name.endswith(('.mp4', '.mkv', '.avi')):
                raise serializers.ValidationError("Video must be in MP4, MKV, or AVI format.")
        
        return data

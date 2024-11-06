from rest_framework import serializers
from .models import User, Manager, Supervisor, Project, Task,Resource,Worker,Task2

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ('user','department','phone_number')

class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ('user',)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'quantity']

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['id', 'name', 'aadhar_number', 'is_working']

class TaskSerializer(serializers.ModelSerializer):
    worker = WorkerSerializer(read_only=True)
    resource = ResourceSerializer(read_only=True)

    class Meta:
        model = Task2
        fields = ['id', 'name', 'resource', 'quantity_used', 'worker', 'project_id', 'supervisor_id', 'start_date', 'end_date', 'image', 'description']
    
    def create(self, validated_data):
        # Create the task instance first
        task = Task2.objects.create(**validated_data)
        
        # The resource quantity will be updated automatically when the task is saved (due to the save method in Task model)
        
        return task
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'role', 'phone_number')

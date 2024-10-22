from rest_framework import serializers
from .models import User, Manager, Supervisor, Project, Task
 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
 
class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'
 
class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = '__all__'
 
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
 
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
 
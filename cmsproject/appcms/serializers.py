from rest_framework import serializers
from .models import User, Manager, Supervisor, Project, Task

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
    user = UserSerializer()

    class Meta:
        model = Manager
        fields = ('user',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')  # Extract user data
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()  # Save the user
        return Manager.objects.create(user=user)

class SupervisorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Supervisor
        fields = ('user',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')  # Extract user data
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()  # Save the user
        return Supervisor.objects.create(user=user)

class ProjectSerializer(serializers.ModelSerializer):
    supervisor = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), required=False)

    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        return Project.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.location = validated_data.get('location', instance.location)
        instance.budget = validated_data.get('budget', instance.budget)
        instance.timeline = validated_data.get('timeline', instance.timeline)
        instance.supervisor = validated_data.get('supervisor', instance.supervisor)
        instance.save()
        return instance

class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    supervisor = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), required=False)

    class Meta:
        model = Task
        fields = ('id', 'project', 'name', 'description', 'start_date', 'end_date', 'supervisor', 'image')

    def create(self, validated_data):
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.supervisor = validated_data.get('supervisor', instance.supervisor)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

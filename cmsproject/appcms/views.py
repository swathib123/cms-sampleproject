from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Manager, Supervisor, Project, Task, User
from .serializers import ManagerSerializer, SupervisorSerializer, UserSerializer, ProjectSerializer, TaskSerializer

# Manager registration view
class ManagerRegisterView(generics.CreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.pop('user')  # Assuming user data is nested
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()  # Create the user
        
        manager = Manager.objects.create(user=user)  # Create the manager profile
        
        # Generate token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({'token': token.key, 'manager_id': manager.id})

# Supervisor registration view
class SupervisorRegisterView(generics.CreateAPIView):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.pop('user')  # Assuming user data is nested
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()  # Create the user
        
        supervisor = Supervisor.objects.create(user=user)  # Create the supervisor profile
        
        # Generate token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({'token': token.key, 'supervisor_id': supervisor.id})

# Custom login view to obtain token
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['token']
        return Response({'token': token})

# Project viewset for managing projects
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

# Task viewset for managing tasks
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

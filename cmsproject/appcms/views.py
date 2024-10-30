from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from .models import Manager, Supervisor, Project, Task
from .serializers import ManagerSerializer, SupervisorSerializer, UserSerializer, ProjectSerializer, TaskSerializer

# Manager registration view
class ManagerRegisterView(generics.CreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.get('user')  # Extract user data from request
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Create the manager profile
        manager = Manager.objects.create(user=user)

        # Generate token for the user
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key, 'manager_id': manager.id})

# Supervisor registration view
class SupervisorRegisterView(generics.CreateAPIView):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.get('user')  # Extract user data from request
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        # Create the supervisor profile
        supervisor = Supervisor.objects.create(user=user)

        # Generate token for the user
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key, 'supervisor_id': supervisor.id})

# Custom login view to obtain token
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['token']
        
        # Get user details
        user_data = {
            'username': request.user.username,
            'role': request.user.role,
        }

        return Response({'token': token, 'user': user_data})

# User detail view to get current user info
class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user

        # Check for manager or supervisor profiles
        if hasattr(user, 'manager_profile'):
            serializer = ManagerSerializer(user.manager_profile)
            return Response(serializer.data)
        elif hasattr(user, 'supervisor_profile'):
            serializer = SupervisorSerializer(user.supervisor_profile)
            return Response(serializer.data)

        return Response({'detail': 'User is not a manager or supervisor'}, status=403)

# Project viewset for managing projects
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Return projects based on user's role
            if self.request.user.role == 'manager':
                return Project.objects.filter(supervisor__user=self.request.user)
            elif self.request.user.role == 'supervisor':
                return Project.objects.filter(supervisor__user=self.request.user)
            return Project.objects.all()
        return Project.objects.none()

# Task viewset for managing tasks
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Return tasks based on user's role
            if self.request.user.role == 'supervisor':
                return Task.objects.filter(project__supervisor__user=self.request.user)
            return Task.objects.all()
        return Task.objects.none()

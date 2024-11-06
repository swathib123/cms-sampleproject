from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Manager, Supervisor, Project, Task, User
from .serializers import ManagerSerializer, SupervisorSerializer,WorkerSerializer,ResourceSerializer, UserSerializer, ProjectSerializer, TaskSerializer
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .models import Manager,Resource,Worker
from rest_framework import status
 

class ManagerRegisterView(generics.CreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.pop('user')  # Assuming user data is nested
        
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)

        try:
            user = user_serializer.save()  # Create the user

            department = request.data.get('department')
            phone_number = request.data.get('phone_number')

            if not department or not phone_number:
                return Response({"error": "Department and phone number are required."}, status=400)

            manager = Manager.objects.create(
                user=user,
                department=department,
                phone_number=phone_number
            )  # Create the manager profile

            # Generate token for the user
            token, created = Token.objects.get_or_create(user=user)

            return Response({'message': 'Successfully registered as a manager.',
                             'token': token.key, 
                             'manager_id': manager.id}, status=status.HTTP_201_CREATED)
        
        except IntegrityError:
            return Response({"error": "User or manager profile could not be created due to integrity issues."}, status=400)

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
        
        return Response({'message': 'Successfully registered as a supervisor.',
                         'token': token.key, 
                         'supervisor_id': supervisor.id}, status=status.HTTP_201_CREATED)

# Custom login view to obtain token
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['token']
        return Response({'message': 'Login successful!',
                         'token': token}, status=status.HTTP_200_OK)

# Project viewset for managing projects
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer



from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Resource, Worker, Task2
from .serializers import ResourceSerializer, WorkerSerializer, TaskSerializer

# Resource Viewset
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

# Worker Viewset
class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer

# Task Viewset
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task2.objects.all()
    serializer_class = TaskSerializer

   


class ManagerProfileView(generics.RetrieveAPIView):
    serializer_class = ManagerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
         
        return Response({
            "username": user.username,
            "role": user.role,
             
        })

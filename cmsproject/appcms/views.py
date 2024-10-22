from django.shortcuts import render
 
# Create your views here.
from rest_framework import viewsets
from .models import Manager, Supervisor, Project, Task
from .serializers import ManagerSerializer, SupervisorSerializer, ProjectSerializer, TaskSerializer
 
class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
 
class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer
 
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
 
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
 
 
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import UserSerializer
 
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
 
    def create(self, request, *args, **kwargs):
        user = super().create(request, *args, **kwargs)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
 
from rest_framework.authtoken.views import ObtainAuthToken
 
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['token']
        return Response({'token': token})
 
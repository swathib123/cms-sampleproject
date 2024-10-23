from rest_framework import generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Manager, Supervisor, Project, Task, User
from .serializers import ManagerSerializer, SupervisorSerializer, UserSerializer, ProjectSerializer, TaskSerializer


class ManagerRegisterView(generics.CreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.pop('user')  
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()  
        
        manager = Manager.objects.create(user=user,department=request.data.get('department'), phone_number=request.data.get('phone_number'))  # Create the manager profile
        
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({'token': token.key, 'manager_id': manager.id})


class SupervisorRegisterView(generics.CreateAPIView):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.pop('user')  
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save() 
        
        supervisor = Supervisor.objects.create(user=user) 
        
       
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({'token': token.key, 'supervisor_id': supervisor.id})


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['token']
        return Response({'token': token})


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
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
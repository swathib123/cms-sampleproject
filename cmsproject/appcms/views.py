from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Manager, Supervisor, Project, Task, User, Resource, Worker, Document
from .serializers import ManagerSerializer, SupervisorSerializer, UserSerializer, ProjectSerializer, TaskSerializer, ResourceSerializer, WorkerSerializer, DocumentSerializer
from django.db import IntegrityError, transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action

# Manager Registration View
class ManagerRegisterView(generics.CreateAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.pop('user')  # Assuming user data is nested
        
        # Validate user data
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)

        try:
            # Create the user
            user = user_serializer.save()

            # Validate manager-specific fields
            department = request.data.get('department')
            phone_number = request.data.get('phone_number')

            if not department or not phone_number:
                return Response({"error": "Department and phone number are required."}, status=status.HTTP_400_BAD_REQUEST)

            # Create the manager profile
            manager = Manager.objects.create(
                user=user,
                department=department,
                phone_number=phone_number
            )

            # Generate a token for the user
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'message': 'Successfully registered as a manager.',
                'token': token.key,
                'manager_id': manager.id
            }, status=status.HTTP_201_CREATED)
        
        except IntegrityError:
            return Response({
                "error": "User or manager profile could not be created due to integrity issues."
            }, status=status.HTTP_400_BAD_REQUEST)


# Supervisor Registration View
class SupervisorRegisterView(generics.CreateAPIView):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer

    def create(self, request, *args, **kwargs):
        user_data = request.data.pop('user')  # Assuming user data is nested
        
        # Validate user data
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()  # Create the user
        
        # Create the supervisor profile
        supervisor = Supervisor.objects.create(user=user)

        # Generate a token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Successfully registered as a supervisor.',
            'token': token.key, 
            'supervisor_id': supervisor.id
        }, status=status.HTTP_201_CREATED)


# Custom Auth Token View
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['token']
        return Response({
            'message': 'Login successful!',
            'token': token
        }, status=status.HTTP_200_OK)


# Project Viewset
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    # Override the create method to handle the supervisor_id
    def perform_create(self, serializer):
        supervisor_id = self.request.data.get('supervisor_id')

        if supervisor_id:
            supervisor = Supervisor.objects.get(id=supervisor_id)
            serializer.validated_data['supervisor'] = supervisor

        serializer.save()

    # Override the update method if you need to handle updates similarly
    def perform_update(self, serializer):
        supervisor_id = self.request.data.get('supervisor_id')

        if supervisor_id:
            supervisor = Supervisor.objects.get(id=supervisor_id)
            serializer.validated_data['supervisor'] = supervisor

        serializer.save()


# Resource Viewset
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    # Custom action for reducing resource quantity
    @action(detail=True, methods=['post'])
    def reduce(self, request, pk=None):
        resource = self.get_object()  # Get the resource instance
        amount = request.data.get('amount')  # Get the amount to reduce
        
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resource.reduce_quantity(amount)
            return Response({
                "message": "Quantity reduced successfully",
                "quantity": resource.quantity
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Custom action for restoring resource quantity
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        resource = self.get_object()  # Get the resource instance
        amount = request.data.get('amount')  # Get the amount to restore
        
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        resource.restore_quantity(amount)
        return Response({
            "message": "Quantity restored successfully",
            "quantity": resource.quantity
        }, status=status.HTTP_200_OK)


# Worker Viewset
class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all() 
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated]  # Optional: Restrict access to authenticated users


# Task Viewset
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        resource = serializer.validated_data.get('resource')
        quantity_used = serializer.validated_data.get('quantity_used')

        # Ensure that the resource has enough quantity
        if resource.quantity < quantity_used:
            raise ValidationError(f"Insufficient quantity for resource {resource.name}. Available: {resource.quantity}")

        # Use a transaction to lock the resource and ensure atomicity
        with transaction.atomic():
            try:
                resource = Resource.objects.select_for_update().get(id=resource.id)
            except Resource.DoesNotExist:
                raise ValidationError(f"Resource {resource.name} does not exist.")
            
            if resource.quantity < quantity_used:
                raise ValidationError(f"Insufficient quantity for resource {resource.name}. Available: {resource.quantity}")

            resource.quantity -= quantity_used
            resource.save()

            serializer.save()

    def perform_update(self, serializer):
        resource = serializer.validated_data.get('resource')
        quantity_used = serializer.validated_data.get('quantity_used')

        if resource and quantity_used is not None:
            old_quantity_used = serializer.instance.quantity_used if serializer.instance else 0

            if quantity_used != old_quantity_used:
                if resource.quantity < quantity_used:
                    raise ValidationError(f"Insufficient quantity for resource {resource.name}. Available: {resource.quantity}")

                with transaction.atomic():
                    try:
                        resource = Resource.objects.select_for_update().get(id=resource.id)
                    except Resource.DoesNotExist:
                        raise ValidationError(f"Resource {resource.name} does not exist.")

                    if quantity_used > old_quantity_used:
                        resource.quantity -= (quantity_used - old_quantity_used)
                    else:
                        resource.quantity += (old_quantity_used - quantity_used)
                    resource.save()

        serializer.save()

    def perform_destroy(self, instance):
        if instance.resource:
            resource = instance.resource
            with transaction.atomic():
                try:
                    resource = Resource.objects.select_for_update().get(id=resource.id)
                except Resource.DoesNotExist:
                    raise ValidationError(f"Resource {resource.name} does not exist.")
                
                resource.quantity += instance.quantity_used
                resource.save()

        instance.delete()


# Manager Profile View
class ManagerProfileView(generics.RetrieveAPIView):
    serializer_class = ManagerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        try:
            manager = user.manager_profile
        except Manager.DoesNotExist:
            return Response({"error": "Manager profile not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "username": user.username,
            "role": user.role,
            "department": manager.department,
            "phone_number": manager.phone_number
        })


# Document Viewset
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])  # Action only for authenticated users
    def upload_document(self, request):
        project_id = request.data.get('project')

        if not project_id:
            return Response({"detail": "Project ID is required."}, status=400)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        # If supervisor is the user, return error
        if project.supervisor == request.user:
            return Response({"detail": "Supervisors cannot upload documents for this project."}, status=403)

        # Serialize the data and validate
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Document uploaded successfully!"}, status=201)

        return Response(serializer.errors, status=400)
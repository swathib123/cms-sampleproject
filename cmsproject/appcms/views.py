from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Manager, Supervisor, Project, Task, User, Resource, Worker, Document, Media
from .serializers import ManagerSerializer, SupervisorSerializer, UserSerializer, ProjectSerializer, TaskSerializer, ResourceSerializer, WorkerSerializer, DocumentSerializer, MediaSerializer
from django.db import IntegrityError, transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.decorators import action
from .permissions import IsManager  # Custom permission for Manager access only
import logging
# Setup logging
logger = logging.getLogger(__name__)

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

    def perform_create(self, serializer):
        supervisor_id = self.request.data.get('supervisor')
        try:
            supervisor = Supervisor.objects.get(id=supervisor_id)
        except Supervisor.DoesNotExist:
            raise serializers.ValidationError("Supervisor not found.")
        # Ensure the supervisor is set correctly in the project instance
        serializer.save(supervisor=supervisor)

# Resource Viewset
class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    @action(detail=True, methods=['post'])
    def reduce(self, request, pk=None):
        resource = self.get_object()
        amount = request.data.get('amount')
        
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

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        resource = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resource.restore_quantity(amount)
            return Response({
                "message": "Quantity restored successfully",
                "quantity": resource.quantity
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Worker Viewset
class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access the API

    def create(self, request, *args, **kwargs):
        # Extract Aadhar number from the request data
        aadhar_number = request.data.get('aadhar_number')

        # Check if the worker already exists by Aadhar number
        if Worker.objects.filter(aadhar_number=aadhar_number).exists():
            return Response(
                {"detail": "A worker with this Aadhar number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optionally, you can check based on other fields like the name:
        # if Worker.objects.filter(name=request.data.get('name')).exists():
        #     return Response(
        #         {"detail": "A worker with this name already exists."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # If the validation passes, proceed with normal creation
        return super().create(request, *args, **kwargs)

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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_document(self, request):
        # Check if the user is a manager
        if request.user.role != 'manager':
            return Response({"detail": "You must be a manager to upload documents."}, status=403)

        # Retrieve the project ID from the request
        project_id = request.data.get('project')

        # Ensure the project ID is provided
        if not project_id:
            return Response({"detail": "Project ID is required."}, status=400)

        # Check if the project exists
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        # If supervisor is the user, return error
        if project.supervisor == request.user:
            return Response({"detail": "Supervisors cannot upload documents for this project."}, status=400)

        # Proceed with file upload logic (e.g., saving file to database or storage)
        document = Document.objects.create(
            project=project,
            file=request.FILES.get('file'),
            uploaded_by=request.user
        )
        
        return Response({
            "message": "Document uploaded successfully.",
            "document_id": document.id
        }, status=status.HTTP_201_CREATED)


# Media Viewset

class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_media(self, request):
        # Ensure the media file (image or video) is provided
        media_file = request.FILES.get('file')
        project_id = request.data.get('project')
        supervisor_id = request.data.get('supervisor')
        manager_id = request.data.get('manager')
        description = request.data.get('description', '')

        if not media_file:
            return Response({"error": "Media file is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate that the project, supervisor, and manager exist
        try:
            project = Project.objects.get(id=project_id)
            supervisor = Supervisor.objects.get(id=supervisor_id)
            manager = Manager.objects.get(id=manager_id)
        except (Project.DoesNotExist, Supervisor.DoesNotExist, Manager.DoesNotExist):
            return Response({"error": "Invalid project, supervisor, or manager ID."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the Media instance based on the provided data
        media = Media.objects.create(
            project=project,
            supervisor=supervisor,
            manager=manager,
            description=description
        )

        # Assign the image or video file
        if media_file.name.endswith(('.jpg', '.jpeg', '.png')):
            media.image = media_file
        elif media_file.name.endswith(('.mp4', '.mkv', '.avi')):
            media.video = media_file
        else:
            return Response({"error": "Invalid file format. Only image and video files are allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the media object
        media.save()

        return Response({
            "message": "Media uploaded successfully.",
            "media_id": media.id
        }, status=status.HTTP_201_CREATED)

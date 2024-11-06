from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Manager, Supervisor, Project, Task2, User, Resource, Worker
from .serializers import ManagerSerializer, SupervisorSerializer, UserSerializer, ProjectSerializer, TaskSerializer, ResourceSerializer, WorkerSerializer
from django.db import IntegrityError
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

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


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    # Override the create method to only handle the supervisor_id
    def perform_create(self, serializer):
        # Extract supervisor_id from the request data
        supervisor_id = self.request.data.get('supervisor_id')

        # If supervisor_id is passed, set the supervisor for the project
        if supervisor_id:
            supervisor = Supervisor.objects.get(id=supervisor_id)
            serializer.validated_data['supervisor'] = supervisor

        # Save the project with the supervisor set
        serializer.save()

    # Override the update method if you need to handle updates in the same way
    def perform_update(self, serializer):
        # Extract supervisor_id from the request data
        supervisor_id = self.request.data.get('supervisor_id')

        # If supervisor_id is passed, set the supervisor for the project
        if supervisor_id:
            supervisor = Supervisor.objects.get(id=supervisor_id)
            serializer.validated_data['supervisor'] = supervisor

        # Save the project with the updated supervisor
        serializer.save()



class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    def perform_create(self, serializer):
        """
        Override the default create method to handle custom logic 
        when creating a resource, if needed.
        """
        # You can add any custom logic here, for example, 
        # logging or performing additional actions before saving.
        serializer.save()

    def perform_update(self, serializer):
        """
        Override the default update method to handle custom logic 
        when updating a resource, if needed.
        """
        # For example, you might want to add a check here 
        # if the quantity goes below a certain threshold.
        resource = serializer.save()
        if resource.quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        
    def perform_destroy(self, instance):
        """
        Override the destroy method to add custom logic when deleting a resource.
        For example, you could prevent deletion if the resource is in use.
        """
        # Add custom logic before deleting a resource, if necessary.
        if instance.quantity > 0:
            raise ValidationError("Cannot delete a resource with remaining quantity.")
        instance.delete()

# Worker Viewset

class WorkerViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Worker instances.
    """
    queryset = Worker.objects.all()  # This gets all Worker objects from the database
    serializer_class = WorkerSerializer  # This tells DRF to use WorkerSerializer for serialization

    # Optional: If you want to restrict access to authenticated users
    permission_classes = [IsAuthenticated]

    # Optional: If you want to customize the query (filtering, ordering, etc.)
    # def get_queryset(self):
    #     user = self.request.user
    #     return Worker.objects.filter(user=user)  # Example of filtering by user

# Task Viewset
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task2.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        """
        Override the default create method to handle the logic 
        for reducing resource quantity and checking its availability.
        """
        # Get the resource and quantity from the validated data
        resource = serializer.validated_data.get('resource')
        quantity_used = serializer.validated_data.get('quantity_used')

        # Ensure that the resource has enough quantity
        if resource.quantity < quantity_used:
            raise ValidationError(f"Insufficient quantity for resource {resource.name}. Available: {resource.quantity}")

        # Start a transaction to ensure atomicity (consistency of resource usage)
        with transaction.atomic():
            # Lock the resource to prevent race conditions
            try:
                resource = Resource.objects.select_for_update().get(id=resource.id)
            except Resource.DoesNotExist:
                raise ValidationError(f"Resource {resource.name} does not exist.")
            
            # Check if the resource has enough quantity again after locking
            if resource.quantity < quantity_used:
                raise ValidationError(f"Insufficient quantity for resource {resource.name}. Available: {resource.quantity}")

            # Reduce the resource quantity
            resource.quantity -= quantity_used
            resource.save()

            # Create the task instance using the serializer
            serializer.save()

    def perform_update(self, serializer):
        """
        Override the default update method to ensure that resources are correctly handled during updates.
        """
        # Get the resource and quantity from the validated data
        resource = serializer.validated_data.get('resource')
        quantity_used = serializer.validated_data.get('quantity_used')

        # If the resource quantity is changed, we need to check it again
        if resource and quantity_used is not None:
            old_quantity_used = serializer.instance.quantity_used if serializer.instance else 0

            # If the quantity_used is changed, we need to update the resource quantity accordingly
            if quantity_used != old_quantity_used:
                # If the new quantity used is greater, we need to check if the resource has enough quantity
                if resource.quantity < quantity_used:
                    raise ValidationError(f"Insufficient quantity for resource {resource.name}. Available: {resource.quantity}")

                # Start a transaction to ensure atomicity (consistency of resource usage)
                with transaction.atomic():
                    try:
                        resource = Resource.objects.select_for_update().get(id=resource.id)
                    except Resource.DoesNotExist:
                        raise ValidationError(f"Resource {resource.name} does not exist.")

                    # Adjust the resource quantity (take the difference)
                    if quantity_used > old_quantity_used:
                        resource.quantity -= (quantity_used - old_quantity_used)
                    else:
                        resource.quantity += (old_quantity_used - quantity_used)
                    resource.save()

        # Save the updated task
        serializer.save()

    def perform_destroy(self, instance):
        """
        Handle custom logic before destroying a task instance.
        For example, if we want to undo the resource quantity changes when deleting a task.
        """
        # If the task is deleted, we can optionally update the resource quantity to add back the used quantity
        if instance.resource:
            resource = instance.resource
            with transaction.atomic():
                try:
                    resource = Resource.objects.select_for_update().get(id=resource.id)
                except Resource.DoesNotExist:
                    raise ValidationError(f"Resource {resource.name} does not exist.")
                
                # Return the used quantity to the resource
                resource.quantity += instance.quantity_used
                resource.save()

        # Call the default destroy method to delete the task
        instance.delete()

# Manager Profile View
class ManagerProfileView(generics.RetrieveAPIView):
    serializer_class = ManagerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get the manager profile
        try:
            manager = user.manager_profile  # Assuming user is linked to manager profile
        except Manager.DoesNotExist:
            return Response({"error": "Manager profile not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "username": user.username,
            "role": user.role,
            "department": manager.department,
            "phone_number": manager.phone_number
        })

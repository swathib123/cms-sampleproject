from rest_framework import serializers
from .models import User, Manager, Supervisor, Project,  Task2, Resource, Worker

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ('id', 'user', 'department', 'phone_number')


class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ('id', 'user')


#project
class ProjectSerializer(serializers.ModelSerializer):
    # Supervisor is included in the response, but manager is removed
    supervisor = SupervisorSerializer(read_only=True)

    # Only supervisor_id is needed to create a project
    supervisor_id = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all(), write_only=True)

    class Meta:
        model = Project
        fields = '__all__'  # Or manually specify fields here if needed

    def create(self, validated_data):
        # Get the supervisor ID from validated data
        supervisor_id = validated_data.pop('supervisor_id', None)

        # Create the project instance with the remaining data
        project = Project.objects.create(**validated_data)
        
        # Set the supervisor
        if supervisor_id:
            project.supervisor = supervisor_id
        
        # Optionally, you can set the manager here if needed (depends on your logic)
        # For example, if you want to automatically assign a manager based on the supervisor
        # project.manager = project.supervisor.manager  # Assuming supervisor has a manager

        project.save()
        return project






class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'quantity']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value





class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['id', 'name', 'aadhar_number', 'is_working']

    # Optional: You can add some custom validation here if required.
    def validate_aadhar_number(self, value):
        # Example: You could check if the Aadhar number is exactly 12 digits long
        if len(str(value)) != 12:
            raise serializers.ValidationError("Aadhar number must be exactly 12 digits long.")
        return value





class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task2
        fields = ['name', 'resource', 'quantity_used', 'worker', 'project_id', 'supervisor_id', 'start_date', 'end_date', 'image', 'description']

    def validate(self, data):
        # Retrieve the resource and quantity_used from the input data
        resource = data.get('resource')
        quantity_used = data.get('quantity_used')

        # Ensure that a resource and quantity_used are provided
        if not resource:
            raise serializers.ValidationError("Resource is required.")
        
        if quantity_used is None or quantity_used <= 0:
            raise serializers.ValidationError("Quantity used must be a positive integer.")

        # Ensure that the resource has enough quantity
        if resource.quantity < quantity_used:
            raise serializers.ValidationError(
                f"Insufficient quantity for resource {resource.name}. Available: {resource.quantity}, Requested: {quantity_used}"
            )
        
        return data


class ProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='manager.phone_number', required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'role', 'phone_number')  # Added phone_number reference from Manager profile

    def to_representation(self, instance):
        """
        Custom representation for Profile, including phone number from Manager if available
        """
        data = super().to_representation(instance)
        if instance.role == 'manager':
            manager = instance.manager_profile
            data['phone_number'] = manager.phone_number if manager else None
        return data

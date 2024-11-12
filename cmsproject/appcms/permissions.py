# permissions.py
from rest_framework import permissions

class IsManager(permissions.BasePermission):
    """
    Custom permission to only allow Managers to upload documents.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

class IsSupervisor(permissions.BasePermission):
    """
    Custom permission to only allow Supervisors to view documents.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Supervisor').exists()

class IsManagerOrSupervisor(permissions.BasePermission):
    """
    Custom permission to allow both Managers and Supervisors to view documents,
    but only Managers can upload documents.
    """
    def has_permission(self, request, view):
        # Supervisors can view, Managers can upload and view
        if view.action == 'upload_document':
            return request.user.groups.filter(name='Manager').exists()
        elif view.action == 'get_project_documents':
            return request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Supervisor').exists()
        return False

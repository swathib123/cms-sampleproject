from django.urls import path
from .views import ManagerRegisterView, SupervisorRegisterView, CustomAuthToken, ProjectViewSet, TaskViewSet

urlpatterns = [
    path('register/manager/', ManagerRegisterView.as_view(), name='manager-register'),
    path('register/supervisor/', SupervisorRegisterView.as_view(), name='supervisor-register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('projects/', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),
    path('projects/<int:pk>/', ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='project-detail'),
    path('tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('tasks/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='task-detail'),
]

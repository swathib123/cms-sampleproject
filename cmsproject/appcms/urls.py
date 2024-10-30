from django.urls import path
from .views import (
    ManagerRegisterView,
    SupervisorRegisterView,
    CustomAuthToken,
    ProjectViewSet,
    TaskViewSet,
    UserDetailView
)

urlpatterns = [
    # User registration
    path('register/manager/', ManagerRegisterView.as_view(), name='manager-register'),
    path('register/supervisor/', SupervisorRegisterView.as_view(), name='supervisor-register'),

    # User login
    path('login/', CustomAuthToken.as_view(), name='login'),

    # User details for both manager and supervisor
    path('user/details/', UserDetailView.as_view(), name='user-details'),

    # Project endpoints
    path('projects/', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),
    path('projects/<int:pk>/', ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='project-detail'),

    # Task endpoints
    path('tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('tasks/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='task-detail'),
]
#end...
from django.urls import path
from .views import ManagerRegisterView, SupervisorRegisterView, ManagerProfileView, DocumentViewSet, CustomAuthToken, ProjectViewSet, TaskViewSet, ResourceViewSet, WorkerViewSet, MediaViewSet
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Register endpoints
    path('register/manager/', ManagerRegisterView.as_view(), name='manager-register'),
    path('register/supervisor/', SupervisorRegisterView.as_view(), name='supervisor-register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('profile/', ManagerProfileView.as_view(), name='manager-profile'),

    # Projects endpoints
    path('projects/', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),
    path('projects/<int:pk>/', ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='project-detail'),

    # Tasks endpoints
    path('tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('tasks/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='task-detail'),

    # Resources endpoints
    path('resources/', ResourceViewSet.as_view({'get': 'list', 'post': 'create'}), name='resource-list'),
    path('resources/<int:pk>/', ResourceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='resource-detail'),

    # Workers endpoints
    path('workers/', WorkerViewSet.as_view({'get': 'list', 'post': 'create'}), name='worker-list'),
    path('workers/<int:pk>/', WorkerViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='worker-detail'),

    # Documents endpoints
    path('documents/', DocumentViewSet.as_view({'get': 'list', 'post': 'create'}), name='document-list'),

    # Media upload endpoint (Custom action)
    path('media/upload/', MediaViewSet.as_view({'post': 'upload_media'}), name='upload-media'),
]

# Serve static files during development if DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ManagerViewSet, SupervisorViewSet, ProjectViewSet, TaskViewSet
 
router = DefaultRouter()
router.register(r'managers', ManagerViewSet)
router.register(r'supervisors', SupervisorViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
 
urlpatterns = [
    path('api/', include(router.urls)),
]
 
 
from .views import RegisterView, CustomAuthToken
 
urlpatterns += [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomAuthToken.as_view(), name='login'),
]
 
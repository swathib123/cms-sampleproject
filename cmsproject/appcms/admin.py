 
# Register your models here.
from django.contrib import admin
from .models import User, Manager, Supervisor, Project, Task
 
admin.site.register(User)
admin.site.register(Manager)
admin.site.register(Supervisor)
admin.site.register(Project)
admin.site.register(Task)
 
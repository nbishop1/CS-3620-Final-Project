from django.contrib import admin
from .models import Event, Task, TaskCompletion, UserProfile


admin.site.register(UserProfile)
admin.site.register(Event)
admin.site.register(Task)
admin.site.register(TaskCompletion)

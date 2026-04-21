from django.contrib import admin
from .models import Event, UserProfile


admin.site.register(UserProfile)
admin.site.register(Event)

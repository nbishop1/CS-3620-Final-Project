from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('tasks/new/', views.task_create_view, name='task-create'),
    path('events/new/', views.event_create_view, name='event-create'),
    path('notes/new/', views.note_create_view, name='note-create'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
]

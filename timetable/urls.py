from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'timetable'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('timetable/', views.timetable_view, name='timetable_view'),

    # Subject CRUD
    path('subject/add/', views.add_subject, name='add_subject'),
    path('subject/<int:subject_id>/edit/', views.edit_subject, name='edit_subject'),
    path('subject/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),

    # Class CRUD
    path('subject/<int:subject_id>/class/add/', views.add_class, name='add_class'),
    path('class/<int:class_id>/edit/', views.edit_class, name='edit_class'),
    path('class/<int:class_id>/delete/', views.delete_class, name='delete_class'),
]



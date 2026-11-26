from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Core Pages
    path('', views.dashboard_view, name='dashboard'),
    path('tasks/', views.task_list_view, name='task_list'),
    path('tasks/<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:task_id>/comment/', views.add_comment, name='add_comment'),
    path('planning/', views.planning_view, name='planning'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('messages/', views.messages_view, name='messages'),
    
    # Task Actions
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:task_id>/add-subtask/', views.add_subtask, name='add_subtask'),
    path('subtasks/<int:subtask_id>/toggle/', views.toggle_subtask, name='toggle_subtask'),

    # Planning Actions
    path('planning/milestone/create/', views.plan_milestone, name='plan_milestone'),
    path('planning/task/<int:task_id>/update-schedule/', views.update_task_schedule, name='update_task_schedule'),
]

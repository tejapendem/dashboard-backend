from django.urls import path
from .views import (
    TaskListCreate,
    MetricsView,
    create_task,
    dashboard_data,
    project_tasks,
    team_count,
    create_team,
    list_teams,
    update_task_status,
    update_task,
    get_all_tasks,
    team_members,
)
from . import views
urlpatterns = [
    path('tasks/', TaskListCreate.as_view(), name='task-list-create'),
    path('metrics/', MetricsView.as_view(), name='metrics'),

    
    path('dashboard/', dashboard_data, name='dashboard-data'),
    path('projects/', project_tasks, name='project-tasks'),

    ## Team-related URLs
    path('teams/count/', team_count, name='team-count'),
    path("teams/create/", create_team, name="create-team"),
    path("teams/all/", list_teams, name="list-teams"),
    path("<int:team_id>/delete/", views.delete_team, name='delete_team'),

    path('create/', create_task, name='create-task'),
    path("<int:task_id>/update_status/", update_task_status, name="update-task-status"),
    path("tasks/<int:task_id>/delete/", views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/update/', update_task, name='update-task'),
    path('all/', get_all_tasks, name='get_all_tasks'),
    
     path("teams/<int:team_id>/members/", team_members, name="team-members"),
]



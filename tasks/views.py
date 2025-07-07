from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db.models import Count
from datetime import date
from rest_framework.permissions import IsAuthenticated

from .models import Task, Project, Team, TaskLog
from .serializers import TaskSerializer, ProjectSerializer, TeamSerializer, TaskLogSerializer
from users.models import CustomUser
from .serializers import SimpleTeamSerializer
from .serializers import TaskSerializer, ProjectSerializer, TeamSerializer, TaskLogSerializer, SimpleTeamSerializer
from rest_framework import status, permissions
# ---------------------
# TASK CREATION & LIST
# ---------------------
class TaskListCreate(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        TaskLog.objects.create(user=self.request.user, task=task, action="created")


# ---------------------
# CREATE TASK API (used by frontend)
# ---------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        task = serializer.save(created_by=request.user)
        TaskLog.objects.create(user=request.user, task=task, action="created")
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# ---------------------
# METRICS VIEW (for Home)
# ---------------------
class MetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        active_users = CustomUser.objects.filter(is_active=True).count()
        tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status="completed").count()
        return Response({
            'active_users': active_users,
            'tasks': tasks,
            'tasks_completed': completed_tasks
        })


# ---------------------
# DASHBOARD DATA
# ---------------------
# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def dashboard_data(request):
#     user = request.user
#     now = timezone.now().date()

#     recent_logs = TaskLog.objects.filter(user=user).order_by('-timestamp')[:5]
#     today_tasks = Task.objects.filter(created_by=user, created_at__date=now)
#     expired_tasks = Task.objects.filter(created_by=user, due_date__lt=now, status__in=["working", "in_progress"])

#     return Response({
#         "recent_activity": TaskLogSerializer(recent_logs, many=True).data,
#         "today_tasks": TaskSerializer(today_tasks, many=True).data,
#         "expired_tasks": TaskSerializer(expired_tasks, many=True).data
#     })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    user = request.user
    today = date.today()

    recent_tasks = Task.objects.filter(created_by=user).order_by('-created_at')[:5]

    today_tasks = Task.objects.filter(created_by=user, due_date=today)
    
    # ✅ Corrected logic: tasks due today or earlier, and not marked completed
    expired_tasks = Task.objects.filter(
        created_by=user,
        due_date__lte=today,
    ).exclude(status='completed')

    return Response({
        "recent_activity": TaskSerializer(recent_tasks, many=True).data,
        "today_tasks": TaskSerializer(today_tasks, many=True).data,
        "expiring_tasks": TaskSerializer(expired_tasks, many=True).data
    })

# ---------------------
# PROJECT TASKS (status-wise)
# ---------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def project_tasks(request):
    user = request.user
    tasks = Task.objects.filter(created_by=user)

    return Response({
        'working': TaskSerializer(tasks.filter(status='working'), many=True).data,
        'in_progress': TaskSerializer(tasks.filter(status='in_progress'), many=True).data,
        'completed': TaskSerializer(tasks.filter(status='completed'), many=True).data,
    })

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_task_status(request, task_id):
    try:
        task = Task.objects.get(id=task_id, created_by=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['working', 'in_progress', 'completed']:
        return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

    task.status = new_status
    task.save()
    return Response({'message': 'Status updated successfully.'})

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, created_by=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Task updated successfully.',
            'task': serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_all_tasks(request):
    tasks = Task.objects.filter(created_by=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


# ---------------------
# TEAM COUNT VIEW (for Dashboard & Team page)
# ---------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def team_count(request):
    count = Team.objects.count()
    return Response({'team_count': count})


# ---------------------
# TEAM CREATION
# ---------------------
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def create_team(request):
#     serializer = TeamSerializer(data=request.data)
#     if serializer.is_valid():
#         team = serializer.save(created_by=request.user)
#         team.members.add(request.user)  # Add creator to team
#         return Response(serializer.data, status=201)
#     return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_team(request):
    serializer = TeamSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        team = serializer.save()
        return Response(TeamSerializer(team).data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_team(request, team_id):
    try:
        team = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)

    # Ensure only the creator can delete
    if team.created_by != request.user:
        return Response({'error': 'You are not authorized to delete this team.'}, status=status.HTTP_403_FORBIDDEN)

    team.delete()
    return Response({'message': 'Team deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, created_by=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found or unauthorized'}, status=404)

    task.delete()
    return Response({'message': 'Task deleted successfully'}, status=204)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_teams(request):
    teams = Team.objects.all()
    serializer = TeamSerializer(teams, many=True, context={'request': request})
    return Response(serializer.data)



from .serializers import CustomUserSerializer  # You'll define this below

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def team_members(request, team_id):
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return Response({"detail": "Team not found."}, status=404)

    members = team.members.all()
    serializer = CustomUserSerializer(members, many=True)
    return Response(serializer.data)
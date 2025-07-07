from rest_framework import serializers
from .models import Task, Project, Team, TaskLog
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'tags', 'status', 'due_date', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']




# class TeamSerializer(serializers.ModelSerializer):
#     members = serializers.PrimaryKeyRelatedField(
#         queryset=Team._meta.get_field('members').related_model.objects.all(),
#         many=True
#     )

#     class Meta:
#         model = Team
#         fields = ['id', 'name', 'members', 'created_by', 'created_at']
#         read_only_fields = ['created_by', 'created_at']

class TeamSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.CharField(),  # Expect list of usernames
        write_only=True
    )
    member_usernames = serializers.SerializerMethodField(read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)


    class Meta:
        model = Team
        fields = ['id', 'name', 'members', 'member_usernames', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def get_member_usernames(self, obj):
        return [user.username for user in obj.members.all()]

    def validate_members(self, usernames):
        """ Ensure all provided usernames exist """
        existing_usernames = set(User.objects.filter(username__in=usernames).values_list('username', flat=True))
        invalid_usernames = set(usernames) - existing_usernames
        if invalid_usernames:
            raise serializers.ValidationError(f"Invalid usernames: {', '.join(invalid_usernames)}")
        return usernames

    def create(self, validated_data):
        member_usernames = validated_data.pop('members', [])
        creator = self.context['request'].user

        team = Team.objects.create(name=validated_data['name'], created_by=creator)

        # Get valid users (already validated above)
        users = User.objects.filter(username__in=member_usernames)
        team.members.set(users)
        team.members.add(creator)

        return team

    
# New simplified serializer (used for teams list view)
class SimpleTeamSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    user = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'user', 'description']

    def get_description(self, obj):
        return f"Created by {obj.created_by.username}"

class TaskLogSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TaskLog
        fields = ['id', 'task', 'task_title', 'user', 'user_name', 'action', 'timestamp']
        read_only_fields = ['timestamp']


from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]
from rest_framework import serializers

from core.models import *
from user.serializers import CustomUserSerializer


class WorkspaceSerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer(read_only=True)

    class Meta:
        model = Workspace
        fields = "__all__"


class TeamMemberSerializer(serializers.ModelSerializer):
    member = CustomUserSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = "__all__"


class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Update
        fields = "__all__"


class MeetingParticipantSerializer(serializers.ModelSerializer):
    participant = CustomUserSerializer(read_only=True)

    class Meta:
        model = MeetingParticipant
        fields = "__all__"


class MeetingSerializer(serializers.ModelSerializer):
    meetingparticipant_set = MeetingParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = "__all__"


class ProjectMemberSerializer(serializers.ModelSerializer):
    member = CustomUserSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    projectmember_set = ProjectMemberSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = "__all__"


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = "__all__"


class TaskMemberSerializer(serializers.ModelSerializer):
    member = CustomUserSerializer(read_only=True)

    class Meta:
        model = TaskMember
        fields = "__all__"


class TaskDpendencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDpendency
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    dependecy_taksks = TaskDpendencySerializer(many=True, read_only=True)
    taskmember_set = TaskMemberSerializer(many=True, read_only=True)
    subtask_set = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = "__all__"

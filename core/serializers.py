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

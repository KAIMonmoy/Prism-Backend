from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

from core.serializers import *
from core.utils import send_email


class WorkspaceListCreate(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.all()

    def perform_create(self, serializer):
        # Create Workspace
        owner = self.request.user
        workspace = serializer.save(owner=owner)
        # Create Update
        update = Update()
        update.workspace = workspace
        update.message = f'{workspace.name} Created'
        update.save()
        # Save owner as admin TeamMember
        teammember = TeamMember()
        teammember.member = owner
        teammember.workspace = workspace
        teammember.role = 'admin'
        teammember.save()

    def list(self, request, *args, **kwargs):
        user = self.request.user
        user_workspaces = Workspace.objects.filter(
            id__in=TeamMember.objects.filter(member=user).values_list('workspace', flat=True)
        )
        serializer = WorkspaceSerializer(user_workspaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkspaceRole(generics.RetrieveAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        workspace = get_object_or_404(Workspace, pk=pk)
        if request.user == workspace.owner:
            return Response({'role': 'owner'}, status=status.HTTP_200_OK)
        if TeamMember.objects.filter(member=request.user, workspace=workspace).exists():
            member = TeamMember.objects.filter(member=request.user, workspace=workspace).first()
            return Response({"role": member.role}, status=status.HTTP_200_OK)
        else:
            return Response({"role": None}, status=status.HTTP_200_OK)


class WorkspaceRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        workspace = get_object_or_404(Workspace, pk=pk)
        if not TeamMember.objects.filter(member=request.user, workspace=workspace).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)

        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        workspace = get_object_or_404(Workspace, pk=pk)
        if request.user != workspace.owner:
            return Response({'error': 'Access restricted to workspace owner only'}, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        workspace = get_object_or_404(Workspace, pk=pk)
        if request.user != workspace.owner:
            return Response({'error': 'Access restricted to workspace owner only'}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamMemberListCreate(generics.ListCreateAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TeamMember.objects.all()

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        new_member_id = request.data.get("member")
        user = request.user
        workspace = get_object_or_404(Workspace, pk=pk)
        assigned_role = request.data.get('role', 'member')
        if assigned_role == 'admin' and user != workspace.owner:
            return Response({'error': 'Access restricted to workspace owner only'}, status=status.HTTP_403_FORBIDDEN)
        elif not TeamMember.objects.filter(member=user, workspace=workspace, role='admin').exists():
            return Response({'error': 'Access restricted to workspace admins only'}, status=status.HTTP_403_FORBIDDEN)
        new_member = get_object_or_404(PrismUser, pk=new_member_id)
        if TeamMember.objects.filter(member=new_member, workspace=workspace).exists():
            return Response({'error': 'Member already exists in the workspace'}, status=status.HTTP_400_BAD_REQUEST)

        teammember = TeamMember()
        teammember.member = new_member
        teammember.workspace = workspace
        teammember.role = assigned_role
        teammember.save()

        update = Update()
        update.workspace = workspace
        update.message = f'{new_member.first_name} {new_member.last_name} addeed to {workspace.name}'
        update.save()

        serializer = TeamMemberSerializer(teammember)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        workspace = get_object_or_404(Workspace, pk=pk)
        if not TeamMember.objects.filter(member=user, workspace=workspace).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)
        team_queryset = TeamMember.objects.filter(workspace=workspace)
        serializer = TeamMemberSerializer(team_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamMemberRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TeamMember.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not TeamMember.objects.filter(member=request.user, workspace=workspace).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)
        team_member = get_object_or_404(TeamMember, pk=pk)
        serializer = TeamMemberSerializer(team_member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if request.user != workspace.owner:
            return Response({'error': 'Access restricted to workspace owner only'}, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if request.user != workspace.owner:
            return Response({'error': 'Access restricted to workspace owner only'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()

        update = Update()
        update.workspace = workspace
        update.message = f'{instance.member.first_name} {instance.member.last_name} removed from {workspace.name}'
        update.save()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateList(generics.ListAPIView):
    serializer_class = UpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Update.objects.all()

    def list(self, request, **kwargs):
        pk = kwargs.get('pk')
        user = self.request.user
        workspace = get_object_or_404(Workspace, pk=pk)
        if not TeamMember.objects.filter(member=user, workspace=workspace).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)
        update_queryset = Update.objects.filter(workspace=workspace).order_by('-created')[:20]
        serializer = UpdateSerializer(update_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MeetingListCreate(generics.ListCreateAPIView):
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Meeting.objects.all()

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        workspace = get_object_or_404(Workspace, pk=pk)
        request.data['workspace'] = pk

        if not TeamMember.objects.filter(member=request.user, workspace=workspace, role='admin').exists():
            return Response({'error': 'Access restricted to workspace admins only'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MeetingSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
        else:
            return Response({'error': 'Invalid arguments for creating meeting'}, status=status.HTTP_400_BAD_REQUEST)

        update = Update()
        update.workspace = workspace
        update.message = f'Meeting - {instance.agenda} is schedueld for {str(instance.start_time).split("+")[0]} \
by {request.user.user_name}'
        update.save()

        participants = request.data.get('participants', None)

        if participants is not None:
            email_list = []
            for user_id in participants:
                try:
                    meeting_user = PrismUser.objects.get(pk=user_id)
                    if TeamMember.objects.filter(member=meeting_user, workspace=workspace).exists():
                        meetint_participant = MeetingParticipant()
                        meetint_participant.participant = meeting_user
                        meetint_participant.meeting = instance
                        meetint_participant.save()
                        email_list.append(meeting_user.email)
                except PrismUser.DoesNotExist:
                    print(f'{user_id} does not exist')

            send_email(
                recipients=email_list,
                subject=f"Meeting - {instance.agenda}",
                message="""
                <table style="min-width: 480px;">
                <thead>
                    <th colspan="2" style="font-size: 24px; padding: 20px;">Prism - Meeting</th>
                </thead>
                <tr>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">Agenda</td>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">"""
                        + instance.agenda + """</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">Time</td>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">"""
                        + str(instance.start_time) + """</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">Duration</td>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">"""
                        + str(instance.duration_mins) + """ Minutes</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">Link</td>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;"><a href="""
                        + '"' + instance.link + '"'
                        + """>""" + instance.link + """</a></td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">Inviter</td>
                    <td style="border: 1px solid #ccc; font-size: 18px; padding: 8px 20px;">"""
                        + request.user.user_name + """</td>
                </tr>
                </table>"""
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        workspace = get_object_or_404(Workspace, pk=pk)
        if not TeamMember.objects.filter(member=user, workspace=workspace).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)
        meeting_queryset = Meeting.objects.filter(workspace=workspace)
        serializer = MeetingSerializer(meeting_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MeetingRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Meeting.objects.all()

    def retrieve(self, request, *args, **kwargs):
        workspace_id = kwargs.get('workspace_id')
        user = request.user
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not TeamMember.objects.filter(member=user, workspace=workspace).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)
        meeting = get_object_or_404(Meeting, pk=kwargs.get('pk'))
        serializer = MeetingSerializer(meeting)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not TeamMember.objects.filter(member=request.user, workspace=workspace, role='admin').exists():
            return Response({'error': 'Access restricted to workspace admins only'}, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        print(instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        update = Update()
        update.workspace = workspace
        update.message = f'Meeting {serializer.data["agenda"]} updated by {request.user.user_name}'
        update.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not TeamMember.objects.filter(member=request.user, workspace=workspace, role='admin').exists():
            return Response({'error': 'Access restricted to workspace admins only'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()

        update = Update()
        update.workspace = workspace
        update.message = f'Meeting {instance.agenda} deleted by {request.user.user_name}'
        update.save()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeetingParticipantListCreate(generics.ListCreateAPIView):
    serializer_class = MeetingParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MeetingParticipant.objects.all()

    def list(self, request, *args, **kwargs):
        pk = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=pk)
        if not TeamMember.objects.filter(member=request.user, workspace=workspace).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)
        meeting_queryset = MeetingParticipant.objects.filter(meeting_id=kwargs.get('meeting_id'))
        serializer = MeetingParticipantSerializer(meeting_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=pk)
        if not TeamMember.objects.filter(member=request.user, workspace=workspace, role='admin').exists():
            return Response({'error': 'Access restricted to workspace admins only'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('participant', None)
        if user_id is None or not TeamMember.objects.filter(member_id=user_id, workspace=workspace).exists():
            return Response({'error': 'Invalid participant id'}, status=status.HTTP_400_BAD_REQUEST)

        meeting_id = kwargs.get('meeting_id')
        if MeetingParticipant.objects.filter(meeting_id=meeting_id, participant_id=user_id).exists():
            return Response({'error': 'Already added to the meeting'}, status=status.HTTP_400_BAD_REQUEST)

        meeting = get_object_or_404(Meeting, pk=meeting_id)
        user = get_object_or_404(PrismUser, pk=user_id)

        meeting_participant = MeetingParticipant()
        meeting_participant.meeting = meeting
        meeting_participant.participant = user
        meeting_participant.save()

        serializer = MeetingParticipantSerializer(meeting_participant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeetingParticipantDestroy(generics.DestroyAPIView):
    serializer_class = MeetingParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MeetingParticipant.objects.all()

    def destroy(self, request, *args, **kwargs):
        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)
        if not TeamMember.objects.filter(member=request.user, workspace=workspace, role='admin').exists():
            return Response({'error': 'Access restricted to workspace admins only'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectListCreate(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.all()

    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        workspace = get_object_or_404(Workspace, pk=pk)
        request.data['workspace'] = pk
        if not TeamMember.objects.filter(member=request.user, workspace=workspace, role='admin').exists():
            return Response({'error': 'Access restricted to workspace admins only'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
        else:
            return Response({'error': 'Invalid arguments for creating project'}, status=status.HTTP_400_BAD_REQUEST)

        update = Update()
        update.workspace = workspace
        update.message = f'Project {instance.name} created by {request.user.user_name}'
        update.save()

        if instance.is_private:
            members = request.data.get('members', None)
            if members is not None:
                for user_id in members:
                    try:
                        project_member_user = PrismUser.objects.get(pk=user_id)
                        if TeamMember.objects.filter(member=project_member_user, workspace=workspace).exists():
                            project_member = ProjectMember()
                            project_member.member = project_member_user
                            project_member.project = instance
                            project_member.save()
                    except PrismUser.DoesNotExist:
                        print(f'{user_id} does not exist')
            if members is None or request.user.id not in members:
                project_member = ProjectMember()
                project_member.member = request.user
                project_member.project = instance
                project_member.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        workspace = get_object_or_404(Workspace, pk=pk)
        if not TeamMember.objects.filter(member=user, workspace=workspace).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)
        project_queryset = Project.objects.filter(workspace=workspace) \
            .filter(Q(is_private=False) | Q(projectmember__member_id=user.id))
        serializer = ProjectSerializer(project_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        project = get_object_or_404(Project, pk=pk)
        if project.is_private:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        project = get_object_or_404(Project, pk=pk)
        if project.is_private:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        request_visibility = request.data.get("is_private", None)
        if not project.is_private and request_visibility is not None and request_visibility:
            return Response({'error': 'Public Project cannot be made Private'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        project = get_object_or_404(Project, pk=pk)
        if project.is_private:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)

        update = Update()
        update.workspace = project.workspace
        update.message = f'Project {project.name} deleted by {request.user.user_name}'
        update.save()

        instance = self.get_object()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMemberListCreate(generics.ListCreateAPIView):
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProjectMember.objects.all()

    def list(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)

        workspace_id = kwargs.get('workspace_id')
        if not TeamMember.objects.filter(member=request.user, workspace_id=workspace_id).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)

        if not project.is_private:
            return Response({"message": "All workspace members have access to public project"},
                            status=status.HTTP_200_OK)

        if not ProjectMember.objects.filter(project=project, member=request.user).exists():
            return Response({'error': 'Access restricted to project members only'}, status=status.HTTP_403_FORBIDDEN)

        member_queryset = ProjectMember.objects.filter(project=project)
        serializer = ProjectMemberSerializer(member_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)

        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)

        if not project.is_private:
            if not TeamMember.objects.filter(member=request.user, workspace=workspace, role='admin').exists():
                return Response({'error': 'Access restricted to workspace admins only'},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('member', None)
        if user_id is None or not TeamMember.objects.filter(member_id=user_id, workspace=workspace).exists():
            return Response({'error': 'Invalid member id'}, status=status.HTTP_400_BAD_REQUEST)

        if ProjectMember.objects.filter(project=project, member_id=user_id).exists():
            return Response({'error': 'Already added to the project'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(PrismUser, pk=user_id)

        project_member = ProjectMember()
        project_member.project = project
        project_member.member = user
        project_member.save()

        serializer = ProjectMemberSerializer(project_member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectMemberDestroy(generics.DestroyAPIView):
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProjectMember.objects.all()

    def destroy(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)

        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)

        if not project.is_private:
            if not TeamMember.objects.filter(member=request.user, workspace=workspace, role='admin').exists():
                return Response({'error': 'Access restricted to workspace admins only'},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListCreate(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.all()

    def create(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        request.data['project'] = project_id

        workspace_id = kwargs.get('workspace_id')
        workspace = get_object_or_404(Workspace, pk=workspace_id)

        if not project.is_private:
            if not TeamMember.objects.filter(member=request.user, workspace=workspace).exists():
                return Response({'error': 'Access restricted to workspace members only'},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)

        todo_task_count = Task.objects.filter(project=project, column='todo').aggregate(Count('id'))
        request.data['index'] = todo_task_count['id__count']

        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        update = Update()
        update.workspace = workspace
        update.message = f'Task {instance.name} for Project {project.name} created by {request.user.user_name}'
        update.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)

        workspace_id = kwargs.get('workspace_id')

        if not TeamMember.objects.filter(member=request.user, workspace_id=workspace_id).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)

        if project.is_private and not ProjectMember.objects.filter(project=project, member=request.user).exists():
            return Response({'error': 'Access restricted to project members only'}, status=status.HTTP_403_FORBIDDEN)

        task_queryset = Task.objects.filter(project=project).order_by('column', 'index')
        serializer = TaskSerializer(task_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.all()

    def retrieve(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)

        workspace_id = kwargs.get('workspace_id')
        task_id = kwargs.get('pk')

        if not TeamMember.objects.filter(member=request.user, workspace_id=workspace_id).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)

        if project.is_private:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)

        task = get_object_or_404(Task, pk=task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        request.data['project'] = project_id

        workspace_id = kwargs.get('workspace_id')

        task_id = kwargs.get('pk')
        task = get_object_or_404(Task, pk=task_id)

        if not TeamMember.objects.filter(member=request.user, workspace_id=workspace_id).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)

        if project.is_private:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)

        updated_column = request.data.get('column', None)
        updated_index = request.data.get('index', None)
        if updated_column is not None and task.column != updated_column and updated_index is None:
            task_column_index = Task.objects.filter(project=project, column=updated_column).aggregate(Count('id'))
            request.data['index'] = task_column_index['id__count']

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        task_name = request.data.get('name', instance.name)
        if updated_column is not None and task.column != updated_column:
            update = Update()
            update.workspace = project.workspace
            update.message = f'Task {task_name} moved from {task.column} to {updated_column} ' \
                             f'by {request.user.user_name}'
            update.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)

        workspace_id = kwargs.get('workspace_id')

        task_id = kwargs.get('pk')

        if not TeamMember.objects.filter(member=request.user, workspace_id=workspace_id).exists():
            return Response({'error': 'Access restricted to workspace members only'}, status=status.HTTP_403_FORBIDDEN)

        if project.is_private:
            if not ProjectMember.objects.filter(project=project, member=request.user).exists():
                return Response({'error': 'Access restricted to project members only'},
                                status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()

        update = Update()
        update.workspace = project.workspace
        update.message = f'Task {instance.name} deleted by {request.user.user_name}'
        update.save()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

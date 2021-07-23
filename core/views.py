from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from core.serializers import *


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

    def list(self, request, **kwargs):
        user = self.request.user
        user_workspaces = Workspace.objects.filter(
            id__in=TeamMember.objects.filter(member=user).values_list('workspace', flat=True)
        )
        serializer = WorkspaceSerializer(user_workspaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        print(serializer.data)
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
        update_queryset = Update.objects.filter(workspace=workspace).order_by('-created')
        serializer = UpdateSerializer(update_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

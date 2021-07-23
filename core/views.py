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

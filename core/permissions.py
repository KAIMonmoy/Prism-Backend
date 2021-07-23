from rest_framework.permissions import BasePermission

from core.models import *


class WorkspaceMemberRead(BasePermission):
    def has_object_permission(self, request, view, obj):
        pass


class WorkspaceMemberWrite(BasePermission):
    def has_object_permission(self, request, view, obj):
        pass


class WorkspaceAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        pass

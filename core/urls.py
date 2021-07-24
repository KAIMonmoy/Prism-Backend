from django.urls import path

from core.views import *


app_name = 'core'

urlpatterns = [
    path("", WorkspaceListCreate.as_view(), name="workspace-list-create"),
    path("<int:pk>/", WorkspaceRetrieveUpdateDelete.as_view(), name="workspace-detail"),
    path("<int:pk>/role/", WorkspaceRole.as_view(), name="workspace-role"),
    path("<int:pk>/team/", TeamMemberListCreate.as_view(), name="teammember-list-create"),
    path("<int:pk>/updates/", UpdateList.as_view(), name="update-list"),
    path("<int:workspace_id>/team/<int:pk>/", TeamMemberRetrieveUpdateDelete.as_view(), name="teammember-detail"),
    path("<int:pk>/meetings/", MeetingListCreate.as_view(), name="meeting-list-create"),
]


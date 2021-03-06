from django.urls import path

from core.views import *

app_name = 'core'

urlpatterns = [
    path("", WorkspaceListCreate.as_view(), name="workspace-list-create"),
    path("<int:pk>/", WorkspaceRetrieveUpdateDelete.as_view(), name="workspace-detail"),
    path("upload/", WorkspaceImageUpload.as_view(), name="workspace-image-upload"),
    path("<int:pk>/role/", WorkspaceRole.as_view(), name="workspace-role"),
    path("<int:pk>/team/", TeamMemberListCreate.as_view(), name="teammember-list-create"),
    path("<int:pk>/updates/", UpdateList.as_view(), name="update-list"),
    path("<int:workspace_id>/team/<int:pk>/", TeamMemberRetrieveUpdateDelete.as_view(), name="teammember-detail"),
    path("<int:pk>/meetings/", MeetingListCreate.as_view(), name="meeting-list-create"),
    path("<int:workspace_id>/meetings/<int:pk>/", MeetingRetrieveUpdateDelete.as_view(), name="meeting-detail"),
    path("<int:workspace_id>/meetings/<int:meeting_id>/participants/", MeetingParticipantListCreate.as_view(),
         name="participant-list-create"),
    path("<int:workspace_id>/meetings/<int:meeting_id>/participants/<int:pk>/", MeetingParticipantDestroy.as_view(),
         name="participant-destroy"),
    path("<int:pk>/projects/", ProjectListCreate.as_view(), name="project-list-create"),
    path("<int:workspace_id>/projects/<int:pk>/", ProjectRetrieveUpdateDelete.as_view(), name="project-detail"),
    path("<int:workspace_id>/projects/<int:project_id>/members/", ProjectMemberListCreate.as_view(),
         name="project-member-list-create"),
    path("<int:workspace_id>/projects/<int:project_id>/members/<int:pk>/", ProjectMemberDestroy.as_view(),
         name="project-member-destroy"),
    path("<int:workspace_id>/projects/<int:project_id>/tasks/", TaskListCreate.as_view(),
         name="task-list-create"),
    path("<int:workspace_id>/projects/<int:project_id>/tasks/<int:pk>/", TaskRetrieveUpdateDelete.as_view(),
         name="task-detail"),
    path("<int:workspace_id>/projects/<int:project_id>/tasks/<int:task_id>/members/", TaskMemberListCreate.as_view(),
         name="task-member-list-create"),
    path("<int:workspace_id>/projects/<int:project_id>/tasks/<int:task_id>/members/<int:pk>/",
         TaskMemberDestroy.as_view(), name="task-member-delete"),
    path("<int:workspace_id>/projects/<int:project_id>/tasks/<int:task_id>/dependency/",
         TaskDependencyListCreate.as_view(), name="task-dependency-list-create"),
    path("<int:workspace_id>/projects/<int:project_id>/tasks/<int:task_id>/dependency/<int:pk>/",
         TaskDependencyDestroy.as_view(), name="task-dependency-delete"),
    path("<int:workspace_id>/projects/<int:project_id>/tasks/<int:task_id>/subtasks/",
         SubTaskListCreate.as_view(), name="subtask-list-create"),
    path("<int:workspace_id>/projects/<int:project_id>/tasks/<int:task_id>/subtasks/<int:pk>/",
         SubTaskRetrieveUpdateDestroy.as_view(), name="subtask-detail"),
]

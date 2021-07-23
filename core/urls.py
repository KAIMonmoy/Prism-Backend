from django.urls import path

from core.views import *


app_name = 'core'

urlpatterns = [
    path("", WorkspaceListCreate.as_view(), name="workspace-list-create"),
    path("<int:pk>/", WorkspaceRetrieveUpdateDelete.as_view(), name="workspace-retriece-update-delete")
]

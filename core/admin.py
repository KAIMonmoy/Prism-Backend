from django.contrib import admin

from core.models import *


admin.site.register(Workspace)
admin.site.register(TeamMember)
admin.site.register(Update)
admin.site.register(Meeting)
admin.site.register(MeetingParticipant)
admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(Task)
admin.site.register(TaskMember)
admin.site.register(SubTask)
admin.site.register(TaskDpendency)

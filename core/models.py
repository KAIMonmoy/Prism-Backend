from django.db import models
from django.utils import timezone

from user.models import PrismUser


class Workspace(models.Model):
    WORKSPACE_TYPES = [
        ("personal", "Personal"),
        ("it_company", "IT Company"),
        ("ngo", "NGO"),
        ("government_office", "Government Office"),
        ("others", "Others"),
    ]
    name = models.CharField(max_length=127, unique=True)
    owner = models.ForeignKey(PrismUser, on_delete=models.CASCADE, blank=True)
    type = models.CharField(max_length=31, choices=WORKSPACE_TYPES, default="it_company")
    image = models.CharField(max_length=255, blank=True, null=True, default=None)

    def __str__(self):
        return self.name


class Update(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    message = models.CharField(max_length=1023)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.message


class TeamMember(models.Model):
    TEAMMEMBER_ROLES = [
        ("admin", "Admin"),
        ("member", "Member"),
    ]
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, blank=True)
    member = models.ForeignKey(PrismUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=31, choices=TEAMMEMBER_ROLES, default="member")

    def __str__(self):
        return self.workspace.name + " | " + self.member.user_name


class Meeting(models.Model):
    agenda = models.CharField(max_length=255)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, blank=True)
    link = models.URLField(blank=True, null=True)
    start_time = models.DateTimeField()
    duration_mins = models.PositiveIntegerField()

    def __str__(self):
        return self.agenda


class MeetingParticipant(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    participant = models.ForeignKey(PrismUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.meeting.agenda + " | " + self.participant.user_name


class Project(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, blank=True)
    is_private = models.BooleanField(default=False, blank=True)
    name = models.CharField(max_length=127)
    createad_at = models.DateTimeField(default=timezone.now, blank=True)
    is_archieved = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.workspace.name + " - " + self.name


class ProjectMember(models.Model):
    member = models.ForeignKey(PrismUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.project.name + " | " + self.member.user_name


class Task(models.Model):
    TASK_PRIORITIES = (
        ("high", "High"),
        ("mid", "Mid"),
        ("low", "Low"),
    )

    COLUMN_OPTIONS = (
        ("todo", "To Do"),
        ("doing", "Doing"),
        ("complete", "Complete"),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, default=None)
    column = models.CharField(max_length=15, choices=COLUMN_OPTIONS, default="todo")
    name = models.CharField(max_length=127)
    index = models.PositiveSmallIntegerField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now, blank=True, null=True)
    deadline = models.DateTimeField(default=None, blank=True, null=True)
    priority = models.CharField(max_length=15, choices=TASK_PRIORITIES, default="low")
    duration = models.PositiveSmallIntegerField(default=1, blank=True)

    def __str__(self):
        return self.name


class TaskMember(models.Model):
    member = models.ForeignKey(PrismUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, default=None)

    def __str__(self):
        return self.task.name + " | " + self.member.user_name


class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, default=None)
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name


class TaskDependency(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, blank=True, default=None, related_name='dependecy_taksks')
    dependency = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.dependency.name + " > " + self.task.name

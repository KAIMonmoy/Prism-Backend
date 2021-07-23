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
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    member = models.ForeignKey(PrismUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=31, choices=TEAMMEMBER_ROLES, default="member")

    def __str__(self):
        return self.workspace.name + " | " + self.member.user_name

# Generated by Django 3.2.5 on 2021-07-23 20:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_auto_20210723_1141'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agenda', models.CharField(max_length=255)),
                ('start_time', models.DateTimeField()),
                ('duration_mins', models.PositiveIntegerField()),
                ('workspace', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='core.workspace')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.meeting')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

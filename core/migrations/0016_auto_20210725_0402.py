# Generated by Django 3.2.5 on 2021-07-25 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_task_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='duration',
            field=models.PositiveSmallIntegerField(blank=True, default=1),
        ),
        migrations.AlterField(
            model_name='taskdependency',
            name='dependency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.task'),
        ),
        migrations.AlterField(
            model_name='taskdependency',
            name='task',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='dependecy_taksks', to='core.task'),
        ),
    ]

# Generated by Django 3.2.5 on 2021-07-23 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_updates'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Updates',
            new_name='Update',
        ),
        migrations.AlterField(
            model_name='workspace',
            name='name',
            field=models.CharField(max_length=127, unique=True),
        ),
    ]

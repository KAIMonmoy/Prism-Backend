# Generated by Django 3.2.5 on 2021-07-25 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_workspace_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workspace',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=''),
        ),
    ]

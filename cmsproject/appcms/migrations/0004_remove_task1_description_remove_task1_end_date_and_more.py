# Generated by Django 5.1.2 on 2024-11-06 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appcms', '0003_remove_project_manager'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task1',
            name='description',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='image',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='name',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='project_id',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='quantity_used',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='resource',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='supervisor_id',
        ),
        migrations.RemoveField(
            model_name='task1',
            name='worker',
        ),
    ]

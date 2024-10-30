# Generated by Django 5.0.7 on 2024-10-29 13:39

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcms', '0003_alter_task_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['start_date']},
        ),
        migrations.RenameField(
            model_name='task',
            old_name='deadline',
            new_name='end_date',
        ),
        migrations.RemoveField(
            model_name='task',
            name='phase',
        ),
        migrations.AddField(
            model_name='task',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='task_images/'),
        ),
        migrations.AddField(
            model_name='task',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='task',
            name='supervisor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='appcms.supervisor'),
        ),
    ]
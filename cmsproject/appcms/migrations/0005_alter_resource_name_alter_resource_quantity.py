# Generated by Django 5.1.2 on 2024-11-06 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcms', '0004_remove_task1_description_remove_task1_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='resource',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
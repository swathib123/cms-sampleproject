# Generated by Django 5.0.7 on 2024-11-13 05:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appcms', '0010_alter_document_document_type_media'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='worker',
            options={'verbose_name': 'Worker', 'verbose_name_plural': 'Workers'},
        ),
        migrations.AlterModelTable(
            name='worker',
            table='worker',
        ),
    ]

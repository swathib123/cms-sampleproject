# Generated by Django 5.0.7 on 2024-11-12 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcms', '0007_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='resource_type',
            field=models.CharField(choices=[('material', 'Material'), ('equipment', 'Equipment'), ('labor', 'Labor')], default='material', max_length=20),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_type',
            field=models.CharField(choices=[('blueprint', 'Blueprint'), ('contract', 'Contract'), ('inspection_report', 'Inspection Report'), ('video', 'Video'), ('image', 'Image')], max_length=20),
        ),
    ]

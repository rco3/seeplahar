# Generated by Django 5.0.6 on 2024-06-30 23:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('farm', '0003_planting_quantity_planting_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='related_item',
        ),
        migrations.AddField(
            model_name='event',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='object_id',
            field=models.UUIDField(default=1),
            preserve_default=False,
        ),
    ]

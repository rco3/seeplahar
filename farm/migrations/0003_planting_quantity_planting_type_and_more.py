# Generated by Django 5.0.6 on 2024-06-30 18:34

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0002_initial'),
        ('media', '0002_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='planting',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='planting',
            name='type',
            field=models.CharField(choices=[('mound', 'Mound'), ('row', 'Row'), ('raised_bed', 'Raised Bed'), ('container', 'Container'), ('pot', 'Pot')], default='container', max_length=50),
        ),
        migrations.AlterField(
            model_name='planting',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='plantings', to='media.photo'),
        ),
        migrations.AlterField(
            model_name='planting',
            name='source_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sourced_plantings', to='users.partner'),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customer')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='farm.location')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# Generated by Django 5.0.6 on 2024-05-28 21:32

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('species_name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('fruit', 'Fruit'), ('vegetable', 'Vegetable'), ('herb', 'Herb'), ('flower', 'Flower'), ('grass', 'Grass'), ('shrub', 'Shrub'), ('tree', 'Tree'), ('cactus', 'Cactus'), ('other', 'Other')], default='other', max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Variety',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('origin', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Synonym',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('taxon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='synonyms', to='taxon.taxon')),
            ],
        ),
    ]

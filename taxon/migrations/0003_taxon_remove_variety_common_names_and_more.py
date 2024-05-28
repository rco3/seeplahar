# Generated by Django 5.0.6 on 2024-05-28 21:09

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxon', '0002_commonname_variety_common_names'),
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
        migrations.RemoveField(
            model_name='variety',
            name='common_names',
        ),
        migrations.RemoveField(
            model_name='variety',
            name='species',
        ),
        migrations.AddField(
            model_name='variety',
            name='origin',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='variety',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='variety',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='variety',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name='Synonym',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('taxon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='synonyms', to='taxon.taxon')),
            ],
        ),
        migrations.DeleteModel(
            name='CommonName',
        ),
        migrations.DeleteModel(
            name='Species',
        ),
    ]

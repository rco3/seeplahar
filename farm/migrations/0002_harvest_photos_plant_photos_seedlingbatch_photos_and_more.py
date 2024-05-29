# Generated by Django 5.0.6 on 2024-05-29 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0001_initial'),
        ('taxon', '0002_photo_taxon_photos_variety_photos'),
    ]

    operations = [
        migrations.AddField(
            model_name='harvest',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='harvests', to='taxon.photo'),
        ),
        migrations.AddField(
            model_name='plant',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='plants', to='taxon.photo'),
        ),
        migrations.AddField(
            model_name='seedlingbatch',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='seedlingbatches', to='taxon.photo'),
        ),
        migrations.AddField(
            model_name='seedlot',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='seedlots', to='taxon.photo'),
        ),
    ]

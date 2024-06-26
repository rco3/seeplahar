# Generated by Django 5.0.6 on 2024-06-01 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxon', '0002_taxon_photos_variety_photos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characteristic',
            name='variety',
        ),
        migrations.AddField(
            model_name='characteristic',
            name='varieties',
            field=models.ManyToManyField(related_name='characteristics', to='taxon.variety'),
        ),
    ]

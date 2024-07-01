# Generated by Django 5.0.6 on 2024-06-30 18:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('media', '0002_initial'),
        ('taxon', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='characteristic',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customer'),
        ),
        migrations.AddField(
            model_name='synonym',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customer'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customer'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='taxons', to='media.photo'),
        ),
        migrations.AddField(
            model_name='synonym',
            name='taxon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='synonyms', to='taxon.taxon'),
        ),
        migrations.AddField(
            model_name='variety',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customer'),
        ),
        migrations.AddField(
            model_name='variety',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='varieties', to='media.photo'),
        ),
        migrations.AddField(
            model_name='variety',
            name='taxon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='varieties', to='taxon.taxon'),
        ),
        migrations.AddField(
            model_name='characteristic',
            name='varieties',
            field=models.ManyToManyField(related_name='characteristics', to='taxon.variety'),
        ),
    ]

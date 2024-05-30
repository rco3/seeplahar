# Generated by Django 5.0.6 on 2024-05-30 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxon', '0007_characteristic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxon',
            name='type',
            field=models.CharField(choices=[('fruit', 'Fruit'), ('vegetable', 'Vegetable'), ('herb', 'Herb'), ('flower', 'Flower'), ('grass', 'Grass'), ('shrub', 'Shrub'), ('tree', 'Tree'), ('succulent', 'Succulent'), ('annual', 'Annual'), ('perennial', 'Perennial'), ('other', 'Other')], default='other', max_length=50),
        ),
    ]

# Generated by Django 4.2 on 2024-08-22 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_tag_nfcproduct_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='nfcproduct',
            name='average_rating',
            field=models.FloatField(default=0),
        ),
    ]

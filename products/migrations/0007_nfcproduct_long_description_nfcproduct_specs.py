# Generated by Django 4.2 on 2024-08-22 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_nfcproduct_average_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='nfcproduct',
            name='long_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='nfcproduct',
            name='specs',
            field=models.JSONField(blank=True, null=True),
        ),
    ]

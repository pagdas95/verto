# Generated by Django 4.2 on 2024-08-22 17:48

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_nfcproduct_long_description_nfcproduct_specs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nfcproduct',
            name='long_description',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]

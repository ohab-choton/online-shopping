# Generated by Django 5.2.1 on 2025-05-15 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_variation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('color', 'Color'), ('size', 'Size')], max_length=100),
        ),
    ]

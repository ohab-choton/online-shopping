# Generated by Django 5.2.1 on 2025-05-29 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_orderproduct_payment_alter_payment_payment_method'),
        ('store', '0007_productvariant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='variation',
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='variation',
            field=models.ManyToManyField(blank=True, db_index=True, to='store.variation'),
        ),
    ]

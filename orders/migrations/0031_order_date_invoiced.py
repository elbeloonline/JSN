# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-08-18 17:55


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0030_auto_20180722_1845'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date_invoiced',
            field=models.DateField(blank=True, default=None),
        ),
    ]

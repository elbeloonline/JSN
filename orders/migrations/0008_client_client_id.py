# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-05 17:40


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20170122_2154'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='client_id',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]

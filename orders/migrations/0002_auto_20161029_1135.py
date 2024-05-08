# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-29 15:35


from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
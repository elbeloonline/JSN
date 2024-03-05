# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-01 18:20


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_auto_20180401_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='generated_reports',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.GeneratedReport'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-21 15:37


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_auto_20180401_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedreport',
            name='merged_report_filename',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

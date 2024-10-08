# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2021-11-07 18:11


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0035_auto_20181202_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedreport',
            name='num_state_hv_matches',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='generatedreport',
            name='state_hv_filename',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='searchname',
            name='high_value_search',
            field=models.BooleanField(default=False),
        ),
    ]

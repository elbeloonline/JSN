# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-05 02:21


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statereport', '0018_auto_20180305_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debt',
            name='docketed_judgment_seq_num',
            field=models.CharField(db_index=True, max_length=50),
        ),
    ]
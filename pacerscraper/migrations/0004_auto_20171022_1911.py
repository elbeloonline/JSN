# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-22 23:11


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pacerscraper', '0003_auto_20171022_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='pacerjudgmentindexcase',
            name='alias_file',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pacerjudgmentindexcase',
            name='case_summary_file',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pacerjudgmentindexcase',
            name='party_file',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]

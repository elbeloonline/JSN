# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-06 06:05


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20161029_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchname',
            name='address1',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='address2',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='company_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='company_type',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='first_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='last_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='name_qualifier',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='suffix',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='searchname',
            name='zip',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]

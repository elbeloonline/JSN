# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-13 16:13


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20161106_0105'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forenames',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('name_match', models.CharField(max_length=255)),
                ('score', models.DecimalField(decimal_places=0, max_digits=10)),
                ('deleted', models.CharField(max_length=1)),
                ('nickname', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'forenames',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Surnames',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('match', models.CharField(max_length=255)),
                ('score', models.DecimalField(decimal_places=0, max_digits=10)),
                ('deleted', models.CharField(max_length=1)),
                ('nickname', models.CharField(max_length=1)),
            ],
            options={
                'db_table': 'surnames',
                'managed': False,
            },
        ),
    ]

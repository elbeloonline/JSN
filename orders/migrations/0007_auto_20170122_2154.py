# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-23 02:54


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_forename_surname'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='forename',
            options={'managed': False, 'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='surname',
            options={'managed': False, 'ordering': ['name']},
        ),
    ]
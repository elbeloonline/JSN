# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-06-09 12:34


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patriot', '0002_auto_20180608_1458'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patriotprimname',
            old_name='alt_name',
            new_name='prim_name',
        ),
        migrations.RenameField(
            model_name='patriotprimname',
            old_name='alt_type',
            new_name='prim_type',
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-09-27 20:48


from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CJAliasDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_hash', models.CharField(max_length=255)),
            ],
        ),
    ]
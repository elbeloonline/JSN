# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-08-28 00:03


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statereport', '0020_party_merged_party_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='party_role_type_code',
            field=models.CharField(db_index=True, max_length=50),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-07-22 22:45


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0029_userclient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userclient',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.Client'),
        ),
        migrations.AlterField(
            model_name='userclient',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-01 17:33


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_generatedreports'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bankruptcy_filename', models.CharField(max_length=255)),
                ('usdc_filename', models.CharField(max_length=255)),
                ('state_filename', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='generatedreports',
            name='order',
        ),
        migrations.DeleteModel(
            name='GeneratedReports',
        ),
        migrations.AddField(
            model_name='order',
            name='generated_reports',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.GeneratedReport'),
        ),
    ]
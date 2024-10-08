# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-26 20:37


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statereport', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_number', models.CharField(max_length=50)),
                ('venue_id', models.CharField(max_length=50)),
                ('court_code', models.CharField(max_length=50)),
                ('report_request_number', models.CharField(max_length=50)),
                ('docketed_judgment_cc', models.CharField(max_length=50)),
                ('docketed_judgment_yy', models.CharField(max_length=50)),
                ('docketed_judgment_seq_num', models.CharField(max_length=50)),
                ('docketed_judgment_type_code', models.CharField(max_length=50)),
                ('debt_number', models.CharField(max_length=50)),
                ('record_type_code', models.CharField(max_length=50)),
                ('report_request_date', models.CharField(max_length=50)),
                ('report_from_date', models.CharField(max_length=50)),
                ('report_to_date', models.CharField(max_length=50)),
                ('record_type_code_data', models.CharField(max_length=50)),
                ('docketed_judgment_number', models.CharField(max_length=50)),
                ('nonacms_docket_number', models.CharField(max_length=50)),
                ('nonacms_venue_id', models.CharField(max_length=50)),
                ('nonacms_docket_type', models.CharField(max_length=50)),
                ('case_type_code', models.CharField(max_length=50)),
                ('case_title', models.CharField(max_length=55)),
                ('case_filed_date', models.CharField(max_length=50)),
                ('acms_docket_number', models.CharField(max_length=50)),
                ('acms_venue_id', models.CharField(max_length=50)),
                ('acms_court_code', models.CharField(max_length=50)),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-09-27 23:38


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pacerscraper', '0024_bankruptcyindexreport_5_pacerbankruptcyindexcase_5_pacerbankruptcyparty_5'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pacerbankruptcyindexcase_5',
            name='bankruptcy_index_report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pacerscraper.BankruptcyIndexReport_5'),
        ),
        migrations.AlterField(
            model_name='pacerbankruptcyparty_1',
            name='bankruptcy_index_case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pacerscraper.PacerBankruptcyIndexCase_1'),
        ),
        migrations.AlterField(
            model_name='pacerbankruptcyparty_2',
            name='bankruptcy_index_case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pacerscraper.PacerBankruptcyIndexCase_2'),
        ),
        migrations.AlterField(
            model_name='pacerbankruptcyparty_3',
            name='bankruptcy_index_case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pacerscraper.PacerBankruptcyIndexCase_3'),
        ),
        migrations.AlterField(
            model_name='pacerbankruptcyparty_4',
            name='bankruptcy_index_case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pacerscraper.PacerBankruptcyIndexCase_4'),
        ),
        migrations.AlterField(
            model_name='pacerbankruptcyparty_5',
            name='bankruptcy_index_case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pacerscraper.PacerBankruptcyIndexCase_5'),
        ),
    ]

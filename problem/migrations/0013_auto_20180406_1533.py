# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-06 07:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0012_auto_20180406_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='is_open_test_case',
            field=models.BooleanField(default=False, verbose_name='测试用例公开的题目'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='is_valid',
            field=models.BooleanField(default=False, verbose_name='有效题目'),
        ),
        migrations.AlterField(
            model_name='problem',
            name='vote_downs',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='problem',
            name='vote_ups',
            field=models.IntegerField(default=0),
        ),
    ]

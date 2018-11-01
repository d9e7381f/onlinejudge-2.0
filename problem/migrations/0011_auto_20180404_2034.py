# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-04 12:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0010_problem_spj_compile_ok'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='vote_downs',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='problem',
            name='vote_ups',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-27 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='ordinal',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]

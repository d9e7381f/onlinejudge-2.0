# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-26 07:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0009_contest_group'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contest',
            old_name='group',
            new_name='groups',
        ),
    ]
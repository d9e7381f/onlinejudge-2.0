# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-22 03:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='班级名称')),
                ('grade', models.IntegerField(verbose_name='年级')),
                ('major', models.CharField(max_length=100, verbose_name='专业名称')),
            ],
        ),
    ]
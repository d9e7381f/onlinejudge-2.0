# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-20 13:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collection', '0003_auto_20180331_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delegation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('read_time', models.DateTimeField(null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delegations', to='collection.Course')),
                ('delegates', models.ManyToManyField(related_name='jobs', to=settings.AUTH_USER_MODEL)),
                ('delegator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delegations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'delegation',
                'ordering': ('-create_time',),
            },
        ),
    ]
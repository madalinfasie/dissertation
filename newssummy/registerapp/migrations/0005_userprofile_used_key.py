# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-02 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registerapp', '0004_userpasschange'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='used_key',
            field=models.BooleanField(default=False),
        ),
    ]

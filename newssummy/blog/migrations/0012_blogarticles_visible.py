# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-27 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_auto_20170227_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogarticles',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]

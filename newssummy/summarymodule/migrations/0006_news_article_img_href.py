# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-19 10:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summarymodule', '0005_auto_20170118_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='article_img_href',
            field=models.CharField(default=None, max_length=250),
            preserve_default=False,
        ),
    ]

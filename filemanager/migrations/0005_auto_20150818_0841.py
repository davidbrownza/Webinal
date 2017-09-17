# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemanager', '0004_auto_20150818_0750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tab',
            name='LastSave',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

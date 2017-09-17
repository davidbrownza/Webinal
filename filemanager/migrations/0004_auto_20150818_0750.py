# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filemanager', '0003_auto_20150216_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('FilePath', models.TextField()),
                ('LastSave', models.DateTimeField()),
                ('User', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Tabs',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tab',
            unique_together=set([('User', 'FilePath')]),
        ),
        migrations.RemoveField(
            model_name='filemanagersettings',
            name='Key',
        ),
        migrations.RemoveField(
            model_name='filemanagersettings',
            name='Salt',
        ),
        migrations.AddField(
            model_name='filemanagersettings',
            name='AutoCompleteInd',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]

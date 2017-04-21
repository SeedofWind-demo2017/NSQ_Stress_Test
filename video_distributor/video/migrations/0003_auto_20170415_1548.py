# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0002_auto_20170408_1940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stats',
            name='name',
        ),
        migrations.RemoveField(
            model_name='stats',
            name='value',
        ),
        migrations.AddField(
            model_name='stats',
            name='consume_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='enque_time',
            field=models.DateTimeField(null=True),
        ),
    ]

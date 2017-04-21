# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0003_auto_20170415_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stats',
            name='consume_time',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='stats',
            name='enque_time',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='uuid',
            field=models.CharField(max_length=255),
        ),
    ]

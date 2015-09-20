# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wee_app', '0002_auto_20150920_0502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stop',
            name='timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
        ('wee_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='planneduberrequest',
            name='issued',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='planneduberrequest',
            name='product_id',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='planneduberrequest',
            name='session',
            field=models.ForeignKey(blank=True, to='sessions.Session', null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterUniqueTogether(
            name='planneduberrequest',
            unique_together=set([]),
        ),
    ]

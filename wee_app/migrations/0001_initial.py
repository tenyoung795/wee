# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('pcln_id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='PlannedUberRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('request_timestamp', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('destination', models.ForeignKey(to='wee_app.Point')),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('hotel', models.ForeignKey(to='wee_app.Hotel')),
                ('planned_uber_requests', models.ManyToManyField(to='wee_app.PlannedUberRequest')),
                ('stops', models.ManyToManyField(to='wee_app.Stop')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='point',
            unique_together=set([('latitude', 'longitude')]),
        ),
        migrations.AddField(
            model_name='planneduberrequest',
            name='destination',
            field=models.ForeignKey(related_name='+', to='wee_app.Point'),
        ),
        migrations.AddField(
            model_name='planneduberrequest',
            name='pickup',
            field=models.ForeignKey(related_name='+', to='wee_app.Point'),
        ),
        migrations.AddField(
            model_name='hotel',
            name='point',
            field=models.OneToOneField(to='wee_app.Point'),
        ),
        migrations.AlterUniqueTogether(
            name='stop',
            unique_together=set([('destination', 'timestamp')]),
        ),
        migrations.AlterUniqueTogether(
            name='planneduberrequest',
            unique_together=set([('pickup', 'destination', 'request_timestamp')]),
        ),
    ]

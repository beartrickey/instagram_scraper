# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag_date', models.DateField()),
                ('instagram_id', models.CharField(max_length=100)),
                ('image_url', models.URLField()),
                ('image_file', models.ImageField(null=True, upload_to=b'images', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('image_count', models.IntegerField(default=0)),
                ('checked_pages', models.IntegerField(default=0)),
                ('last_max_tag_id', models.CharField(max_length=100, null=True, blank=True)),
                ('last_modified_datetime', models.DateTimeField(auto_now=True, null=True)),
                ('job_start_datetime', models.DateTimeField(auto_now_add=True, null=True)),
                ('job_end_datetime', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='tag',
            field=models.ForeignKey(related_name='jobs', to='pixlee_app.Tag'),
        ),
        migrations.AddField(
            model_name='instagramcontent',
            name='tag',
            field=models.ForeignKey(related_name='instagram_content', to='pixlee_app.Tag'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-05 14:38
from __future__ import unicode_literals

import blog.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("blog", "0003_auto_20171105_1206")]

    operations = [
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("caption", models.CharField(max_length=255)),
                ("photo", models.ImageField(upload_to=blog.utils.FileUploader())),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="blog.Entry"
                    ),
                ),
            ],
        )
    ]

# Generated by Django 2.2.6 on 2019-12-29 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbs', '0005_auto_20191224_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='update_interval',
            field=models.IntegerField(default=3600, verbose_name='更新间隔（秒）'),
        ),
    ]
# Generated by Django 2.2.4 on 2019-09-11 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20190909_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bird',
            name='group',
            field=models.CharField(choices=[('EE', 'Eastern Empids')], max_length=6),
        ),
    ]

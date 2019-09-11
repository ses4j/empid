# Generated by Django 2.2.4 on 2019-09-09 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190906_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='guess',
            name='is_correct',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='guess',
            name='confidence',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='guess',
            name='species_code',
            field=models.CharField(help_text='Guessed species code.', max_length=6),
        ),
    ]

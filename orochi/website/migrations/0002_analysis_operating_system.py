# Generated by Django 3.0.5 on 2020-05-25 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='operating_system',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Linux'), (2, 'Windows'), (3, 'Mac'), (4, 'Other')], default=1),
        ),
    ]
# Generated by Django 2.1.5 on 2019-03-02 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190224_1545'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel',
            old_name='visible',
            new_name='connected',
        ),
    ]

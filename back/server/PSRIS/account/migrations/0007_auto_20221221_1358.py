# Generated by Django 4.1.3 on 2022-12-21 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_auto_20221221_0141'),
    ]

    operations = [
        migrations.RunSQL('ALTER SEQUENCE auth_user_id_seq RESTART WITH 1128;'),
        migrations.RunSQL('ALTER SEQUENCE account_profile_id_seq RESTART WITH 1129;')
    ]

# Generated by Django 4.1.3 on 2022-12-20 22:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20221221_0105'),
    ]

    operations = [
        migrations.RunSQL('ALTER SEQUENCE auth_user_id_seq RESTART WITH 1128;'),
        migrations.RunSQL('ALTER SEQUENCE account_profile_id_seq RESTART WITH 1129;')
    ]
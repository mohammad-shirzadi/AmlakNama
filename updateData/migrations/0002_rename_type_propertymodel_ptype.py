# Generated by Django 5.1.4 on 2025-01-07 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('updateData', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='propertymodel',
            old_name='type',
            new_name='ptype',
        ),
    ]

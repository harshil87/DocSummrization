# Generated by Django 4.2.6 on 2023-10-12 10:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('UserReport', '0002_rename_created_at_summarydata_upload_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='summarydata',
            old_name='Name',
            new_name='file_name',
        ),
    ]

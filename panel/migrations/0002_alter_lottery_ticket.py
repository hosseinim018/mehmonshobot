# Generated by Django 5.1.5 on 2025-02-03 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lottery',
            name='ticket',
            field=models.CharField(blank=True, default='975665d0', max_length=255, null=True),
        ),
    ]

# Generated by Django 5.1.5 on 2025-02-06 16:49

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0003_alter_admins_user_id_alter_lottery_ticket'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='gateway_transaction_id',
            new_name='authority',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='description',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='gateway_name',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='gateway_response',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='metadata',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='receiver_card_number',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='receiver_name',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='sender_card_number',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='sender_name',
        ),
        migrations.AlterField(
            model_name='lottery',
            name='ticket',
            field=models.CharField(blank=True, default='eb7bbf6b', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('VERIFIED', 'VERIFIED'), ('PAID', 'PAID'), ('IN_BANK', 'IN_BANK'), ('FAILED', 'FAILED'), ('REVERSED', 'REVERSED')], default='VERIFIED', max_length=10),
        ),
        migrations.AlterField(
            model_name='setting',
            name='payment_method',
            field=models.CharField(choices=[('card-to-card', 'card-to-card'), ('gateway', 'gateway')], default='card-to-card', max_length=20),
        ),
    ]

# Generated by Django 5.1.6 on 2025-04-17 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='business_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='business_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='business_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='business_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='business_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='mobile_money_network',
            field=models.CharField(blank=True, choices=[('MTN', 'MTN Mobile Money'), ('VODAFONE', 'Vodafone Cash'), ('AIRTELTIGO', 'AirtelTigo Money')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='paystack_subaccount_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='paystack_subaccount_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='paystack_subaccount_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

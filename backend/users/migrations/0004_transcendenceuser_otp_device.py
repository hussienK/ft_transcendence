# Generated by Django 4.2.16 on 2024-11-05 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('otp_totp', '0003_add_timestamps'),
        ('users', '0003_transcendenceuser_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='transcendenceuser',
            name='otp_device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='otp_totp.totpdevice'),
        ),
    ]
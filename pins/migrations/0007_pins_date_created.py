# Generated by Django 3.2.4 on 2021-07-11 08:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pins', '0006_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='pins',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
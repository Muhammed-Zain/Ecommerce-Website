# Generated by Django 4.1.7 on 2023-04-07 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_listing_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='time',
            field=models.CharField(default='Time', max_length=30),
        ),
    ]
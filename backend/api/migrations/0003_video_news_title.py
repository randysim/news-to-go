# Generated by Django 5.1.7 on 2025-04-20 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='news_title',
            field=models.TextField(null=True),
        ),
    ]

# Generated by Django 4.0.2 on 2022-02-04 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_profile_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='username',
            field=models.CharField(blank=True, default='user__username', editable=False, max_length=255, null=True),
        ),
    ]

# Generated by Django 4.0.2 on 2022-02-07 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcement', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='announcement',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='announcement',
            name='slug',
            field=models.SlugField(default='test-announcement', max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='announcement',
            name='thumbnail',
            field=models.ImageField(default='announcement/thumbnail/default.jpg', upload_to='announcement/thumbnail'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]

# Generated by Django 4.2.5 on 2023-10-28 07:10

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_post_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image_cover',
            field=models.ImageField(null=True, upload_to=main.models.upload_path),
        ),
    ]
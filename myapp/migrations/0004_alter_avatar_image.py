# Generated by Django 5.0.3 on 2024-05-05 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_blogs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='image',
            field=models.ImageField(default='avatars/pofile picture.png', upload_to='avatars/', verbose_name='Image'),
        ),
    ]
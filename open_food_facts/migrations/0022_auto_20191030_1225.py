# Generated by Django 2.2 on 2019-10-30 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_food_facts', '0021_auto_20191030_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(max_length=400, unique=True, upload_to=''),
        ),
    ]
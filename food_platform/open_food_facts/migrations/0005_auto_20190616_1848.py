# Generated by Django 2.2 on 2019-06-16 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_food_facts', '0004_auto_20190616_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='score',
            field=models.CharField(max_length=1),
        ),
    ]
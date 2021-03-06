# Generated by Django 2.2 on 2019-07-13 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_food_facts', '0010_product_score_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.AddField(
            model_name='category',
            name='products',
            field=models.ManyToManyField(to='open_food_facts.Product'),
        ),
        migrations.AddField(
            model_name='user',
            name='substitutes',
            field=models.ManyToManyField(to='open_food_facts.Product'),
        ),
        migrations.DeleteModel(
            name='Substitute',
        ),
    ]

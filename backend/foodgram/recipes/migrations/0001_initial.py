# Generated by Django 2.2.19 on 2022-12-26 12:30

from django.db import migrations, models
import recipes.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('color', models.CharField(default='#E26C2D', max_length=7)),
                ('slug', models.SlugField(max_length=200, unique=True, validators=[recipes.validators.validate_slug])),
            ],
        ),
    ]

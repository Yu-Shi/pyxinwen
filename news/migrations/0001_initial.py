# Generated by Django 2.1.1 on 2018-09-11 08:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPiece',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news_title', models.CharField(max_length=200)),
                ('news_content', models.CharField(max_length=10000)),
                ('pub_date', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('newspiece', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', related_query_name='tag', to='news.NewsPiece')),
            ],
        ),
    ]

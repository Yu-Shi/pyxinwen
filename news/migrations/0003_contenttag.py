# Generated by Django 2.1.1 on 2018-09-13 03:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20180912_1726'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('newspiece', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.NewsPiece')),
            ],
        ),
    ]

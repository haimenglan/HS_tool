# Generated by Django 4.1.1 on 2022-09-10 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HS_server', '0002_hardware_doc'),
    ]

    operations = [
        migrations.CreateModel(
            name='English_doc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('path', models.CharField(default='', max_length=100)),
                ('format', models.CharField(default='', max_length=10)),
                ('order_id', models.IntegerField(blank=True, null=True)),
                ('is_secret', models.BooleanField(default=False)),
                ('is_delete', models.BooleanField(default=False)),
            ],
        ),
    ]

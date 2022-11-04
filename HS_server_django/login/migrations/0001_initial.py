# Generated by Django 4.0.3 on 2022-08-17 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=30)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('ip', models.CharField(blank=True, max_length=20, null=True)),
                ('port', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('is_online', models.BinaryField(blank=True, default=b'0', max_length=1, null=True)),
                ('photo', models.CharField(blank=True, max_length=200, null=True)),
                ('sign', models.CharField(blank=True, max_length=200, null=True)),
                ('birthday', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('phone', models.CharField(blank=True, max_length=30, null=True)),
                ('mail', models.CharField(blank=True, max_length=50, null=True)),
                ('is_delete', models.BinaryField(blank=True, default=b'0', max_length=1, null=True)),
                ('cookie', models.CharField(blank=True, max_length=100, null=True)),
                ('fd_file', models.IntegerField(blank=True, null=True)),
                ('connect_time', models.CharField(blank=True, max_length=25, null=True)),
                ('internal_server_port', models.SmallIntegerField(blank=True, null=True)),
                ('internal_port', models.SmallIntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'contact',
            },
        ),
    ]

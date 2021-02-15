# Generated by Django 3.1.6 on 2021-02-15 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lumber', '0002_auto_20210213_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='created',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='funcname',
            field=models.CharField(db_index=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='level',
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='lineno',
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='message',
            field=models.TextField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='msg',
            field=models.TextField(db_index=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='name',
            field=models.CharField(db_index=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='pathname',
            field=models.CharField(db_index=True, max_length=1024),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='process',
            field=models.PositiveIntegerField(blank=True, db_index=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='thread',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, default=None, null=True),
        ),
    ]
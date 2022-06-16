# Generated by Django 3.2.7 on 2022-05-23 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Check_In',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('reservation_no', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=255)),
                ('arrival_date', models.DateField()),
                ('departure_date', models.DateField()),
                ('room_type', models.CharField(max_length=100)),
                ('room_no', models.CharField(max_length=100)),
                ('selfie_image', models.ImageField(upload_to='')),
                ('submit_date_time', models.DateTimeField()),
            ],
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_userdirectorymeta'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('role', models.CharField(max_length=100)),
                ('purpose', models.TextField()),
                ('preferred_date', models.DateField()),
                ('preferred_time', models.TimeField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'dashboard_meeting_request',
            },
        ),
    ]

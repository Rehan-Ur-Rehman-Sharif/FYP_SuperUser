from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDirectoryMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_kind', models.CharField(max_length=50)),
                ('source_id', models.PositiveIntegerField()),
                ('role', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], default='offline', max_length=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'dashboard_user_meta',
                'unique_together': {('user_kind', 'source_id')},
            },
        ),
    ]

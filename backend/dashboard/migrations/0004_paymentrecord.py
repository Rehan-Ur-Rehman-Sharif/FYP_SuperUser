from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_meetingrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('role', models.CharField(max_length=100)),
                ('amount', models.PositiveIntegerField()),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('Paid', 'Paid'), ('Pending', 'Pending'), ('Overdue', 'Overdue')], default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'dashboard_payment_record',
            },
        ),
    ]

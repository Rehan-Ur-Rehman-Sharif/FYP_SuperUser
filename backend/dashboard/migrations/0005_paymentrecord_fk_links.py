from django.db import migrations, models
import django.db.models.deletion


def backfill_payment_admin_links(apps, schema_editor):
    PaymentRecord = apps.get_model('dashboard', 'PaymentRecord')
    OrganizationAdmin = apps.get_model('dashboard', 'OrganizationAdmin')
    EventAdmin = apps.get_model('dashboard', 'EventAdmin')

    for payment in PaymentRecord.objects.all():
        role = (payment.role or '').strip().lower()

        if role == 'admin':
            org_admin = OrganizationAdmin.objects.filter(
                email__iexact=payment.email,
                management__Management_name__iexact=payment.organization,
            ).first()
            if org_admin is None:
                org_admin = OrganizationAdmin.objects.filter(
                    email__iexact=payment.email,
                ).first()
            if org_admin:
                payment.organization_admin_id = org_admin.id

        elif role == 'event admin':
            event_admin = EventAdmin.objects.filter(
                email__iexact=payment.email,
                organization__iexact=payment.organization,
            ).first()
            if event_admin is None:
                event_admin = EventAdmin.objects.filter(
                    email__iexact=payment.email,
                ).first()
            if event_admin:
                payment.event_admin_id = event_admin.id

        payment.save(update_fields=['organization_admin_id', 'event_admin_id'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_paymentrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrecord',
            name='event_admin',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='dashboard.eventadmin'),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='organization_admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='dashboard.organizationadmin'),
        ),
        migrations.RunPython(backfill_payment_admin_links, noop_reverse),
    ]

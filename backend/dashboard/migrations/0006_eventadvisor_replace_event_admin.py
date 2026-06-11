from django.conf import settings
from django.db import migrations, models
from django.utils import timezone
import django.db.models.deletion


def noop_reverse(apps, schema_editor):
    pass


def prune_events_event_event_admin_refs(apps, schema_editor):
    conn = schema_editor.connection
    cursor = conn.cursor()
    tables = conn.introspection.table_names(cursor)
    if 'events_event' not in tables:
        return
    cols = [col[0] for col in conn.introspection.get_table_description(cursor, 'events_event')]
    if 'event_admin_id' not in cols:
        return
    cursor.execute('UPDATE events_event SET event_admin_id = NULL')


def ensure_eventadvisor_table_and_import_event_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    conn = schema_editor.connection
    cursor = conn.cursor()
    tables = conn.introspection.table_names(cursor)

    if 'events_eventadvisor' not in tables:
        if conn.vendor == 'postgresql':
            cursor.execute(
                '''
                CREATE TABLE "events_eventadvisor" (
                    "id" bigserial NOT NULL PRIMARY KEY,
                    "name" varchar(200) NOT NULL,
                    "created_at" timestamp with time zone NOT NULL,
                    "user_id" bigint NOT NULL UNIQUE REFERENCES "auth_user" ("id")
                )
                '''
            )
        else:
            cursor.execute(
                '''
                CREATE TABLE "events_eventadvisor" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "name" varchar(200) NOT NULL,
                    "created_at" datetime NOT NULL,
                    "user_id" bigint NOT NULL UNIQUE REFERENCES "auth_user" ("id")
                )
                '''
            )

    if 'event_admin' not in tables:
        return

    cursor.execute('SELECT id, name, email, created_at FROM event_admin')
    rows = cursor.fetchall()

    for _ea_id, name, email, created_at in rows:
        email = (email or '').strip()
        if not email:
            continue

        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            user = User.objects.filter(username__iexact=email).first()

        if user is None:
            import secrets

            user = User.objects.create_user(
                username=email,
                email=email,
                password=secrets.token_urlsafe(32),
            )
        else:
            if user.email != email:
                user.email = email
                user.save(update_fields=['email'])

        cursor.execute(
            'SELECT 1 FROM events_eventadvisor WHERE user_id = %s',
            [user.pk],
        )
        if cursor.fetchone():
            continue

        ts = created_at or timezone.now()
        cursor.execute(
            'INSERT INTO events_eventadvisor (name, created_at, user_id) VALUES (%s, %s, %s)',
            [name or email, ts, user.pk],
        )


def backfill_payment_event_advisor(apps, schema_editor):
    PaymentRecord = apps.get_model('dashboard', 'PaymentRecord')
    conn = schema_editor.connection
    cursor = conn.cursor()
    tables = conn.introspection.table_names(cursor)
    if 'event_admin' not in tables:
        return

    for pr in PaymentRecord.objects.exclude(event_admin_id=None).iterator():
        cursor.execute(
            '''
            SELECT ea.id
            FROM events_eventadvisor ea
            INNER JOIN auth_user u ON u.id = ea.user_id
            INNER JOIN event_admin e ON e.id = %s
            WHERE LOWER(COALESCE(e.email, '')) = LOWER(COALESCE(u.email, ''))
            ''',
            [pr.event_admin_id],
        )
        row = cursor.fetchone()
        if row:
            PaymentRecord.objects.filter(pk=pr.pk).update(event_advisor_id=row[0])


def rewrite_user_meta_kind(apps, schema_editor):
    UserDirectoryMeta = apps.get_model('dashboard', 'UserDirectoryMeta')
    UserDirectoryMeta.objects.filter(user_kind='event_admin').update(user_kind='event_advisor')


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0005_paymentrecord_fk_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdirectorymeta',
            name='account_status',
            field=models.CharField(
                choices=[('active', 'active'), ('inactive', 'inactive')],
                default='active',
                max_length=10,
            ),
        ),
        migrations.RunPython(ensure_eventadvisor_table_and_import_event_admin, noop_reverse),
        migrations.RunPython(prune_events_event_event_admin_refs, noop_reverse),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='EventAdvisor',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        (
                            'user',
                            models.OneToOneField(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='event_advisor',
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        'db_table': 'events_eventadvisor',
                        'managed': False,
                    },
                ),
            ],
            database_operations=[],
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='event_advisor',
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payments',
                to='dashboard.eventadvisor',
            ),
        ),
        migrations.RunPython(backfill_payment_event_advisor, noop_reverse),
        migrations.RemoveField(
            model_name='paymentrecord',
            name='event_admin',
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='EventAdmin'),
            ],
            database_operations=[],
        ),
        migrations.RunSQL('DROP TABLE IF EXISTS event_admin;', migrations.RunSQL.noop),
        migrations.RunPython(rewrite_user_meta_kind, noop_reverse),
    ]

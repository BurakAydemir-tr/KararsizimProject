"""Django-owned tables stay private even if the Data API is re-enabled."""

from django.db import migrations

TABLES = (
    "accounts_user", "accounts_user_groups", "accounts_user_user_permissions",
    "auth_group", "auth_group_permissions", "auth_permission", "django_admin_log",
    "django_content_type", "django_migrations", "django_session",
)


def protect_internal_tables(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        raise RuntimeError("Bu migration PostgreSQL gerektirir.")
    quote = schema_editor.quote_name
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT rolname FROM pg_roles WHERE rolname IN (%s, %s, %s)",
            ["anon", "authenticated", "service_role"],
        )
        roles = ["PUBLIC"] + [quote(row[0]) for row in cursor.fetchall()]
    recipients = ", ".join(roles)
    for table in TABLES:
        qualified = f'{quote("public")}.{quote(table)}'
        # The owner (Django's DB role) can still use ORM. API roles cannot.
        schema_editor.execute(f"ALTER TABLE {qualified} ENABLE ROW LEVEL SECURITY")
        schema_editor.execute(f"REVOKE ALL PRIVILEGES ON TABLE {qualified} FROM {recipients}")
        if table != "django_session":
            sequence = f'{quote("public")}.{quote(table + "_id_seq")}'
            schema_editor.execute(f"REVOKE ALL PRIVILEGES ON SEQUENCE {sequence} FROM {recipients}")

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        # Reversing this migration must not silently restore public access.
        migrations.RunPython(protect_internal_tables, reverse_code=migrations.RunPython.noop),
    ]

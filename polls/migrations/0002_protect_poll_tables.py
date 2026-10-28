from django.db import migrations


def protect_tables(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        raise RuntimeError("Bu migration PostgreSQL gerektirir.")
    quote = schema_editor.quote_name
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT rolname FROM pg_roles WHERE rolname IN ('anon','authenticated','service_role')")
        roles = ["PUBLIC"] + [quote(row[0]) for row in cursor.fetchall()]
    recipients = ", ".join(roles)
    for table in ("polls_poll", "polls_choice", "polls_vote"):
        target = f'{quote("public")}.{quote(table)}'
        schema_editor.execute(f"ALTER TABLE {target} ENABLE ROW LEVEL SECURITY")
        schema_editor.execute(f"REVOKE ALL PRIVILEGES ON TABLE {target} FROM {recipients}")
        sequence = f'{quote("public")}.{quote(table + "_id_seq")}'
        schema_editor.execute(f"REVOKE ALL PRIVILEGES ON SEQUENCE {sequence} FROM {recipients}")


class Migration(migrations.Migration):
    dependencies = [("polls", "0001_initial")]
    operations = [migrations.RunPython(protect_tables, reverse_code=migrations.RunPython.noop)]

"""Consistent, local application-only logical backup; no credentials in output."""
import gzip
import hashlib
import io
import json
import os
import uuid
from pathlib import Path

from django.apps import apps
from django.core import serializers
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Uygulama tablolarını tutarlı gzip JSON yedeğine alır; oturum/hız/hata/admin günlüklerini içermez."

    def add_arguments(self, parser):
        parser.add_argument("--directory", default=".backups")

    def handle(self, *args, **options):
        directory = Path(options["directory"]).resolve()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = directory / ("application-" + timezone.now().strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8] + ".json.gz")
        labels = ["contenttypes.ContentType", "auth.Permission", "auth.Group", "accounts.User",
                  "polls.Poll", "polls.Choice", "polls.Vote"]
        manifest = {"format": 1, "created_at": timezone.now().isoformat()}
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                if "polls_report" in connection.introspection.table_names():
                    labels.append("polls.Report")
                manifest["counts"] = {label.lower(): apps.get_model(label).objects.count() for label in labels}
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb") as compressed:
                    with io.TextIOWrapper(compressed, encoding="utf-8") as output:
                        # Match current DB columns, so an additive pending migration
                        # can be backed up before deploying its new model fields.
                        output.write("[")
                        first = True
                        for label in labels:
                            model = apps.get_model(label)
                            with connection.cursor() as cursor:
                                columns = {column.name for column in connection.introspection.get_table_description(cursor, model._meta.db_table)}
                            fields = [field.name for field in model._meta.concrete_fields if field.column in columns]
                            fields += [field.name for field in model._meta.many_to_many]
                            concrete = [field.name for field in model._meta.concrete_fields if field.column in columns]
                            encoded = serializers.serialize("json", model.objects.only(*concrete).order_by("pk"), fields=fields)[1:-1]
                            if encoded.strip():
                                if not first:
                                    output.write(",")
                                output.write(encoded)
                                first = False
                        output.write("]")
            manifest["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            metadata = path.with_suffix(path.suffix + ".manifest.json")
            with os.fdopen(os.open(metadata, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as output:
                json.dump(manifest, output, indent=2)
        except Exception as error:
            path.unlink(missing_ok=True)
            raise CommandError(f"Yedek oluşturulamadı ({type(error).__name__}); gizli değerler gösterilmedi.") from None
        self.stdout.write(str(path))

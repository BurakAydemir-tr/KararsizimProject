"""Restore only into a newly created, unique disposable database."""
import copy
import hashlib
import json
import gzip
import uuid
from pathlib import Path

import psycopg
from psycopg import sql
from django.apps import apps
from django.core.management import call_command
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from config.environment import database, env


class Command(BaseCommand):
    help = "Yedeği yeni restorecheck_<rastgele> DB'ye geri yükler, sayımları doğrular ve sadece o DB'yi kaldırır."

    def add_arguments(self, parser):
        parser.add_argument("backup")

    def handle(self, *args, **options):
        path = Path(options["backup"]).resolve()
        manifest = json.loads(path.with_suffix(path.suffix + ".manifest.json").read_text())
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"]:
            raise CommandError("Yedek checksum doğrulanamadı; geri yükleme yapılmadı.")
        config = database("DATABASE_TEST_ADMIN_URL" if env.str("DATABASE_TEST_ADMIN_URL", default="") else "DATABASE_MIGRATION_URL")
        if config["HOST"].endswith(".pooler.supabase.com") and config["USER"].startswith("postgres."):
            config.update(HOST="db." + config["USER"].split(".", 1)[1] + ".supabase.co", USER="postgres", PORT=5432)
        dbname = "restorecheck_" + uuid.uuid4().hex
        kwargs = dict(host=config["HOST"], port=config["PORT"], user=config["USER"], password=config["PASSWORD"],
                      dbname=config["NAME"], **config["OPTIONS"])
        kwargs.pop("prepare_threshold", None)
        created = False
        try:
            with psycopg.connect(**kwargs, autocommit=True) as admin:
                admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
                created = True
                restored = copy.deepcopy(connections["default"].settings_dict)
                restored.update(config)
                restored["NAME"] = dbname
                connections.databases["restorecheck"] = restored
                try:
                    call_command("migrate", database="restorecheck", interactive=False, verbosity=0)
                    # Fresh migrations generate metadata; restore the snapshot's
                    # exact metadata instead of leaving new-version extra rows.
                    apps.get_model("auth.Permission").objects.using("restorecheck").all().delete()
                    apps.get_model("contenttypes.ContentType").objects.using("restorecheck").all().delete()
                    call_command("loaddata", str(path), database="restorecheck", verbosity=0)
                    counts = {label: apps.get_model(label).objects.using("restorecheck").count() for label in manifest["counts"]}
                    if counts != manifest["counts"]:
                        raise ValueError("Restored row counts differ")
                    with gzip.open(path, "rt", encoding="utf-8") as source:
                        for record in json.load(source):
                            model = apps.get_model(record["model"])
                            obj = model.objects.using("restorecheck").get(pk=record["pk"])
                            actual = json.loads(serializers.serialize("json", [obj], fields=record["fields"].keys()))[0]["fields"]
                            expected = record["fields"]
                            for field in model._meta.many_to_many:
                                if field.name in actual:
                                    actual[field.name] = sorted(actual[field.name])
                                    expected[field.name] = sorted(expected[field.name])
                            if actual != expected:
                                raise ValueError("Restored field values differ")
                    self.stdout.write("PASS: checksum, migration, gerçek geri yükleme ve tüm tablo sayımları doğrulandı.")
                finally:
                    connections["restorecheck"].close()
                    del connections["restorecheck"]
                    connections.databases.pop("restorecheck", None)
                    admin.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(dbname)))
                    created = False
        except Exception as error:
            suffix = " Geçici DB kontrol edilmeli: " + dbname if created else ""
            raise CommandError(f"Geri yükleme doğrulanamadı ({type(error).__name__})." + suffix) from None

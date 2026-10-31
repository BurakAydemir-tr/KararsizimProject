import re
import time
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "14 günü geçen uygulama yedeklerini listeler; silmek için --apply gerekir."

    def add_arguments(self, parser):
        parser.add_argument("--directory", default=".backups")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        directory = Path(options["directory"]).resolve()
        count = 0
        for path in directory.glob("application-*.json.gz"):
            if path.is_symlink() or not re.fullmatch(r"application-\d{8}T\d{6}Z-[0-9a-f]{8}\.json\.gz", path.name):
                continue
            if path.stat().st_mtime >= time.time() - 14 * 86400:
                continue
            count += 1
            if options["apply"]:
                path.unlink()
                path.with_suffix(path.suffix + ".manifest.json").unlink(missing_ok=True)
        self.stdout.write(f"14 günü geçen yedek: {count}; " + ("silindi" if options["apply"] else "yalnızca plan, silinmedi"))

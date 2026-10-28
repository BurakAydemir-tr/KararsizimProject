"""Opt-in sample content for a separate development database only."""
import hashlib

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from accounts.models import User
from polls.models import Poll
from polls.services import cast_vote, create_poll, manage_poll


class Command(BaseCommand):
    help = "Ayrı demo DB için örnek anketler. Varsayılan yalnızca planı gösterir."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Örnekleri gerçekten oluştur.")

    def handle(self, *args, **options):
        if not options["apply"]:
            self.stdout.write("Plan: giriş yapamayan demo kullanıcı, 2 açık ve 1 kapalı anket. Veri yazılmadı.")
            return
        name = connection.settings_dict["NAME"]
        if not settings.DEBUG or not (name.endswith("_demo") or name.startswith("test_kararsizim_")):
            raise CommandError("Yalnızca DEBUG=true ve adı _demo ile biten ayrı DB'de çalışır. Uygulama DB'sine örnek yüklenmedi.")
        examples = [
            ("Bu akşam sinemaya mı, restorana mı gidelim?", ["Sinema", "Restoran"], False),
            ("Hafta sonu hangi etkinliği seçelim?", ["Müze", "Yürüyüş", "Konser"], False),
            ("Birlikte hangi filmi izleyelim?", ["Komedi", "Bilim kurgu"], True),
        ]
        with transaction.atomic():
            user = User.objects.filter(username="kararsizim_demo").first()
            if user is None:
                user = User.objects.create_user("kararsizim_demo", "demo@example.invalid", password=None)
            elif user.email != "demo@example.invalid" or user.has_usable_password():
                raise CommandError("Demo kullanıcı adı başka bir hesaba ait; hiçbir veri değiştirilmedi.")
            created = 0
            for question, options_text, closed in examples:
                if Poll.objects.filter(author=user, question=question).exists():
                    continue
                poll = create_poll(user, question, "Geliştirme için örnek içerik.", options_text)
                for number, choice in enumerate(list(poll.choices.all())[:2]):
                    guest_hash = hashlib.sha256(f"demo:{poll.pk}:{number}".encode()).hexdigest()
                    cast_vote(poll.pk, choice.pk, guest_hash=guest_hash)
                if closed:
                    manage_poll(poll.pk, user, "close")
                created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} örnek anket oluşturuldu. Mevcut örnekler korundu."))

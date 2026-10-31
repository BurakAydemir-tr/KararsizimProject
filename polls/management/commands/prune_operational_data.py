from django.core.management.base import BaseCommand
from django.utils import timezone
from polls.models import RateLimit, ErrorEvent, Report


class Command(BaseCommand):
    help = "Süresi dolmuş hız sayaçlarını, 30 günlük hataları ve 180 günlük sonuçlanmış bildirimleri temizler."

    def handle(self, *args, **options):
        now = timezone.now()
        counts = [RateLimit.objects.filter(expires_at__lte=now).delete()[0],
                  ErrorEvent.objects.filter(created_at__lt=now - timezone.timedelta(days=30)).delete()[0],
                  Report.objects.filter(resolved_at__lt=now - timezone.timedelta(days=180)).delete()[0]]
        self.stdout.write(f"Temizlendi: hız={counts[0]}, hata={counts[1]}, sonuçlanmış bildirim={counts[2]}")

# Faz 5 — Kullanım ve işletim

Kapsam: e-posta doğrulama/parola sıfırlama hariç güvenli küçük grup kullanımı.
Arama ve isteğe bağlı 1 saat/24 saat/7 gün bitişi eklenir; kategori veya takip
sistemi eklenmez. Bitiş, her oy isteğinde kilitli anket satırında denetlenir;
cron gerektirmez. Sonuçlar görünür kalır. Arama en fazla 100 karakter kullanır
ve gizlenmiş/kaldırılmış içerikleri göstermez.

## Kötüye kullanım ve moderasyon

`ABUSE_LIMITS` ayarlarında varsayılanlar: giriş 20/5 dakika, kayıt 5/saat,
anket oluşturma 10/saat, oy 60/dakika, bildirim 10/saat, silme 3/saat.
POST denemeleri IP ve varsa hesap kimliği başına sınırlandırılır; girişte
normalize edilmiş kullanıcı adı da sınırlıdır. Pencereler sabittir; pencere
sınırlarında kısa süreli iki kat trafik mümkün olabilir. 429 yanıtında
`Retry-After` vardır. Aynı IP'yi paylaşan kullanıcılar ortak sınıra takılabilir.
Sayaçlar PostgreSQL'dedir, ayrı sunucu süreçlerinde ortak ve atomiktir; ham IP
ve kullanıcı adı saklanmaz. Vercel ayarları yalnızca Vercel'in yeniden yazdığı
X-Forwarded-For başlığına güvenir. Başka bir proxy zinciri eklenirse bu varsayım
yeniden değerlendirilmelidir. Yerelde istemcinin gönderdiği bu başlık yok sayılır.

Herkese açık anket detayında “Bu içeriği bildir” bağlantısı vardır. Misafirlerde
imzalı çerez, üyelerde hesap başına tek bildirim kabul edilir. Bildirim yığını
otomatik sansür oluşturmaz. Yönetici Django admin → Reports ekranında inceleyip
“İhlali doğrula, anketi gizle” veya “İhlal yok” kararı verir; karar zamanı ve
yönetici kaydedilir. Süreç sonuçlandırılınca tekrar çalıştırmak kararı değiştirmez.
Yayınlanan soru/seçenek ve oylar admin'de düzenlenemez.

Misafir oyu halen hesap/tarayıcı kimliği düzeyindedir. Çerez temizleme, başka
cihazlar veya yeni hesaplar kişi başına kesin tek oy garantisini aşabilir.
IP sınırı bu riski azaltır; kimlik doğrulaması veya bot engelleme garantisi değildir.

## Veri silme ve gizlilik

Alt menüde `/gizlilik/` sayfası; üyeler için parola + açık onay isteyen
`/hesabimi-sil/` ekranı vardır. Hesap, kendi anketleri (bunlardaki diğer oylar
dahil), diğer anketlerdeki kendi oyları ve gönderdiği bildirimler kaldırılır.
Başka üyelerin bağımsız anketleri korunur. Hesap yok olduğundan eski oturumlar
artık kullanıcı bulamaz. Yönetici hesabı kendi kendine bu ekrandan silinemez.
Misafir oy silme yalnızca mevcut imzalı tarayıcı kimliğinin sahipsiz oylarını
siler; hesaba aktarılmış oyları silemez. GET istekleri silmez, POST + CSRF gerekir.

Yedeklerdeki eski veriler anında değişmez. Yedekten gerçek bir geri dönüş yapılacaksa
yedek tarihinden sonra gelen silme taleplerinin kayıtları ayrıca uzlaştırılmalı ve
yeniden uygulanmalıdır; aksi hâlde eski hesaplar geri dönebilir. Bu nedenle bu
komutlar canlıya otomatik geri yükleme yapmaz. Gizlilik açıklaması teknik davranışı
anlatır; ticari/geniş yayın öncesi veri sorumlusu ve iletişim bilgileri ayrıca
belirlenmelidir.

## Hata ve sağlık kontrolü

Her yanıtta `X-Request-ID` vardır. Beklenmeyen uygulama hataları admin → Error
events ekranına istek UUID'si, route adı, hata sınıfı ve zaman olarak kaydedilir.
Hata mesajı, parola, form içeriği, URL sorgusu, IP veya çerez kaydedilmez. DB
erişilemiyorsa güvenli özet stderr/Vercel log'una düşer. Sağlık URL'si `/health/`
salt okunur `SELECT 1` sonucuna göre 200 veya 503 verir, bağlantı bilgisi sızdırmaz.
Haricî Sentry/analitik servisi veya bildirim aboneliği kurulmadı.

Günde bir işletici tarafından çalıştırılacak bakım:

```powershell
.\.venv\Scripts\python.exe manage.py prune_operational_data --settings=config.migration_settings
```

Bu komut süresi dolmuş sayaçları, 30 günü geçen hata olaylarını ve 180 günü geçen
sonuçlanmış bildirimleri kaldırır. Açık bildirimler inceleme için kalır. Sürekli
zamanlayıcı henüz kurulmadı; komut çalışmadan süre dolması fiziksel silme yapmaz.

## Yedekleme ve gerçek geri yükleme provası

```powershell
.\.venv\Scripts\python.exe manage.py backup_application --settings=config.migration_settings
.\.venv\Scripts\python.exe manage.py verify_application_backup '.backups/GERCEK_DOSYA.json.gz' --settings=config.migration_settings
.\.venv\Scripts\python.exe manage.py prune_application_backups
.\.venv\Scripts\python.exe manage.py prune_application_backups --apply
```

Yedek REPEATABLE READ, READ ONLY snapshot'ıdır; Django uygulama tablolarını ve
izin metadatasını kapsar. Oturum, hız sayacı, hata olayı ve admin günlükleri,
Supabase Auth/Storage ve ortam dosyaları kapsam dışıdır. E-posta, parola hash'i
ve kullanıcı içeriği içerdiği için hassastır; gzip **şifreleme değildir**.
`.backups/` Git ve Vercel dışında tutulur. Bu bilgisayarda klasör ACL'si mevcut
kullanıcı ve sistem/yönetici erişimiyle sınırlanmıştır. Başka makinede de güvenli
ACL ve şifreli disk/erişimi kısıtlı yedek depolaması kullanılmalıdır.

Manifest dosyası SHA-256 ve tablo sayımlarını tutar. Doğrulama komutu sadece
yeni `restorecheck_<rastgele>` DB oluşturur; migration + loaddata + tablo ve alan
değerlerini karşılaştırır ve oluşturduğu DB'yi kaldırır. Var olan uygulama DB'sini
hedef olarak kabul etmez. `CREATEDB` yetkili doğrudan bağlantı gerektirir;
`DATABASE_TEST_ADMIN_URL` verilmezse migration pooler kullanıcı adından direct
endpoint türetilir. TLS `verify-full` korunur. Bu komut gerçek veriyle provadır,
canlı veritabanına geri dönüş komutu değildir.

Başarılı yedekleri günlük ve her migration öncesi alın. 14 günü geçen kopyaları
önce plan çıktısını inceleyerek temizleyin. İşlem şu anda işletici tarafından
başlatılır; otomatik günlük/off-site yedekleme veya Supabase PITR satın alınmadı.
Yerel disk kaybına karşı ayrı şifreli depoya kopyalama işletim sorumluluğudur.

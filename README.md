# Kararsızım

Django ve Supabase PostgreSQL ile geliştirilen anket uygulaması. **Faz 3**: çalışan üyelik/anket/oylama akışının mobil yerleşimleri, erişilebilir form hataları, karakter sayaçları ve işlem geri bildirimleri iyileştirildi. Django templates, HTML/CSS ve küçük bir JavaScript dosyası kullanılır.

Ürün kararları: [ana belge](docs/KARARSIZIM_PROJE_PLANI_VE_PROMPT.md). Tamamlanan kontroller ve kalan engeller: [proje durumu](docs/PROJE_DURUMU.md).

Faz 4 Vercel önizleme hazırlığı: [dağıtım rehberi](docs/VERCEL_DAGITIM.md). Çevrimiçi dağıtım durumu proje durumunda ayrıca belirtilir. Yerel çalıştırma komutları değişmedi.

27 Ekim 2026 itibarıyla Faz 2 şeması Supabase'e uygulandı: 22 migration, 13 özel tablo. Kritik iş kuralları ayrı PostgreSQL test veritabanında, temel akış ayrıca izole tarayıcı ortamında doğrulandı. Ayrıntılı sonuçlar durum belgesindedir.

## Windows PowerShell kurulumu

Önce proje klasörüne geçin. Mevcut `.venv` varsa yeniden oluşturmanız gerekmez; etkinleştirme komutu da zorunlu değildir.

```powershell
Set-Location -LiteralPath 'C:\Users\burak\Documents\ChatGPT\Kararsızım Projesi'
.\.venv\Scripts\python.exe --version
```

Yeni bir bilgisayarda Python 3.14.8 kurulduktan sonra:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Bağımlılıklar kesin sürümlere sabittir: Django 5.2.18, django-environ 0.14.0, psycopg/binary 3.3.6; geçişli bağımlılıklar da requirements.txt içindedir. Frontend derleme aracı veya Node.js gerekmez.

## Yerel gizli ayarlar

[Supabase projesinde](https://supabase.com/dashboard/project/kdwncovghqyprwrhwptl) veritabanı parolanızı belirleyin. Bu, Supabase hesabınıza giriş parolası değildir. Data API → Overview bölümündeki Enable Data API kapalı kalmalıdır; Django kendi üyelik ve oturum tablolarını yönetir.

```powershell
.\.venv\Scripts\python.exe scripts\configure_local.py
```

Komut yalnızca veritabanı parolasını gizli olarak sorar, özel karakterleri kodlar ve `.env` oluşturur. Yazarken karakter görünmemesi normaldir. Var olan `.env` dosyasının üzerine yazmaz. Farklı bir proje için `--connection-urls` kullanarak iki tam pooler URI'si girilebilir.

Bağlantı `password authentication failed` verirse [Database → Settings](https://supabase.com/dashboard/project/kdwncovghqyprwrhwptl/database/settings) bölümünde bu projenin **Database password** değerini doğrulayın veya yenisini belirleyin. Supabase hesabının giriş parolası farklıdır. Var olan `.env` dosyasındaki yalnızca iki veritabanı bağlantı parolasını değiştirmek için:

```powershell
py -3.14 'C:\Users\burak\Documents\ChatGPT\Kararsızım Projesi\scripts\configure_local.py' --update-password
```

Komut yeni parolayı iki kez gizli olarak ister; girişler eşleşmezse `.env` değişmez. Diğer gizli anahtarlar korunur ve parola ekrana yazdırılmaz. Parolayı `.env` içine elle düz metin URI olarak yapıştırmaya gerek yoktur; yardımcı komut özel karakterleri kodlar.

**“The term ... is not recognized” hatası:** Terminal farklı klasördeyse aşağıdaki kısa komut her klasörden çalışır. Bu bilgisayarda `py -3.14` komutunun Python 3.14.8'i başlattığı doğrulandı:

```powershell
py -3.14 'C:\Users\burak\Documents\ChatGPT\Kararsızım Projesi\scripts\configure_local.py'
```

Sanal ortamın Python'unu doğrudan kullanmak isterseniz başındaki `&` işaretiyle tam yol da çalışır. `Kararsızım Projesi` ile `.venv` arasında `\` bulunduğuna dikkat edin:

```powershell
& 'C:\Users\burak\Documents\ChatGPT\Kararsızım Projesi\.venv\Scripts\python.exe' 'C:\Users\burak\Documents\ChatGPT\Kararsızım Projesi\scripts\configure_local.py'
```

Ortam değişkenleri `.env.example` içinde listelenir. Parola ve `.env` içeriğini sohbete veya Git'e koymayın. İşletim sistemi ortam değişkenleri `.env` değerlerinden önceliklidir.

| Ayar | Kullanım |
| --- | --- |
| `DJANGO_SECRET_KEY` | En az 50 karakter; yardımcı komut üretir |
| `DJANGO_DEBUG` | Yerel geliştirmede true |
| `DJANGO_ALLOWED_HOSTS` | Virgülle ayrılan izinli alan adları |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Şema dahil güvenilen kaynaklar |
| `DATABASE_URL` | Transaction pooler, port 6543; HTTP istekleri |
| `DATABASE_MIGRATION_URL` | Session pooler, port 5432; migration |
| `GUEST_VOTE_HASH_KEY` | Misafir kimliği HMAC anahtarı; en az 32 karakter, oturumlar arasında sabit |
| `DATABASE_TEST_ADMIN_URL` | İsteğe bağlı, ayrı test DB oluşturabilen doğrudan PostgreSQL bağlantısı |

Supabase: Kaptan / kararsizim-dev / Frankfurt. Pooler `aws-1-eu-central-1.pooler.supabase.com`, kullanıcı `postgres.kdwncovghqyprwrhwptl`. Yardımcı komut bu projede panelden doğrulanmış değerleri kullanır. Başka projeye geçerken paneldeki Connect → Connection String değerlerini kullanın.

Bağlantılar SSL gerektirir. Kalıcı bağlantı, sunucu tarafı imleç ve otomatik prepared statement kapalıdır. Eksik ayarlarda SQLite'a geçilmez; anlaşılır yapılandırma hatası alınır.

## Migration ve çalıştırma

`.env` hazır olduktan sonra aşağıdaki komutları sırayla çalıştırın:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate --plan --settings=config.migration_settings
.\.venv\Scripts\python.exe manage.py migrate --settings=config.migration_settings
.\.venv\Scripts\python.exe manage.py showmigrations --settings=config.migration_settings
.\.venv\Scripts\python.exe manage.py verify_database
.\.venv\Scripts\python.exe manage.py runserver
```

Ana sayfa: http://127.0.0.1:8000/. Sunucuyu durdurmak için Ctrl+C. Migration sunucu açılışında veya HTTP isteğinde otomatik uygulanmaz. `accounts/0002` ve `polls/0002`, Django tablolarında RLS açar ve Supabase API rollerinin tablo/sequence yetkilerini kaldırır. Django tablo sahibi üzerinden çalışır; Supabase Auth kullanılmaz. Bu migration'lar geri alınırken erişim izinleri otomatik geri verilmez.

İsteğe bağlı admin hesabı ve ekranı:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

http://127.0.0.1:8000/admin/ adresine kullanıcı adıyla giriş yapılır. Kullanıcı adı 3–24 karakter, `a-z`, `0-9`, `_`; kullanıcı adı ve e-posta küçük harfe çevrilir. E-posta zorunludur. Her ikisinin benzersizliği veritabanında da korunur.

## Doğrulama

Sistem kontrolü ve tüm fazların testleri:

```powershell
.\.venv\Scripts\python.exe manage.py check --settings=config.check_settings
.\.venv\Scripts\python.exe manage.py test accounts polls config.tests scripts --settings=config.test_settings --noinput
.\.venv\Scripts\python.exe -m pip check
```

`config.test_settings` yalnızca `manage.py test` komutunda açılır. Her çalıştırmada `test_kararsizim_<rastgele>` adlı yeni PostgreSQL veritabanı oluşturur, migration'ları oraya uygular ve test sonunda kaldırır. Mevcut uygulama veritabanında test satırı oluşturmaz, `flush` yapmaz. Teste özel hızlı parola hash'i sadece bu ayarda kullanılır; normal uygulama Django'nun güvenli varsayılanını kullanır.

Varsayılan olarak session pooler kullanıcı adından aynı Supabase projesinin doğrudan bağlantısı türetilir; aynı parola, SSL ve `postgres` rolü kullanılır. Test DB oluşturmak için bu role `CREATEDB` ve doğrudan ağa erişim gerekir. Farklı/yerel bir PostgreSQL sunucusu kullanmak için yalnızca `.env` içinde `DATABASE_TEST_ADMIN_URL` tanımlanır. Testler SQLite'a geçmez ve bağlantı yoksa atlanmış gibi başarılı gösterilmez.

Testler kayıt ve parola kurallarını, 2–5 seçenek sınırını, kimlik/gizlilik/CSRF/yetkileri, misafir oyunun aktarılmasını, farklı hesapların aynı tarayıcıdan oy hakkını, sonuçları, moderasyonu, DB kısıtlarını ve eşzamanlı oy/kapatma/aktarım davranışlarını kapsar.

Bağlantısız sınırlı kontroller için:

```powershell
.\.venv\Scripts\python.exe manage.py test accounts.tests config.tests scripts --settings=config.check_settings
```

`config.check_settings` çevrimdışı kontroller içindir; gerçek PostgreSQL testlerinin yerini almaz ve normal sunucuda kullanılmaz.

Gerçek PostgreSQL ve migration tutarlılığı:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=config.migration_settings
.\.venv\Scripts\python.exe manage.py verify_database
```

`verify_database` Faz 1'den gelen, yalnızca DEBUG=true geliştirme ortamında çalıştırılan isteğe bağlı bağlantı kontrolüdür. Geçici kullanıcı/oturum satırları yazar ve rollback ile geri alır; sequence sayaçları ilerleyebilir. Faz 2 testleri için yukarıdaki **ayrı test veritabanı** komutu kullanılmalıdır.

Gizli dosya kontrolü:

```powershell
git check-ignore .env .env.local .venv/Scripts/python.exe
```

## Kapsam ve yapı

- `config`: ortak, migration ve çevrimdışı test ayarları.
- `accounts`: özel kullanıcı, admin formları, migration ve kontroller.
- `polls`: anket/seçenek/oy modelleri, formlar, oylama/aktarım servisleri, sayfalar ve salt okunur admin moderasyonu.
- `templates`, `static`: ortak HTML ve CSS; frontend framework yok.
- `scripts`: yerel ayar yardımcısı.
- `docs`: ürün planı, proje durumu ve ekran doğrulama görselleri.

## Elle deneme

1. `/uye-ol/` ile hesap oluştur; `/anket/olustur/` üzerinden 2–5 seçenekli anket yayınla.
2. Çıkış yapıp aynı anketi aç; misafir olarak oy ver ve sonucu gör.
3. Tekrar giriş yap; misafir oyun hesaba bağlanmış olacak. Aynı hesap başka cihazdan da ikinci oy kullanamaz.
4. Aynı tarayıcıda başka bir hesap aç; kendi oyunu verebilmeli. Önceki hesaba bağlanan oy ona aktarılmaz.
5. Anket sahibi olarak `/anketlerim/` sayfasından onay vererek oylamayı kapat veya anketi kaldır.
6. Admin'de seçili anketler gizlenebilir/kapatılabilir. Yayınlanan soru/seçenekler ve oy kayıtları değiştirilemez.

Üye oyları hesap başına, misafir oyları imzalı 180 günlük `HttpOnly` çerez kimliği başına benzersizdir. Çerezi silmek veya başka cihaz kullanmak misafire tekrar oy olanağı sağlayabilir; kesin kişi doğrulaması yoktur. Girişte çakışma varsa hesap oyu korunur, sahipsiz misafir oyu kaldırılır. Oylama ve kapatma aynı anket satırını kilitler. Sonuçlar oy kayıtlarından hesaplanır; canlı güncelleme için sayfayı yenilemek gerekir.

Faz 3 mobil/klavye/kontrast ve JavaScript olmadan temel kullanım kontrolleri tamamlandı; Vercel yayını Faz 4 kapsamındadır. Geniş test grubuna açmadan önce sohbette paylaşılmış veritabanı parolası değiştirilip yerel ayarlar güncellenmelidir. Hata sayfalarının güvenli Türkçe sürümü `DJANGO_DEBUG=false` iken kullanılır; geliştirmedeki DEBUG=true hata ayrıntıları yalnızca yerel kullanım içindir.

## Faz 3 arayüz kontrolleri ve örnek veri

Form hataları özetten ilgili alana bağlantı verir; JavaScript açıkken özet odaklanır. Yardım ve hatalar `aria-describedby` ile alanlara bağlanır. Karakter sayaçları, seçenek sayısı ve gönderim durumu JavaScript ile eklenir. Tarayıcının geri düğmesiyle dönüldüğünde düğmeler yeniden kullanılabilir. JavaScript yüklenmezse beş seçenek alanı görünür ve sunucu formları çalışır.

Elle kontrol: kısa soru gönderip hata bağlantısını Enter ile açın, Tab ile sonraki alana geçin; beş seçenek ekleyip sınırı görün; uzun soru/seçeneklerle 360, 768 ve 1280 px genişlikleri deneyin. Kapalı ankette hem kapanma bilgisi hem önceki seçiminiz görünür. [Tarayıcı kanıtları](docs/verification/phase3/browser-checks.json) ve [kontrast ölçümleri](docs/verification/phase3/contrast.json) kaydedildi. Bu kontroller tam ekran okuyucu/WCAG sertifikasyonu değildir.

Örnek veri komutu varsayılan olarak yalnızca planı gösterir, veri yazmaz:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo
```

Gerçek örnek yüklemek için **ayrı**, adı `_demo` ile biten geliştirme PostgreSQL veritabanını önceden hazırlayın. O PowerShell oturumunda `DATABASE_URL` ve `DATABASE_MIGRATION_URL` değerlerini bu ayrı DB'ye yönlendirin; `DJANGO_DEBUG=true` olsun. Şemayı migration komutuyla uyguladıktan sonra çalıştırın:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo --apply
```

Komut normal Supabase `postgres` uygulama DB'sine örnek yazmayı reddeder. İki açık, bir kapalı anket ve örnek oylar oluşturur; tekrarında aynı örnekleri çoğaltmaz. Demo kullanıcısının giriş yapabileceği parolası yoktur. Otomatik testlerde yalnızca ayrı `test_kararsizim_...` veritabanlarına izin verilir. Ayrı demo DB kurmak mevcut uygulamayı denemek için zorunlu değildir.

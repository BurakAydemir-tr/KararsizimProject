# Kararsızım — Vercel önizleme dağıtımı

Hedef: **Kaptan / kaptan4** ekibinde **kararsizim**, yalnızca **Preview** ortamı.
Kaynak: https://github.com/BurakAydemir-tr/KararsizimProject
Hazırlık dalı: `codex/phase4-preview`. Production yayını bu fazın kapsamına dahil değildir.

## Uygulama yapılandırması

- Python sürümü `.python-version` ile 3.14; mevcut kesin sürümlü `requirements.txt` korunur.
- `vercel.json`: Django preset, Frankfurt `fra1`, `config/wsgi.py` ve 30 saniye istek süresi.
- Vercel mevcut `manage.py` / WSGI uygulamasını algılar. Ayrı API girişi veya frontend derlemesi yoktur.
- `STATIC_ROOT` nedeniyle Vercel build sırasında `collectstatic` çalıştırıp dosyaları CDN'den sunar. Ek WhiteNoise paketi veya özel build komutu gerekmez.
- **Build ve HTTP istekleri migration çalıştırmaz.** Yeni migration varsa önce yerel session pooler ile kontrollü uygulanır.
- Bu fazda `git.deploymentEnabled=false`: push'lar kendiliğinden yayın başlatmaz. Dağıtım açıkça Preview hedefiyle, seçilen Git commit'inden oluşturulur. Production dalı `master` olarak doğrulandı; production ortamında uygulama sırları tanımlı değildir.
- `.vercelignore` yerel gizli dosyaları, sanal ortamı, IDE/geçici dosyaları ve test/kanıt içeriklerini dağıtım yüklemesinden çıkarır. Belgeler GitHub'da kalır.

Resmi kaynaklar: [Django dağıtımı](https://vercel.com/docs/frameworks/full-stack/django), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [ortam değişkenleri](https://vercel.com/docs/environment-variables).

## Gizli ayarlar

Önce sohbette paylaşılmış veritabanı parolasını Supabase'de yenileyin ve yerel `.env` dosyasını `scripts/configure_local.py --update-password` ile güncelleyin. Yeni parolayı sohbete veya Git'e eklemeyin. Bağlantının başarılı olduğu doğrulanmadan dağıtım tamamlanmış sayılmaz.

Doğrulanmış yerel bağlantıdan **ayrı preview anahtarları** hazırlamak için:

```powershell
Set-Location -LiteralPath 'C:\Users\burak\Documents\ChatGPT\Kararsızım Projesi'
.\.venv\Scripts\python.exe scripts\prepare_vercel_env.py
```

Komut `.env.vercel.local` oluşturur; hiçbir gizli değeri ekrana yazmaz. Mevcut dosyayı değiştirmez; böylece oturum ve misafir anahtarları tekrar çalıştırmada dönmez. Dosya Git ve Vercel kaynak yüklemesinin dışındadır. Veritabanı parolası daha sonra değiştirilirse bu dosyadaki ve Vercel'deki `DATABASE_URL` de güvenli biçimde güncellenmelidir; diğer iki anahtar korunur.

| Değişken | Preview değeri/türü |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.vercel_settings`, Config |
| `DJANGO_DEBUG` | `false`, Config |
| `DJANGO_ALLOWED_HOSTS` | Boş; sistemdeki tam deployment/branch hostname'leri eklenir. Özel alan adı varsa ayrıca tam adını ekleyin. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Boş; izinli tam alan adlarının HTTPS origin'leri türetilir. |
| `DJANGO_SECRET_KEY` | Yalnızca bu preview için üretilmiş Secret |
| `GUEST_VOTE_HASH_KEY` | Yalnızca bu preview için üretilmiş, sabit Secret |
| `DATABASE_URL` | Doğrulanmış transaction pooler (6543), Secret |

Bu değerler sadece doğru projenin **Preview** ortamına kaydedilir. Runtime'a migration URL'si veya test DB yöneticisi verilmez. Anahtar/parola değerlerini araç çıktısına, ekran görüntüsüne veya kaynağa koymayın. Vercel'de gizli değerler Secret/Sensitive olarak tutulmalıdır.

`config.vercel_settings`, DEBUG'u zorunlu olarak kapatır; Secure oturum/CSRF çerezlerini ve HTTPS yönlendirmesini açar. Vercel'in TLS proxy'sindeki `X-Forwarded-Proto` bilgisi kullanılır. `VERCEL_URL` ve `VERCEL_BRANCH_URL` sadece tam `.vercel.app` hostname kabul eder; tüm `.vercel.app` alanları için joker izin verilmez. Vercel sistem değişkenleri build ve runtime'a açık olmalıdır.

Önizlemede HSTS bir saatle sınırlıdır; alt alan adlarına yayılmaz ve preload kaydı istenmez. `check --deploy` bu iki bilinçli tercih için `security.W005` ve `security.W021` uyarıları verir. Gerçek alan adı/production planında yeniden değerlendirilir.

## Veritabanı ve dağıtım sırası

1. Doğru ekip, proje, GitHub deposu ve Preview ortamını doğrulayın. Vercel Login Connection ile GitHub uygulamasının depo erişimi ayrı adımlardır.
2. Ortam değişkenlerini kaydedin. Yerel `.env` veya `.env.vercel.local` dosyasını kaynak dosyası olarak yüklemeyin.
3. Kullanılan veritabanı `kararsizim-dev` geliştirme prototipidir; mevcut kullanıcı deneme verileri korunur. Production veritabanı yerine kullanılmamalıdır.
4. `manage.py migrate --check --settings=config.migration_settings` ile bekleyen migration kontrolü yapın. Gerekiyorsa aynı ayarla açıkça `migrate` çalıştırın.
5. Testleri ayrı PostgreSQL veritabanında çalıştırın:

```powershell
.\.venv\Scripts\python.exe manage.py test accounts polls config.tests scripts --settings=config.test_settings --noinput
```

6. Hazırlık dalının kesin commit'ini Preview olarak dağıtın. `--prod`, promotion veya production alias ataması yapmayın.
7. Build durumunu ve runtime loglarını inceleyin. Yalnızca `READY` ve gerçek HTTP doğrulaması sonrasında bağlantıyı çalışan teslim olarak paylaşın.

## Gerçek URL doğrulaması

- HTTPS ana sayfa, kayıt/giriş, CSS/JS ve admin CSS dosyaları açılmalı; hassas HTML `private, no-store` kalmalı.
- CSRF korumalı kayıt → anket oluşturma → misafir oyu → sonuç akışı tamamlanmalı.
- Yeniden oy ve aynı tarayıcıda farklı hesap davranışı korunmalı; farklı bir `.vercel.app` origin'inden istek kabul edilmemeli.
- Çerezlerde Secure, oturum ve misafir kimliğinde HttpOnly/SameSite kontrol edilmeli.
- Yanlış URL Türkçe 404 göstermeli; debug ayrıntıları dışarı verilmemeli.
- Önceden bulunan kullanıcı/anketleri değiştirmeyin. QA kayıtları açıkça sentetik adlarla oluşturulmalı ve sadece bu kayıtlar üzerinde işlem yapılmalı.

Vercel Authentication koruması çıkarsa mevcut erişimle doğrulayın. Test grubuna erişim ayrı olarak değerlendirilir; koruma izinsiz kapatılmaz. Dağıtım URL'si ve yapılan/yapılamayan kontroller `PROJE_DURUMU.md` içinde kaydedilir.

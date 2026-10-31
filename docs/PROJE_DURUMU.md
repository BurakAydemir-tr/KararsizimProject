# Kararsızım — Proje durumu

Son güncelleme: **31 Ekim 2026**. Kapsam: **Faz 5 — E-posta işlemleri hariç küçük grup kullanımı**.
Ürün referansı: [ana plan](KARARSIZIM_PROJE_PLANI_VE_PROMPT.md). Kurulum ve komutlar: [README](../README.md).

## Faz 5 — Güncel teslim kapsamı

- E-posta doğrulama, parola sıfırlama ve gerçek e-posta gönderimi kullanıcı isteğiyle ertelendi.
- Ortak PostgreSQL hız sayaçları ve 429/Retry-After; aynı yazar/soru için 24 saatlik tekrar kontrolü.
- Üye/misafir içerik bildirimi ve yönetici inceleme kararı; otomatik bildirim sayısıyla gizleme yok.
- Parola ve açık onayla hesap/veri silme; mevcut tarayıcının sahipsiz misafir oyları için ayrı silme ekranı.
- Gizlilik/çerez açıklaması, arama ve isteğe bağlı 1 saat/24 saat/7 günlük anketler.
- Güvenli istek kimliği/hata olayları, admin incelemesi ve salt okunur sağlık URL'si.
- Uygulama yedeği alındı; ayrı restorecheck DB'ye gerçek geri yükleme, checksum, tablo sayımları ve alan değerleri doğrulandı; geçici DB kaldırıldı.
- Tam PostgreSQL regresyon paketi 75/75; son eklenen 3 hedefli kontrol de geçti (iki test mevcut paketle ortaktır).
- Model/migration farkı yok; Django kontrolü ve pip check başarılı. Yeni tablolar RLS/API-rol erişim korumasını aynı migration içinde alır.
- İşletim ve saklama komutları: [Faz 5 rehberi](FAZ5_ISLETIM.md). Günlük zamanlayıcı, haricî hata alarmı, off-site yedek/PITR veya production alan adı kurulmadı.

Aşağıdaki Faz 4 ve önceki test kayıtları tarihsel teslim bilgileridir.

## Önceki teslim durumu

**Faz 4 tamamlandı.** Django/Supabase temeli ve çalışan işlevler korundu. Vercel Preview yayını READY durumunda; gerçek HTTPS adresinde üyelik ve oylama akışı doğrulandı. Bu tarihsel teslimde production yayını veya Faz 5 başlatılmamıştı.

## Faz 4 teslimi

- GitHub kaynak adresi: `BurakAydemir-tr/KararsizimProject`; çalışma dalı `codex/phase4-preview`.
- Vercel hedefi: Kaptan (`kaptan4`, `team_zolmCXRGWBcqIns3PHPfcIqH`) / `kararsizim`, Preview. Ekip erişimi kullanıcı tarafından onaylandı ve doğrulandı.
- Proje ID: `prj_I7NY6gR5g7SL8KvxPAD5XlxPZNAi`; deployment: `dpl_9V3FACCFPpq9JoumDpVpYs1sFbK3`.
- [Önizleme adresi](https://kararsizim-gqndxxo2i-kaptan4.vercel.app) — READY, Frankfurt `fra1`, Django 5.2.18 / Python 3.14.8, build 9 saniye. Uygulama commit'i `ac2822c7d7250f0888a2dad20fb63ea9b6d38dab`; kaynak CLI yüklemesi ve aynı Git commit metadata'sı doğrulandı. Sonraki belge/kanıt commit'leri çalışan uygulamayı değiştirmez.
- Kalıcı Vercel Authentication koruması açık. Kullanıcının açık onayıyla yalnızca bu deployment için 23 saatlik paylaşım bağlantısı oluşturuldu; erişim parametresi Git'e yazılmadı, sohbette paylaşıldı. Süre dolunca Vercel oturumu veya yeni paylaşım bağlantısı gerekir.
- `vercel.json`: Django preset, mevcut WSGI girişi, Frankfurt, 30 saniye. Mevcut Python 3.14 ve paket sürümleri korundu; ek runtime paketi yok.
- `config.vercel_settings`: HTTPS, güvenli çerezler, kapalı debug, tam deployment/branch hostname ve HTTPS CSRF origin'leri. Yerel `config.settings` davranışı korunuyor.
- `.vercelignore`: gizli ayarlar, geçici dosyalar ve test/kanıt içerikleri kaynak yüklemesinden dışlanıyor.
- `scripts/prepare_vercel_env.py`: ayrı preview anahtarlarıyla Git dışında kalan ortam dosyası hazırlığı; mevcut dosyayı üzerine yazarak anahtar döndürmez. Yanlış/session pooler adresini reddeder.
- [Dağıtım rehberi](VERCEL_DAGITIM.md) eklendi. Migration'lar build/HTTP isteklerine bağlanmadı; şema değiştirilmedi.
- **Geçen kontroller:** Tam paket **52/52**, ayrı geçici PostgreSQL DB'si; mevcut 5 eşzamanlılık testi dahil. Ayrıca 18 çevrimdışı test, sistem kontrolü ve pip check geçti; 130 statik dosya yerelde toplandı, Vercel build'inde collectstatic çalıştı. Supabase 13/13 uygulama tablosunda RLS etkin.
- `check --deploy`: yalnızca önizleme için bilinçli bırakılan HSTS alt alan adı/preload uyarıları (`security.W005`, `security.W021`). HSTS süresi bir saat; production alan adı henüz yok.
- Kullanıcı DB parolasını yeniledi; `.env` güncellendi, session pooler bağlantısı ve bekleyen migration olmadığı doğrulandı. Tam PostgreSQL testleri de yeni bağlantıyla geçti. Runtime transaction pooler bağlantısı gerçek kayıt/anket/oy işlemleriyle doğrulandı.
- GitHub Login Connection ve Vercel GitHub uygulaması kullanıcı tarafından kuruldu; depo bağlantısı çalışıyor. CLI 65.5.0 oturumu ve Kaptan/kararsizim yerel bağlantısı doğrulandı. Dört Config ve üç Secret sadece Preview'a kaydedildi; production sırları eklenmedi. Sırlar kullanıcı onayıyla, yerel dosyadan stdin üzerinden, değerleri gösterilmeden aktarıldı.
- İlk otomatik Git build'i Production hedefini seçti ve eksik production sırları nedeniyle ERROR oldu; çalışan production yayını oluşmadı. `git.deploymentEnabled=false` ile otomatik Git yayınları kapatıldı. Başarılı dağıtım CLI'da açık `--target=preview` seçimiyle yapıldı; API kaydında `target=null` Preview anlamına gelir. `master` production dalı olarak doğrulandı.
- Canlı tarayıcı: kayıt → anket oluşturma → çıkış → misafir oy → %100 sonuç → yenilemede tekrar oy düğmesinin yokluğu → girişte oy aktarımı → aynı tarayıcıda ikinci hesapla bağımsız oy → %50/%50 sonuç geçti. Gerçek DB'de iki oyun iki ayrı hesaba bağlı olduğu ve sahipsiz misafir oyu kalmadığı ayrıca doğrulandı.
- HTTPS ana sayfa, CSS, JS ve admin CSS HTTP 200; Türkçe 404, debug ayrıntısı yok. `private, no-store`, HSTS 3600, nosniff ve Secure CSRF çerezi gözlendi. Diğer çerez bayrakları konfigürasyon ve regresyon testlerinde doğrulandı; tekrar kullanılan HTTP istemcisinde misafir çerezi yeniden gönderilmedi.
- Sonuç ekranı 360/768/1280 px genişlikte taşmadı; e-posta HTML'de görünmedi; uygulama kaynaklı tarayıcı konsol hatası yok. Bu Preview'ın son 30 dakikalık error/fatal runtime log taramasında kayıt yok.
- Sentetik QA anketi akıştan kaldırıldı; iki QA hesabı devre dışı bırakılıp parolaları kullanılamaz yapıldı. Önceden var olan hesap/anket/oylar korunuyor; fiziksel satır silinmedi. Kalan geçici test veritabanı sayısı 0. Yerel sunucu açılmadı.

Kanıtlar: [özet](verification/phase4/checks.json), [canlı tarayıcı kontrolleri](verification/phase4/browser-checks.json), [DB kontrolü](verification/phase4/database-checks.json), [QA temizliği](verification/phase4/qa-cleanup.json), [masaüstü sonuç](verification/phase4/results-desktop.png), [mobil sonuç](verification/phase4/results-360.png). Görseller yalnızca sentetik QA içerikleridir.

Yerel curl/urllib istemcilerinde TLS bağlantı sıfırlaması görüldü; canlı kontroller gerçek tarayıcı ve kullanıcı onaylı geçici erişimi kullanan Vercel fetch üzerinden tamamlandı. Başarılı tarayıcı akışından sonraki son yeniden açılışta in-app browser da `ERR_CONNECTION_RESET` verdi; bu erişim sorunu kalıcı olarak çözülmüş sayılmaz. Aynı anda Vercel fetch ana sayfayı HTTP 200 döndürdü ve QA anketinin akıştan çıktığını doğruladı. Kullanıcının kendi tarayıcısı/ağı üzerinden erişimi ayrıca denemesi gerekir. Bu önizleme küçük test grubu içindir; production alan adı, e-posta doğrulama/parola sıfırlama ve geniş katılımlı yayın ayrı kapsamdır.

Kullanıcı, hesap/misafir tekrar oy ve oy aktarımı senaryolarını elle denedi ve çalıştığını doğruladı. Son görsel düzeltmede kapalı anket etiketi açık turuncu zemin/koyu mercan yazıyla ayrıldı; açık anket etiketi mor kaldı. Yerel sunucu kullanıcının isteğiyle durduruldu. Faz 1–3 kaynakları, belgeler ve doğrulama kanıtları ilk Git teslimine dahil edildi; gizli ayarlar ve geçici dosyalar dışarıda tutuldu.

## Faz 3 değişiklikleri ve doğrulamalar

- Ortak hata özeti: alan bağlantıları, klavye odağı ve tekrar girişte korunan normal form değerleri. Parolalar yeniden doldurulmaz. Yardım/hata ID'leri ile `aria-describedby` bağlantıları tamamlandı; textarea hata rengi eklendi.
- Karakter sayaçları, 2–5 seçenek alanı için canlı sayı/sınır bildirimi, kaldırma düğmelerine anlamlı adlar. JavaScript ile gizlenen bir alan hata içeriyorsa görünür tutulur.
- Gönderimde düğme kilidi ve işlem mesajı; tarayıcı geçmişinden dönüldüğünde düğme ve sayaçlar yenilenir. Veritabanındaki çift oy koruması ayrıca devam eder.
- Mobil menüde daha rahat dokunma alanları, uzun kullanıcı adı/metin sarma, etkin menü bağlantısı, radyo odağı, sonuç çubukları ve kapatma onayı düzeni. Anketlerim kartlarının başlık seviyesi düzeltildi.
- Daha önce oy veren kullanıcıya da kapalı anket bilgisi gösterilir; önceki seçimi ayrıca görünür.
- `seed_demo`: varsayılan kuru çalışma. `--apply`, yalnızca DEBUG=true ve ayrı `_demo` / geçici `test_kararsizim_...` DB'de çalışır; normal `postgres` DB'sini reddeder. Üç örnek anketi çoğaltmadan oluşturur; demo hesabının parolası kullanılamaz. Uygulama veritabanına örnek yüklenmedi.
- Yeni paket, model veya migration eklenmedi. Oylama/aktarım/izin kuralları değiştirilmedi.

| Kontrol | Sonuç |
| --- | --- |
| Test paketi | 45 testlik ana çalıştırma + 2 demo testi başarılı; toplam 47 farklı test |
| Ek son kontrol | 3 erişilebilirlik + 2 demo testi tekrar başarılı |
| Kritik kurallar | Mevcut 5 eşzamanlılık testi dahil çift oy, aktarım, yetki, CSRF ve gizlilik kontrolleri geçti |
| Django / bağımlılıklar | Sistem kontrolü ve pip check başarılı; migration farkı yok |
| Mobil/masaüstü | Uzun soru + 5 uzun seçenek, sonuç, akış, oluşturma ve kayıt: 360/768/1280 px yatay taşma yok |
| Klavye | Hata özetinden Enter ile alan odağı; Tab ile sonraki alana geçiş ve görünür odak doğrulandı |
| JavaScript yüklenmeden | İzole sunucuda uygulama JS dosyası boş yanıtlandı; beş alanlı form → anket oluşturma → oy → sonuç gerçek tarayıcıda geçti |
| Kontrast | Seçilen 8 temel metin/zemin çifti 4.5:1 üstünde; ölçülen en düşük oran 5.77:1 |
| Tarayıcı | Misafir oy, girişte aktarım/çakışma, seçenek sınırı, hata odağı, kapatma onayı ve kapalı sonuç ekranı geçti; konsol hatası yok |

Test verileri ayrı geçici PostgreSQL DB'lerinde oluşturuldu. Tarayıcı önizleme DB'si de kapatılıp silindi; normal uygulamadaki hesap ve anketler korundu. Yerel test sunucusu teslim sonunda durduruldu.

Kanıtlar: [tarayıcı ölçümleri](verification/phase3/browser-checks.json), [kontrast](verification/phase3/contrast.json), [masaüstü sonuç](verification/phase3/results-desktop.png), [mobil oluşturma](verification/phase3/create-360.png), [kapalı anket](verification/phase3/closed-360.png), [JS olmadan sonuç](verification/phase3/nojs-results-360.png). `long-vote-*` ve `long-results-*` görselleri üç genişlikte uzun içerik testlerini gösterir. Tüm görseller silinmiş, sentetik önizleme verilerine aittir.

Sınırlar: tam ekran okuyucu ve farklı tarayıcı motorlarıyla kapsamlı erişilebilirlik denetimi yapılmadı. Otomatik tekrar gönderme/ağ zaman aşımında sonuç sorgulama eklenmedi; bağlantı kopmasında sunucu kayıt durumu sayfa yenilenerek kontrol edilir. Yeni performans sorunu görülmediğinden sorgu yapısı korunmuştur. Aşağıdaki Faz 2 sayıları ve ekranlar tarihsel doğrulama kaydıdır.

## Çalışan özellikler

- Kullanıcı adı/e-posta/parola/parola onayıyla kayıt; otomatik oturum açma, kullanıcı adıyla giriş ve CSRF korumalı POST çıkış. Aynı site dışındaki `next` hedefleri reddedilir.
- Kullanıcı adları normalize edilir; e-posta zorunlu ve büyük/küçük harften bağımsız benzersizdir. Halka açık HTML'de e-posta ve oy veren kimlikleri gösterilmez.
- Soru 10–200, açıklama en fazla 500, seçenekler 1–100 karakter. 2–5 seçenek; boş ek alanlar atlanır, aynı seçenekler ve altıncı seçenek sunucuda reddedilir. Anket/seçenek kaydı atomiktir.
- Yeni anketler önce gelecek şekilde tarih/ID sıralı ve 12 kayıtlık sayfalı açık akış; detay, herkese açık sonuçlar ve Anketlerim.
- İmzalı, HttpOnly, SameSite=Lax, 180 günlük misafir çerezi; HTTPS kullanımında Secure. Veritabanında ham kimlik yerine ayrı anahtarla HMAC özeti tutulur. Geri dönmüş geçerli çerez olmadan misafir oy oluşturulmaz.
- Üyede anket/hesap, misafirde anket/çerez özeti bazında benzersizlik veritabanında korunur. Aynı tarayıcıdaki farklı hesaplar bağımsız oy verebilir.
- Giriş ve kayıtta sahipsiz misafir oyları atomik biçimde hesaba bağlanır. Hesabın oyu varsa o korunur, misafir oyu kaldırılır. Bağlanmış oy başka hesaba taşınmaz.
- Oy verme, kapatma, kaldırma ve admin gizleme aynı anket satırını kilitler. Aktarım kilitleri anket ID sırasıyla alınır. Oy sonuçları Vote satırlarından hesaplanır; ayrı sayaç yoktur.
- Sahibi için kapatma/kaldırma onay ekranları. Kaldırma kalıcı satır silmek yerine işaretleme yapar. Gizli/kaldırılmış anketin halka açık adresi 404 döndürür.
- Django admin üzerinden gizleme/kapatma. Yayınlanmış soru ve seçenekler salt okunur; oy ekleme/değiştirme/silme admin'de kapalıdır.
- Beşe kadar seçenek ekleme/kaldırma ve radio seçilmeden oy düğmesini devre dışı tutma için küçük JavaScript. Normal sunucu formları JavaScript olmadan da çalışır.
- DEBUG=false iken Türkçe 400/403/404/500 ve CSRF ekranları. CSS sürüm adresi Faz 1 önbelleğinin eski görünümü taşımaması için güncellendi.

## Veritabanı ve güvenlik

- Supabase: Kaptan / kararsizim-dev / Frankfurt, proje ref `kdwncovghqyprwrhwptl`.
- Çalışma zamanı transaction pooler (6543), migration session pooler (5432); SSL ve psycopg prepared statement/imleç ayarları korunuyor.
- `polls/0001_initial` ve `polls/0002_protect_poll_tables` uygulandı. Toplam **22 uygulanmış migration**, **13 tablo** var. Bekleyen migration veya model/migration farkı yok.
- 13/13 tabloda RLS. PUBLIC ve Supabase API rollerinden tablo/sequence izinleri kaldırıldı; anon/authenticated/service_role için beklenmeyen tablo yetkisi **0**, sequence yetkisi **0**.
- Data API kapalı kalıyor; [27 Ekim panel kanıtı](verification/supabase-data-api-disabled.png).
- Supabase advisor yalnızca 13 adet **INFO — RLS Enabled No Policy** bildirimi verdi. Bu iç tablolara API erişimi istenmediğinden politika eklenmedi; Django tablo sahibi üzerinden çalışır. [Bildirimin açıklaması](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy).
- Faz 2 otomatik test tesliminde uygulama DB'si boştu. Sonraki kullanıcı isteğiyle normal deneme hesabı açıldı ve kullanıcı kendi testlerini yaptı; önceki sıfır sayıları güncel veri sayısı değildir. Faz 3 testleri bu verilere yazmadı.

## Doğrulamalar

| Kontrol | Sonuç |
| --- | --- |
| Django sistem kontrolü | Sorun yok |
| Model/migration tutarlılığı | No changes detected |
| Uygulama DB migration kontrolü | Bekleyen migration yok |
| Tam test paketi | **42/42 geçti**, ayrı PostgreSQL DB |
| Eşzamanlı testler | Aynı misafir/üye için çift oy, oy/kapatma yarışı, aktarım/üye oyu yarışı, iki hesabın aynı misafir oyunu sahiplenmesi geçti |
| Temel iş kuralları | Kayıt/giriş, normalizasyon, parola hash'i, sınırlar, CSRF, yetki, gizlilik, sonuçlar, admin salt okunurluğu ve gerçek DB kısıtları geçti |
| Liste performansı | Misafir akışında 12 kart için 2 sorgu; kart başına sorgu yok |
| Bağımlılıklar | pip check başarılı; yeni paket eklenmedi |
| Gizli dosyalar | .env, .env.local, .venv ve .idea Git dışında |

Makine tarafından okunabilir özet: [checks.json](verification/phase2/checks.json). Normal uygulamada ana sayfa, kayıt, giriş, admin giriş, CSS ve JavaScript HTTP 200 döndü. Test ayarının test dışındaki komutları reddettiği ve kalan geçici test veritabanı sayısının 0 olduğu ayrıca kontrol edildi.

`config.test_settings` her çalıştırmada yeni `test_kararsizim_<rastgele>` veritabanı oluşturur, migration'ları oraya uygular, sonunda siler. `manage.py test` dışındaki kullanımı engellenir. Ayrı DB için doğrudan PostgreSQL/CREATEDB erişimi gerekir; isteğe bağlı DATABASE_TEST_ADMIN_URL desteklenir. Test ayarı normal uygulamada kullanılmaz.

Tarayıcı doğrulaması da ayrı geçici PostgreSQL veritabanında yapıldı: kayıt, üç seçenekli anket, seçenek ekleme sınırı/kaldırma, misafir oy, girişte sahiplenme, aynı tarayıcıda ikinci hesapla ikinci oy, yüzde 50/50 sonuç, sahibin onayla kapatması ve kaldırması doğrulandı. Tarayıcı test DB'si de temizlendi; deneme hesabı veya anket bırakılmadı.

| Sonuç ekranı | Yatay taşma | Kanıt |
| --- | --- | --- |
| 360 px | Yok | [Mobil](verification/phase2/results-360.png) |
| 768 px | Yok | [Tablet](verification/phase2/results-768.png) |
| 1280 px | Yok | [Masaüstü](verification/phase2/results-1280.png) |

Akış ve oluşturma formu da 360 px genişlikte taşmadı. Diğer kanıtlar: [Akış](verification/phase2/feed.png), [mobil oluşturma](verification/phase2/create-mobile.png), [Anketlerim](verification/phase2/my-polls.png). Görsellerdeki hesaplar ve anket yalnızca silinmiş izole test ortamına aittir. Son menü değişikliğinden sonra normal uygulamanın [ana sayfası](verification/phase2/home-live-mobile.png) ve [kayıt formu](verification/phase2/signup-mobile.png) da 360 px genişlikte tekrar doğrulandı.

## Önceki temelden korunanlar ve düzeltmeler

- Python 3.14.8, Django 5.2.18 LTS, django-environ 0.14.0, psycopg/binary 3.3.6; asgiref 3.12.1, sqlparse 0.6.0, tzdata 2026.5.
- Özel AbstractUser, admin entegrasyonu, ortam yardımcısı, açık zemin/mor/mint/mercan tasarım korundu.
- Yinelenen veya geçersiz kullanıcı adıyla form doğrulamasında normalize_username(None) hatası düzeltildi. Yinelenen e-posta alanına anlaşılır Türkçe hata eklendi.
- Boş POST formlarının doğrulama hatalarını göstermesi sağlandı; toplu oy sayımı sonrası akış sıralaması açıkça tarih/ID olarak sabitlendi.
- Yeni bağımlılık, frontend framework, ayrı API veya arka plan servisi eklenmedi.

## Kalan işler

- Parola yenileme takip işi 28 Ekim'de kullanıcı tarafından tamamlandı; bağlantı ve Preview Secret doğrulandı. Yeni parolalar sohbete/Git'e yazılmamalı.
- Faz 3 tamamlandı; kapsamlı ekran okuyucu/farklı tarayıcı denetimleri ileride ihtiyaç oldukça genişletilebilir.
- Faz 4 tamamlandı; geçici paylaşım bağlantısının süresi dolarsa yeniden erişim bağlantısı oluşturulabilir. Kalıcı/public production yayını ayrıca kararlaştırılacak.
- E-posta doğrulama/parola sıfırlama ertelendi; daha geniş katılımlı/production yayın, otomatik bakım ve off-site yedek işletimi ayrı planlanacak. Misafir çerezinin silinmesi tekrar oy olanağı sağlayabilir; kişi başına kesin oy garantisi verilmez.

Kalıcı admin hesabı kullanıcı tarafından createsuperuser ile oluşturulabilir. Test sunucuları teslim sonunda durdurulur; README'deki runserver komutu uygulamayı yeniden açar.

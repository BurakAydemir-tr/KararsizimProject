# Kararsızım — Proje Tanımı, Geliştirme Planı ve ChatGPT Promptları

Belge sürümü: 1.5  
Hazırlanma tarihi: 20 Ekim 2026  
Son güncelleme: 28 Ekim 2026  
Hedef: Önce çalışan ve denenebilir bir web uygulaması prototipi, ardından küçük adımlarla geliştirme.

Güncel uygulama durumu ve doğrulamalar: [PROJE_DURUMU.md](PROJE_DURUMU.md). Faz 3 tamamlandı; Faz 4 Vercel önizleme hazırlığı devam ediyor. Dağıtım rehberi: [VERCEL_DAGITIM.md](VERCEL_DAGITIM.md).

## 1. Bu belge nasıl kullanılmalı?

Bu dosya, Kararsızım uygulamasının ürün ve teknik referansıdır. ChatGPT ile geliştirme yaparken dosyanın tamamını sohbete ekle veya içeriğini paylaş. Ardından **18. bölümdeki ana promptu** gönder. İlk çalışma için **19. bölümdeki Faz 1 promptunu** kullan.

- Bir seferde yalnızca bir fazı uygulat. Faz içindeki gerekli işleri birlikte tamamlat.
- Her fazın sonunda çalıştırma adımlarını, test sonuçlarını ve kalan işleri al.
- Sonraki faza geçmeden önce ortaya çıkan sonucu kendi ortamında dene.
- Yeni bir sohbet açarsan bu belgeyi, güncel proje dosyalarını ve son durum özetini paylaş. Önceki sohbetin kendiliğinden hatırlandığını varsayma.
- ChatGPT'nin dosya düzenleme, terminal veya dağıtım erişimi yoksa aynı çalışma dosya içerikleri ve adım adım komutlarla yürütülmeli. Yapılmamış işlemler yapılmış gibi anlatılmamalı.

**Bu belge bir geliştirme talimatıdır; uygulamanın şu anda oluşturulduğu veya yayına alındığı anlamına gelmez.**

## 2. Ürün özeti

**Proje adı:** Kararsızım  
**Kısa tanım:** Günlük kararlarını topluluğa sor, seçeneklerini paylaş, insanların oylarıyla kararını kolaylaştır.  
**Önerilen slogan:** “Kararsız kaldın? Bir de bize sor.”

Örnek kullanım:

> Bugün sinemaya mı gitsem, restorana mı?
>
> - Sinemaya git 🎬
> - Yeni bir restoran dene 🍝
> - Evde film gecesi yap 🍿

Anket sahibi sorusunu ve seçeneklerini yayınlar. Ziyaretçiler seçeneklerden birine oy verir. Sonuçlar oy sayıları ve yüzde çubuklarıyla gösterilir.

Temel değer, insanların küçük kararlar için hızlıca fikir alabilmesidir. Ürün dili sıcak, gündelik ve Türkçe olmalı. İlk sürüm sosyal ağ özellikleriyle genişletilmemeli.

## 3. Değişmez gereksinimler

Bu bölüm doğrudan proje sahibinin talepleridir; açık bir yeni talep olmadan değiştirilmemelidir.

1. Uygulamanın adı **Kararsızım** olacak.
2. Kullanıcılar soru ve seçeneklerden oluşan anketler oluşturabilecek.
3. Bir ankette **en az 2, en fazla 5 seçenek** bulunacak.
4. Takip etme, takipçi veya takip edilenler mekanizması olmayacak.
5. Platformdaki yayınlanmış anketler tüm ziyaretçiler tarafından görülebilecek; içerik erişimi takip ilişkisine veya üyeliğe bağlanmayacak.
6. Üye olmayan ziyaretçiler anketleri görüntüleyebilecek ve oy verebilecek.
7. Anket oluşturmak için üyelik ve açık bir kullanıcı oturumu gerekecek.
8. Kayıt sırasında e-posta, parola ve kullanıcı adı alınacak.
9. Anketlerde oluşturucunun kullanıcı adı görünecek; e-posta adresi herkese açık alanlarda gösterilmeyecek.
10. Backend Python ve Django ile geliştirilecek.
11. Veritabanı Supabase üzerinde PostgreSQL olacak.
12. Dağıtım hedefi Vercel olacak.
13. Ön yüz aynı repoda HTML, CSS ve JavaScript ile geliştirilecek; ayrı frontend framework kullanılmayacak.
14. Arayüz açık arka planlı, canlı renk vurgulu, temiz ve gençlere hitap eden bir tasarıma sahip olacak.
15. Öncelik basit bir prototip; gereksiz teknoloji ve mimari katmanlar eklenmeyecek.

“Herkes görebilir” kuralı yayınlanmış içerik içindir. Sahibi tarafından kaldırılmış veya yönetici tarafından gizlenmiş içerik, normal akışta gösterilmez. Oylaması kapatılmış anketlerin sonuçları ise görülebilir.

## 4. Prototip için önerilen varsayımlar

Aşağıdaki kararlar talepte belirtilmeyen ayrıntıları tamamlar. Bunlar değiştirilebilir başlangıç kararlarıdır; her biri için geliştirmeyi durdurup soru sormak gerekmez.

| Konu | İlk sürüm kararı |
|---|---|
| Dil | Türkçe |
| Giriş yöntemi | Kullanıcı adı ve parola; e-posta kayıt için zorunlu |
| Oy tipi | Tek seçimli; her oy tek bir seçeneğe gider |
| Oy değiştirme | İlk sürümde yok |
| Kendi anketine oy verme | Anket sahibi de oy verebilir |
| Sonuçları görme | Oy verdikten sonra otomatik; oy vermeden “Sonuçları gör” bağlantısıyla da erişilebilir |
| Sonuçları gördükten sonra oy verme | Anket açıksa ve önceden oy verilmediyse mümkün |
| Varsayılan akış | En yeni yayınlanan anketler; sayfa başına 12 kayıt |
| Anket süresi | Otomatik süre sınırı yok; sahibi oylamayı elle kapatabilir |
| Kapandıktan sonra | Sonuçlar görünür, yeni oy kabul edilmez; tekrar açma ilk sürümde yok |
| Düzenleme | Yayınlandıktan sonra soru ve seçenekler değiştirilemez |
| Kaldırma | Sahibi kendi anketini onay ekranından kaldırabilir; kayıt soft delete ile saklanır |
| Anket açıklaması | İsteğe bağlı kısa düz metin |
| Görsel yükleme | İlk sürümde yok |
| Kullanıcı adı değiştirme | İlk sürümde yok |
| E-posta doğrulama / parola sıfırlama | Kontrollü prototipte ertelenebilir; geniş katılımlı kullanımdan önce ayrıca planlanır |
| Gerçek zamanlı sonuçlar | Yok; sayfa yenilendiğinde veya oy gönderildiğinde güncellenir |
| Kullanıcı profili | Herkese açık profil yok; yalnızca oturum sahibine özel “Anketlerim” sayfası |

Sonuçların önceden görülebilmesi oy tercihlerini etkileyebilir. Bu ürün bilimsel veya resmi bir araştırma aracı olarak sunulmaz.

## 5. Kullanıcı rolleri ve yetkiler

| İşlem | Misafir | Üye | Yönetici |
|---|---|---|---|
| Yayındaki anketleri listeleme ve açma | Evet | Evet | Evet |
| Açık ankete oy verme | Evet | Evet | Evet |
| Toplam sonuçları görme | Evet | Evet | Evet |
| Anket oluşturma | Hayır | Evet | Evet |
| Kendi anketlerini listeleme | Hayır | Evet | Evet |
| Kendi anketini kapatma / kaldırma | Hayır | Evet | Evet |
| Başkasının anketini kapatma / gizleme | Hayır | Hayır | Evet |
| Kullanıcıları devre dışı bırakma | Hayır | Hayır | Evet |
| E-posta bilgisine erişim | Hayır | Yalnızca kendi hesap bilgisi | Yetkili yönetim ekranında |

Oy verenlerin kimlikleri veya hangi kişinin hangi seçeneğe oy verdiği herkese açık gösterilmez. Yönetim yetkileri yalnızca gerekli personele verilir.

## 6. Ekranlar ve kullanıcı akışları

### 6.1. Ana sayfa / keşfet

- Üst bölümde Kararsızım logosu veya yazı logosu.
- Navigasyon: “Keşfet”, “Anket oluştur”; misafire “Giriş yap” ve “Üye ol”; üyeye kullanıcı adı, “Anketlerim” ve “Çıkış yap”.
- Kısa başlık: “Aklındaki soruyu topluluğa sor.”
- Yardımcı metin: “Oylamak için üye olmana gerek yok.”
- Ana eylem: “Anket oluştur”.
- Her kartta soru, `@kullaniciadi`, oluşturulma zamanı, toplam oy ve açık/kapalı durumu.
- Karttan anket detayına geçilir. İlk sürümde oylama detay sayfasında yapılır; kart içi oylama şart değildir.
- Yeni anketler önce gelir. Aynı tarihli kayıtlar için ID ile kararlı sıralama uygulanır.
- Kapatılmış anketler listelenebilir; kaldırılmış ve gizlenmiş olanlar listelenmez.
- Sayfalama kullanılır; sonsuz kaydırma zorunlu değildir.
- Boş durum: “Henüz anket yok. İlk soruyu sen sor!”

### 6.2. Anket detay sayfası

- Soru başlık olarak, açıklama varsa hemen altında.
- Oluşturan kullanıcının adı; e-posta hiçbir HTML alanında bulunmaz.
- İki ile beş arasında büyük, tıklanabilir seçenek; semantik radio input kullanılır.
- Seçim yapılmadan “Oy ver” butonu devre dışı görünür; sunucu boş gönderimi de reddeder.
- Başarılı oy sonrası “Oyun kaydedildi!” mesajı, seçilen seçenek işareti ve sonuçlar gösterilir.
- Sonuçlarda her seçenek için oy sayısı ve yüzde bulunur.
- Henüz oy yoksa tüm yüzdeler %0 gösterilir; sıfıra bölme hatası oluşmaz.
- Eşit sonuçlarda bir seçenek rastgele kazanan ilan edilmez.
- Yuvarlama nedeniyle toplam yüzdelerin %99 veya %101 olabileceği kabul edilir; kesin toplam oy sayısı doğru kalır.
- Önceden oy verildiyse yeni oy formu yerine oy durumu gösterilir.
- Kapalı ankette “Bu anketin oylaması sona erdi.” metni görünür.
- “Sonuçları gör” ve gerekirse “Seçeneklere dön” bağlantıları bulunur.
- Anket sahibine “Oylamayı kapat” ve “Anketi kaldır” eylemleri sunulur; ikisi de açıklayıcı onay adımı içerir.
- Adres çubuğundaki URL paylaşılabilir. Ayrı sosyal paylaşım entegrasyonu gerekmez.

### 6.3. Kayıt

Alanlar: kullanıcı adı, e-posta, parola, parola tekrar.

- Kullanıcı adı: 3–24 karakter; ilk sürümde küçük Latin harfleri, rakamlar ve alt çizgi (`a-z`, `0-9`, `_`).
- Başındaki ve sonundaki boşluklar temizlenir; büyük Latin harfleri küçüğe dönüştürülür. Türkçe harflerin kullanıcı adında desteklenmediği alan yardımında açıkça yazılır. Soru ve açıklamalarda Türkçe karakterler tamamen desteklenir.
- Kullanıcı adı benzersizdir; `Burak` ve `burak` ayrı hesaplar olamaz.
- E-posta zorunlu, biçimi geçerli ve büyük/küçük harften bağımsız benzersiz olmalıdır.
- Parola en az 8 karakter olmalı; Django'nun yaygın parola, tamamen sayısal parola ve kullanıcı bilgisine benzerlik kontrolleri etkin olmalı.
- Parola düz metin saklanmaz; Django'nun parola oluşturma mekanizması kullanılır.
- Form hataları alanların yanında gösterilir; girilen kullanıcı adı ve e-posta korunur, parola yeniden doldurulmaz.
- Kayıt sonrası kullanıcı oturumu açılır ve güvenli `next` hedefi varsa oraya, yoksa ana sayfaya gidilir.
- Yardım metni: “Anketlerinde kullanıcı adın görünür. E-posta adresin diğer kullanıcılara gösterilmez.”

### 6.4. Giriş ve çıkış

- Kullanıcı adı ve parola ile giriş yapılır.
- Hatalı girişte: “Kullanıcı adı veya parola hatalı.”
- Oturum Django tarafından yönetilir; JWT veya tarayıcı localStorage içinde oturum tokenı gerekmez.
- Çıkış işlemi CSRF korumalı POST ile yapılır.
- Misafir “Anket oluştur” seçerse giriş/kayıt sayfasına yönlendirilir; işlem sonrası oluşturma sayfasına geri döner.
- `next` parametresi yalnızca izin verilen aynı site adreslerine yönlendirebilir.

### 6.5. Anket oluşturma

| Alan | Kural |
|---|---|
| Soru | Zorunlu; boşluklar temizlendikten sonra 10–200 karakter |
| Açıklama | İsteğe bağlı; en fazla 500 karakter |
| Seçenek metni | Zorunlu; boşluklar temizlendikten sonra 1–100 karakter |
| Seçenek adedi | En az 2, en fazla 5 |

- Başlangıçta iki seçenek alanı gösterilir.
- “Seçenek ekle” ile beşe kadar çıkılır; beşincide ekleme düğmesi devre dışı kalır.
- İkiden fazla seçenek varken seçenek kaldırılabilir.
- Boşlukları temizlenmiş, harf büyüklüğü dışında aynı seçenekler kabul edilmez. Emoji kullanılabilir.
- Ön yüzdeki kısıtlar sunucuda da uygulanır; JavaScript veya form alanları değiştirilerek aşılamaz.
- JavaScript kapalıyken beş sabit alan ve “en az ikisini doldur” yardımıyla temel oluşturma akışı çalışabilir. Tamamen boş ek satırlar atlanır; geçerli seçenek sayısı yeniden hesaplanır.
- Yayınlama öncesi bilgi: “Yayınlandıktan sonra soru ve seçenekleri değiştiremezsin.”
- Başarılı yayınlama sonrası yeni anketin detay sayfasına yönlendirilir.
- Anket ve tüm seçenekleri tek veritabanı işlemi içinde kaydedilir; yarım kayıt oluşmaz.
- Hata durumunda doldurulmuş alanlar korunur.

### 6.6. Anketlerim

- Yalnızca oturum sahibinin anketleri listelenir.
- Açık/kapalı durum, toplam oy, detay bağlantısı ve yönetim eylemleri gösterilir.
- Kaldırılmış anketler normal listede gösterilmez; geri yükleme ilk sürümde yoktur.
- Boş durum: “Henüz bir anket oluşturmadın. İlk sorunu paylaş!”

### 6.7. Yönetim ve hata ekranları

- Ayrı yönetim paneli geliştirmek yerine Django admin kullanılır.
- Yönetici uygunsuz anketi gizleyebilir, oylamayı kapatabilir, hesabı devre dışı bırakabilir.
- Oy verildikten sonra seçenekleri admin üzerinden değiştirmek veya silmek de engellenir; ilk sürümde yayınlanmış soru ve seçenekler salt okunurdur.
- Gizlenmiş/kaldırılmış bir anketin herkese açık adresi 404 döndürür.
- 403, 404, CSRF hatası ve 500 ekranları Türkçe, anlaşılır ve ana sayfaya dönüş bağlantılı olur.
- Kullanıcıya traceback, veritabanı bağlantı bilgisi veya gizli anahtar gösterilmez.

## 7. Oylama kuralları ve misafir kimliği

### 7.1. Temel doğrulamalar

Oy isteği yalnızca POST kabul eder. Sunucu şu kontrolleri yapar:

1. Anket mevcut mu, görünür mü ve oylaması açık mı?
2. Gönderilen seçenek gerçekten bu ankete mi ait?
3. Üyeyse bu hesap, misafirse bu tarayıcı kimliği daha önce bu ankete oy verdi mi?
4. İstek CSRF ve form doğrulamasından geçti mi?

Başkasının anketindeki bir seçenek ID'si gönderildiğinde istek reddedilir. Aynı isteğin tekrar gönderilmesi oy toplamını artırmaz. Kullanıcı ID'si veya misafir kimliği formdan güvenilerek alınmaz.

### 7.2. Sade prototip çözümü

**Kesinleşen karar (20 Ekim 2026):** Üyelerde hesap başına, misafirlerde tarayıcı kimliği başına tek oy uygulanır. Farklı kayıtlı hesaplar aynı tarayıcıdan ayrı ayrı oy verebilir.

- Sunucu, tarayıcı için tahmin edilemeyen rastgele bir kimlik üretir; Django imzalı, `HttpOnly`, `SameSite=Lax` çerezinde tutar. HTTPS ortamında `Secure` etkin olur.
- Bu kimlik oturum çerezinden ayrıdır; giriş veya çıkışta sıfırlanmaz. Önerilen süre 180 gündür.
- Veritabanına ham çerez yerine kimliğin sunucu anahtarıyla üretilmiş özeti yazılır. Bu değer kullanıcıya özel kişisel profil oluşturmak için kullanılmaz.
- Misafir oyunda tarayıcı özeti, üye oyunda kullanıcı ilişkisi bulunur. Misafirden devralınan oyda kaynak tarayıcı özeti tutulabilir; bu değer başka üyelerin oy hakkını kısıtlamaz.
- Misafir oyları için aynı anket ve tarayıcı özeti; üye oyları için aynı anket ve kullanıcı benzersizdir. Tarayıcı özeti bütün üye oyları için ortak benzersizlik anahtarı değildir.
- Giriş yapmış üye başka cihazda da aynı ankete ikinci kez oy veremez.
- Giriş sırasında o tarayıcıdaki sahipsiz misafir oyları giriş yapılan hesaba bağlanır. Hesap aynı ankete zaten oy vermişse hesap oyu korunur, misafir oyu kaldırılır; toplam oy buna göre azalır.
- Aktarım ve çakışma çözümü tek işlem içinde yapılır. Bir hesaba bağlanmış oy başka hesaba aktarılmaz. Aynı tarayıcıda daha sonra açılan farklı hesap kendi oyunu kullanabilir.
- İlk misafir oyu gönderilmeden önce misafir kimlik çerezinin tarayıcıdan geri geldiği doğrulanır. Kimlik çerezi yoksa önce kimlik oluşturulup form tekrar gösterilir; kimliksiz POST doğrudan oy oluşturmaz.
- Çerezleri engelleyen ziyaretçi anketi ve sonuçları görebilir; oy için “Oy verebilmek için site çerezlerine izin vermelisin.” mesajı alır.

**Ortak tarayıcı davranışı:** İki farklı kayıtlı hesap ayrı ayrı oy verebilir. Sahipsiz misafir oylarının ilk giriş yapan hesaba bağlanacağı giriş ekranında açıklanır. Tarayıcıyı paylaşan kişilerin gerçekten aynı kişi olup olmadığı doğrulanmaz.

**Sınırlar:** Çerezi silmek, gizli pencere açmak, başka tarayıcı kullanmak veya misafir olarak başka cihazdan gelmek tekrar oy vermeyi mümkün kılabilir. Aynı insanın farklı kimliklerle oy vermesini kesin engelleme garantisi yoktur. “Kişi başına kesin tek oy” iddiası kullanılmaz. IP adresi tek başına kimlik kabul edilmez; cihaz parmak izi çıkarılmaz.

### 7.3. Eşzamanlı istekler

- “Daha önce oy var mı?” sorgusu tek başına yeterli değildir; veritabanı benzersizlik kısıtları da gerekir.
- Oy kaydı `transaction.atomic()` içinde oluşturulur; benzersizlik hatası kullanıcıya anlaşılır “Bu ankete zaten oy verdin.” yanıtına çevrilir.
- Oylamayı kapatma ile oy verme yarışını önlemek için oy verme ve kapatma işlemleri aynı anket satırını işlem içinde kilitler, durumu kilit altında kontrol eder.
- Form gönderildikten sonra detay sayfasına yönlendirme yapılır; sayfa yenileme yeni oy üretmez.
- İlk sürümde oy sayıları Vote kayıtlarından hesaplanır. Ayrı bir sayaç alanı tutularak tutarsızlık riski eklenmez.

## 8. Arayüz ve görsel dil

### 8.1. Tasarım yönü

Açık zemin, beyaz kartlar, belirgin mor ana eylemler ve küçük mercan/mint vurgular. Eğlenceli ama okunaklı; büyük boşluklar ve anlaşılır etkileşimler. Ağır animasyonlar, kalabalık paneller ve yoğun gradyanlar kullanılmaz.

Önerilen başlangıç renkleri:

| Amaç | Değer |
|---|---|
| Sayfa zemini | `#F8F7FC` |
| Kart yüzeyi | `#FFFFFF` |
| Ana metin | `#202033` |
| İkincil metin | `#5F6074` |
| Ana renk / buton | `#6D28D9` |
| Ana renk hover | `#5B21B6` |
| Hafif mor yüzey | `#F0EAFE` |
| Mercan vurgu | `#FF785A` |
| Mint vurgu | `#B8F2DF` |
| Kenarlık | `#E5E3EF` |
| Başarı metni | `#137A55` |
| Hata metni | `#B42318` |

Mercan ve mint renkleri varsayılan olarak dekoratif yüzeylerde kullanılır; üzerlerine beyaz küçük metin koyulmaz. Son renk çiftlerinin kontrastı geliştirme sırasında kontrol edilir.

### 8.2. Yerleşim ve bileşenler

- Mobil öncelikli tasarım; yaklaşık 360, 768 ve 1280 piksel genişliklerde kontrol.
- Sayfa içerik genişliği en fazla yaklaşık 1100 piksel; form ve anket detayı yaklaşık 680 piksel.
- Akış mobilde tek, geniş ekranda iki sütun olabilir; görsel sıra okuma sırasıyla tutarlı olmalı.
- Mobil yatay boşluk yaklaşık 16 piksel; genel boşluk sistemi 4/8/12/16/24/32 piksel.
- Kartlarda yaklaşık 16–20 piksel köşe yarıçapı, ince kenarlık ve çok hafif gölge.
- Gövde metni en az 16 piksel; sistem font ailesi yeterli. Harici font zorunlu değil.
- Seçenekler büyük tıklama alanına sahip olmalı; yalnızca küçük radio noktası hedef olmamalı.
- Etkileşim alanları mümkün olduğunca en az 44×44 piksel olmalı.
- Ortak bileşenler: navbar, buton, anket kartı, form alanı, hata özeti, durum rozeti, sonuç çubuğu, sayfalama ve boş durum.
- CSS değişkenleriyle renkler ve aralıklar merkezi tutulmalı.

### 8.3. Erişilebilirlik ve durumlar

- Formlarda gerçek `label`, radio gruplarında `fieldset` ve `legend` kullanılır.
- Klavyeyle gezinme, görünür odak ve Enter/Space davranışları çalışır.
- Seçim veya hata yalnızca renkle anlatılmaz; metin ve işaret de bulunur.
- Başarı mesajı erişilebilir durum alanında duyurulur; hata özeti ilgili alanlara bağlanır.
- Normal metinde en az 4.5:1 kontrast hedeflenir.
- Animasyon varsa kısa tutulur ve `prefers-reduced-motion` tercihi dikkate alınır.
- Uzun soru, uzun seçenek, emoji, Türkçe karakter ve 200 karakterlik başlık yerleşimi bozmaz.
- Sayfa yükleniyor, işlem sürüyor, boş sonuç, doğrulama hatası ve sunucu hatası durumları tasarlanır.
- JavaScript başarısız olsa da görüntüleme, giriş, normal form gönderimi ve oylama çalışır.

## 9. Teknik mimari

```text
Tarayıcı
  HTML + CSS + küçük JavaScript dosyaları
       |
       | HTTPS, Django sayfaları ve form POST istekleri
       v
Django — Vercel üzerinde
  URL yönlendirme / view / form / template
  Django Auth / session / admin
  Anket ve oy iş kuralları
       |
       | Django ORM + PostgreSQL sürücüsü
       v
Supabase PostgreSQL
  Kullanıcılar / anketler / seçenekler / oylar / oturumlar
```

### 9.1. Temel tercihler

- Django templates ile sunucuda HTML üretimi.
- Django Forms/ModelForms ve gerektiğinde formset; gereksiz REST API katmanı yok.
- JavaScript yalnızca seçenek ekleme/kaldırma ve küçük kullanılabilirlik iyileştirmeleri için.
- Django Auth kullanıcı ve parola yönetimini üstlenir; Supabase yalnızca PostgreSQL hizmeti olarak kullanılır.
- Supabase Auth, Supabase JavaScript istemcisi ve `supabase-py` bu mimarinin zorunlu parçaları değildir.
- Tarayıcı doğrudan Supabase tablolarına bağlanmaz.
- Django'nun veritabanı destekli session altyapısı kullanılır; süreç belleğine dayalı oturum tutulmaz.
- İş kuralları birkaç okunaklı view/form ve küçük bir `services.py` içinde toplanabilir. Katman sayısı ihtiyaçtan fazla artırılmaz.
- Şema değişikliklerinin uygulama tarafındaki tek kaynağı Django migration dosyalarıdır. Aynı tablolar için ayrı, çakışan migration sistemi kurulmaz.
- İlk migration öncesinde `AbstractUser` tabanlı özel User modeli ve `AUTH_USER_MODEL` tanımlanır. [Django kullanıcı modeli rehberi](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project)

### 9.2. Bağımlılıklar ve sürümler

Başlangıç için Django, PostgreSQL sürücüsü (`psycopg`) ve ihtiyaç halinde ortam değişkenlerini okumayı kolaylaştıran tek bir küçük yardımcı paket yeterlidir. Testler Django'nun test araçlarıyla yazılabilir.

Uygulamaya başlanırken desteklenen Python/Django sürüm çifti ve Vercel uyumu resmi belgelerden doğrulanmalı; seçilen sürümler README'ye yazılmalı ve bağımlılıklar tekrarlanabilir biçimde sabitlenmelidir. Bu belge belirli bir yama sürümünü geleceğe dönük varsaymaz.

İlk sürümde React, Next.js, Vue, ayrı SPA, Django REST Framework, GraphQL, Redis, Celery, Docker zorunluluğu, mikroservis, Kubernetes veya WebSocket eklenmez. CSS framework, npm tabanlı frontend derleme zinciri ve TypeScript de gerekli değildir. Vercel CLI'nin araç bağımlılıkları ayrı frontend mimarisi anlamına gelmez.

### 9.3. Önerilen repo yapısı

```text
kararsizim/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── docs/
│   ├── PROJE_DURUMU.md
│   ├── verification/
│   └── KARARSIZIM_PROJE_PLANI_VE_PROMPT.md
├── scripts/
│   ├── configure_local.py
│   └── test_configure_local.py
├── config/
│   ├── settings.py
│   ├── environment.py
│   ├── migration_settings.py
│   ├── check_settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── management/commands/verify_database.py
│   ├── migrations/
│   └── tests/
├── polls/
│   ├── models.py
│   ├── forms.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   └── tests/
├── templates/
│   ├── base.html
│   ├── accounts/
│   ├── polls/
│   ├── components/
│   ├── 403.html
│   ├── 404.html
│   └── 500.html
└── static/
    ├── css/style.css
    └── js/polls.js
```

Bu yapı fazlar tamamlandığındaki hedef için yol göstericidir; Faz 2'de üyelik view'ları, anket modelleri/formları ve oy JavaScript'i mevcuttur. Hata sayfaları ortak error.html template'ini kullanır. Standart Django dosyaları gerektiğinde eklenir. Dağıtım yapılandırma dosyaları güncel Vercel ihtiyacına göre eklenir; gereksiz eski `vercel.json` şablonları baştan kopyalanmaz.

## 10. Veri modeli

### User

`AbstractUser` temel alınır. `username`, `email`, `password`, `date_joined`, `is_active` ve yetki alanları kullanılır.

- `username` zorunlu, normalize edilmiş ve benzersiz.
- `email` zorunlu; uygulama normalizasyonu ve veritabanı düzeyindeki harf büyüklüğünden bağımsız benzersizlik birlikte uygulanır.
- `password` Django hash alanıdır; ayrı bir düz metin parola alanı oluşturulmaz.
- İlk sürüm için avatar, biyografi ve takip ilişkileri eklenmez.

### Poll

| Alan | Açıklama |
|---|---|
| `id` | Birincil anahtar |
| `author` | User ilişkisi |
| `question` | En fazla 200 karakter |
| `description` | En fazla 500 karakter; boş olabilir |
| `created_at` | Yayınlama zamanı |
| `closed_at` | Boşsa açık, doluysa oylama kapalı |
| `deleted_at` | Sahip kaldırdıysa dolu |
| `hidden_at` | Yönetici gizlediyse dolu |

Görünürlük `deleted_at` ve `hidden_at` üzerinden; oylama açıklığı buna ek olarak `closed_at` üzerinden belirlenir. Çelişen birden fazla durum alanı eklenmez. Kullanıcı hesabını kalıcı silme ilk sürüm kapsamında değildir; yönetici hesabı devre dışı bırakabilir.

### Choice

| Alan | Açıklama |
|---|---|
| `id` | Birincil anahtar |
| `poll` | Poll ilişkisi |
| `text` | En fazla 100 karakter |
| `position` | 1–5 arasında görüntüleme sırası |

`poll + position` benzersizdir. İki-beş seçenek ve yinelenen metin kontrolü kayıt servisinde/form doğrulamasında yapılır. Toplam ilişkili kayıt sayısını basit bir satır `CHECK` kısıtıyla doğrulayabildiğini varsayma. Admin üzerinden bu kuralların aşılmasını engelle.

### Vote

| Alan | Açıklama |
|---|---|
| `id` | Birincil anahtar |
| `poll` | Poll ilişkisi |
| `choice` | Seçilen Choice ilişkisi |
| `user` | Üye ise User; misafir ise NULL |
| `guest_identity_hash` | Misafir için zorunlu tarayıcı kimliği özeti; doğrudan üye oyunda boş olabilir |
| `created_at` | Oy zamanı |

Kısıtlar:

- Yalnızca `user` boş olan misafir oylarında `poll + guest_identity_hash` benzersiz; misafir kimliği boş olamaz.
- `user` boş değilken `poll + user` benzersiz.
- Misafir oyunu hesaba bağlama ve hesapta mevcut oy varsa misafir kaydını kaldırma Faz 2'de aynı işlem içinde uygulanır. Aktarılmış kayıtlar başka hesaba taşınmaz.
- `choice.poll_id == poll_id` eşitliği sunucuda, tek oy yazma yolunda doğrulanır; iki ayrı foreign key bu eşitliği kendiliğinden sağlamaz.
- Oylar uygulama ve admin üzerinden keyfi değiştirilemez; sonuçlar gerçek Vote kayıtlarından üretilir.
- Akış için tarih/ID, kullanıcı anketleri için author/tarih sorguları dikkate alınarak az sayıda uygun indeks eklenir.
- Liste sorguları `select_related`, `prefetch_related` veya uygun toplu sayımlarla kart başına tekrar eden sorgular üretmeyecek şekilde yazılır. Karmaşık önbellekleme eklenmez.

## 11. Sayfa adresleri

| Adres | Yöntem | Amaç |
|---|---|---|
| `/` | GET | Herkese açık anket akışı |
| `/anket/<id>/` | GET | Detay / sonuçlar |
| `/anket/<id>/oy/` | POST | Oy kaydetme |
| `/anket/olustur/` | GET, POST | Üyeye özel oluşturma formu |
| `/anket/<id>/kapat/` | POST | Sahibi veya yönetici oylamayı kapatır |
| `/anket/<id>/kaldir/` | POST | Sahibi veya yönetici kaldırır |
| `/anketlerim/` | GET | Oturum sahibinin anketleri |
| `/uye-ol/` | GET, POST | Kayıt |
| `/giris/` | GET, POST | Giriş |
| `/cikis/` | POST | Çıkış |
| `/admin/` | Django admin | Yetkili yönetim |

GET istekleri oy, silme veya kapatma yapmaz. İstenirse onay sayfaları için ayrıca GET görünümü eklenir; değişiklik yalnızca POST aşamasındadır.

## 12. Supabase ve Vercel uygulama notları

Bu bölüm geliştirme sırasında yeniden kontrol edilmesi gereken platform kararlarını içerir. Plan veya kullanım kotası hakkında ücretsiz/sınırsız çalışma garantisi verilmez.

### 12.1. Supabase PostgreSQL

- Bağlantı adresi Supabase panelinden alınır; bölgeden tahmin edilmez.
- Vercel çalışma zamanı için transaction pooler; migration için doğrudan bağlantı, IPv4 kısıtı varsa uyumlu session pooler değerlendirilir.
- SSL etkin olur; çalışma zamanı için başlangıç tercihi `CONN_MAX_AGE=0` olur.
- Transaction pooling kullanılırken sunucu tarafı cursor'lar kapatılır; sürücüde prepared statement davranışı doğrulanır. `psycopg` 3 kullanılıyorsa uygun ayar `prepare_threshold=None` olabilir; seçilen sürümle test edilir.
- Çalışma zamanı ve migration bağlantısı ayrı ortam değerleri olabilir. Gerçek bağlantı/parola belgeye veya sohbete yapıştırılmaz.

Kaynaklar: [Supabase bağlantı seçenekleri](https://supabase.com/docs/guides/database/connecting-to-postgres), [Django transaction pooling ve cursor açıklaması](https://docs.djangoproject.com/en/5.2/ref/databases/#transaction-pooling-and-server-side-cursors).

Bu proje için ayrı bir Supabase projesinde kullanılmayan **Data API kapalı tutulmalı**. Açık kalması gerekiyorsa Django tabloları API'ye açılmayan şemada tutulmalı veya açık şemadaki tablolarda RLS ve rol izinleri açıkça düzenlenmeli. Kullanıcı, parola hash'i ve session tabloları API üzerinden erişilebilir olmamalı. Django oturumu, Supabase Auth oturumu değildir; `auth.uid()` kendiliğinden Django kullanıcısını temsil etmez. Django ORM üzerinden çalışan sahiplik kontrolleri ayrıca zorunludur. [Supabase API güvenliği](https://supabase.com/docs/guides/api/securing-your-api)

### 12.2. Vercel

Güncel resmi rehber Django projeleri için yerleşik algılama ve WSGI/ASGI giriş noktası desteği tarif ediyor. Prototip WSGI ile ilerleyebilir. `STATIC_ROOT` tanımlandığında statik dosyaların derleme sırasında toplanması ve CDN'den sunulması destekleniyor. Bu nedenle sırf eski örneklerde var diye özel adaptör veya WhiteNoise ekleme. Dağıtım sırasında güncel akışı doğrula. [Vercel Django rehberi](https://vercel.com/docs/frameworks/full-stack/django)

Proje kararları:

- Kalıcı veri PostgreSQL'de tutulur; dağıtım dosya sistemine SQLite veya kalıcı kullanıcı verisi yazılmaz.
- Kullanıcı dosya yüklemesi prototipte yoktur.
- Migration her HTTP isteğinde veya her paralel preview build içinde otomatik çalıştırılmaz; kontrollü bir yönetim adımıdır.
- Preview ve production gizli değerleri ayrı tutulur. Preview veritabanı gerçek production verisini değiştirmemelidir.
- İlk demo için yalnızca prototipe ayrılmış Supabase veritabanı kullanılabilir; gerçek kullanıcılara açılırken ortam ayrımı yapılır.
- `ALLOWED_HOSTS`, HTTPS içeren `CSRF_TRUSTED_ORIGINS` ve proxy güven ayarları kullanılan alan adlarına göre yapılandırılır; gelişigüzel wildcard kullanılmaz.
- HTTPS ortamında güvenli cookie ayarları ve `DEBUG=False` doğrulanır.
- Derleme sırasında veritabanını değiştiren veya demo verisi yükleyen yan etkiler bulunmaz.

### 12.3. Ortam değişkenleri

`.env.example` yalnızca açıklayıcı yer tutucular içerir:

```dotenv
DJANGO_SECRET_KEY=<yerel-olarak-uretilen-gizli-deger>
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000
DATABASE_URL=<supabase-postgresql-runtime-baglantisi>
DATABASE_MIGRATION_URL=<gerekiyorsa-ayri-migration-baglantisi>
GUEST_VOTE_HASH_KEY=<yerel-olarak-uretilen-ayri-gizli-deger>
```

Bu isimler uygulamanın okuyacağı ayarlardır; Django bunların hepsini otomatik yorumlamaz. Boolean ve liste ayrıştırması açık yazılmalı; `"false"` metni yanlışlıkla doğru kabul edilmemeli. Migration URL'sinin hangi komutla kullanılacağı README'de anlatılmalı.

`.env`, `.env.local`, sanal ortam ve erişim bilgileri Git'e eklenmez. Production'da gerekli değişken eksikse sessizce SQLite'a veya güvensiz varsayılanlara düşülmez. Anahtar yenilemenin mevcut misafir kimlik özetlerini etkileyebileceği bakım notunda belirtilir.

## 13. Güvenlik ve veri görünürlüğü

Prototip basit olabilir; temel doğrulamalar ertelenmez.

- Tüm durum değiştiren form isteklerinde CSRF koruması.
- Kullanıcı içeriklerinde Django template escaping; kullanıcı metnine `safe` uygulanmaz, HTML kabul edilmez.
- Soru ve seçenek doğrulaması hem istemcide hem sunucuda.
- Anket oluşturucusu `request.user` üzerinden belirlenir; formdaki author ID'sine güvenilmez.
- Kapatma/kaldırmada sunucu tarafında sahiplik kontrolü; butonu gizlemek tek başına yetkilendirme değildir.
- E-posta adresi anket HTML'ine, gizli inputlara, `data-*` alanlarına veya varsa JSON yanıtına eklenmez.
- Parolalar, tam bağlantı adresleri ve çerez kimlikleri loglara yazılmaz.
- Kayıt/giriş/oy POST isteklerini kişiye özel yanıtlarla birlikte ortak CDN önbelleğine alma. Kullanıcıya göre değişen sayfalar için uygun cache başlıklarını kullan.
- Gizli anahtarlar frontend koduna gönderilmez; bu mimaride tarayıcı için Supabase API anahtarı da gerekmez.
- Devre dışı hesapların yeni giriş ve anket oluşturma işlemleri engellenir.
- Test ve örnek verileri gerçek e-posta/parola içermeyen geliştirme verileridir.

Kontrollü prototipte temel admin moderasyonu yeterlidir. Herkese açık büyüme öncesinde giriş ve kayıt denemeleri, anket oluşturma ve aşırı oy istekleri için hız sınırlama eklenir. Vercel'de süreç belleğindeki sayaçların bütün sunucular için ortak olmadığı dikkate alınır; ihtiyaç kanıtlanmadan Redis gibi ek hizmet kurulmaz. Hız sınırlama yoksa prototipin bu eksikliği dürüstçe kaydedilir.

## 14. Prototip dışında bırakılanlar

- Takip mekanizması, takipçi sayısı ve takip edilenler akışı: ürün talebi gereği kapsam dışı.
- Yorumlar, özel mesajlar, beğeni sistemi, rozetler ve puanlar.
- Görsel/video yükleme, görselli seçenekler.
- Kategori, etiket, arama, gelişmiş filtre ve popülerlik algoritması.
- Sosyal hesapla giriş, mobil uygulama ve push bildirimleri.
- AI ile karar verme, soru yazdırma veya sonuç yorumlama.
- Reklam, ödeme, premium üyelik.
- Otomatik süre dolumu, görev kuyruğu ve gerçek zamanlı sonuç altyapısı.

Proje ChatGPT ile geliştirilecek olsa da uygulamanın içinde bir AI özelliği olması gerekmiyor.

## 15. Geliştirme fazları

### Faz 1 — Temel kurulum ve ilk ekran

**Amaç:** Mimariyi doğru kurmak ve tarayıcıda ilk çalışan sayfayı görmek.

İşler:

- Python/Django sürüm uyumunu kontrol et ve sürümleri sabitle.
- Django projesi, `accounts` ve `polls` uygulamalarını oluştur.
- İlk migration öncesinde özel User modelini tanımla.
- Supabase PostgreSQL bağlantısını, ortam ayarlarını ve `.env.example` dosyasını hazırla.
- Uygun veritabanında migration uygula; erişim yoksa yapılmamış adımı açıkça belirt.
- Temel template, navbar, renk değişkenleri ve boş anket akışı ekranını oluştur.
- README'ye Windows PowerShell kurulum/çalıştırma komutları ekle.
- `docs/PROJE_DURUMU.md` dosyasını oluştur.

**Bitti sayılması:** Geliştirme sunucusu açılır, boş ana sayfa düzgün görünür, veritabanı bağlantısı ve kullanıcı migration'ı doğrulanır. Henüz üyelik/oylama tamamlanmış sayılmaz.

### Faz 2 — Çalışan ürün prototipi

**Amaç:** Baştan sona gerçek veriye dayalı temel deneyim.

İşler:

- Kayıt, giriş, çıkış ve özel Anketlerim sayfası.
- Poll, Choice, Vote modelleri ve migration'lar.
- İki-beş seçenekli anket oluşturma.
- Herkese açık akış, detay ve sonuç ekranı.
- Misafir ve üye oylaması; çerez, benzersizlik ve işlem kuralları.
- Sahip için kapatma/kaldırma; admin için gizleme.
- Temel iş kurallarını doğrulayan testler.

**Bitti sayılması:** Bir kişi üye olup anket yayınlar; oturumu olmayan başka bir tarayıcı bunu görüp oy verir; sonuç veritabanında kalır. Yetkisiz değişiklik ve aynı kimlikle tekrar oy engellenir. Bu faz sonunda yerel çalışan prototip vardır.

### Faz 3 — Tasarım, kullanılabilirlik ve sağlamlaştırma

**Amaç:** Prototipi sunulabilir ve rahat kullanılabilir hale getirmek.

İşler:

- Tasarım bölümüne uygun kartlar, formlar ve sonuç çubukları.
- Mobil yerleşim, klavye erişimi ve kontrast kontrolü.
- Türkçe başarı/hata/boş durumlar ve uzun içerik kontrolleri.
- JavaScript kapalı temel akış ve çift gönderim kontrolleri.
- Yetki, gizlilik, eşzamanlı oy ve kapatma testlerini tamamla.
- Gerekli sorgu iyileştirmeleri ve yalnızca geliştirme ortamına örnek veri ekleme komutu.

**Bitti sayılması:** Temel akışlar mobil ve masaüstünde denenir; 16. bölümdeki prototip kontrolleri geçer veya ortam nedeniyle denenemeyenler açıkça listelenir. Dış hizmet doğrulaması yapılmadıysa bu faza ait iddialar sınırlandırılır.

### Faz 4 — Vercel üzerinde denenebilir prototip

**Amaç:** Yereldeki prototipi paylaşılabilir bir ortamda çalıştırmak.

İşler:

- Güncel resmi Django dağıtım rehberine uygun giriş ve statik dosya ayarları.
- Vercel ortam değişkenleri, Supabase pooler uyumu ve veri erişimi kontrolü.
- Migration'ların kontrollü uygulanması; demo verisinin üretime kendiliğinden taşınmaması.
- Preview dağıtımı ve gerçek URL üzerinde üyelik → anket → misafir oy → sonuç akışı.
- HTTPS, CSRF, statik dosyalar ve hata sayfalarının kontrolü.
- Dağıtım, tekrar dağıtım ve sorun giderme adımlarını README'ye ekle.

**Bitti sayılması:** Erişilebilir prototip URL'sinde ana akış çalışır; oturum ve oylar yeni istekler arasında korunur; e-posta ve gizli değerler sızmaz. Hesap/erişim engeli varsa dağıtım yapılmış sayılmaz.

Preview platform koruması kullanılıyorsa linki açacak test kullanıcılarının buna erişimi ayrıca kontrol edilir. Platform erişim koruması, uygulamanın üyeliksiz oy verebilme kuralından farklıdır.

### Faz 5 — Kullanıcı geri bildirimi ve daha geniş kullanım (sonraki çalışma)

Bu faz prototipin bitmesi için şart değildir. Geri bildirime göre küçük işlere bölünür:

- E-posta doğrulama, parola sıfırlama ve gerçek e-posta gönderimi.
- Hız sınırlama, spam kontrolü, raporlama ve moderasyon süreci.
- Hesap/veri silme akışı ve kullanıcıya anlaşılır gizlilik/çerez açıklamaları.
- Hata izleme, yedekleme ve geri yükleme denemesi.
- İhtiyaca göre arama, kategoriler veya süreli anketler.
- Misafir oy politikasının gerçek kullanım verisine göre yeniden değerlendirilmesi.

Takip sistemi sonradan da kendiliğinden eklenmez. Yeni özellikler ayrı bir kullanıcı talebi ve kapsam kararıyla ele alınır.

## 16. Kabul kriterleri ve test senaryoları

Testler davranışı doğrulamalı; yalnızca kodun yazılmış olduğunu kontrol eden gereksiz testler üretilmemeli. PostgreSQL'e özgü benzersizlik ve eşzamanlılık davranışları PostgreSQL üzerinde doğrulanmalı. Otomatik testler canlı/prototip veritabanını temizlememeli; izole bir test veritabanı kullanmalı. Test veritabanı oluşturma yetkisi yoksa bu engel ve güvenli çözüm açıklanmalı.

| No | Senaryo | Beklenen |
|---|---|---|
| 1 | Misafir ana sayfayı açar | Üyelik duvarı olmadan yayınlanmış anketleri görür |
| 2 | Misafir anket oluşturmaya çalışır | Giriş/kayıt akışına yönlenir; kayıt oluşturulmaz |
| 3 | Geçerli e-posta, kullanıcı adı ve parola ile kayıt | Hesap oluşturulur ve oturum açılır |
| 4 | Aynı kullanıcı adı veya harf büyüklüğü farklı aynı e-posta | İkinci hesap oluşmaz; uygun hata gösterilir |
| 5 | Bir veya altı seçenek gönderilir | Sunucuda reddedilir |
| 6 | İki veya beş geçerli seçenek gönderilir | Anket ve seçenekler birlikte oluşur |
| 7 | Boş, yinelenen veya fazla uzun seçenek | Açık alan hatası; yarım anket oluşmaz |
| 8 | Misafir geçerli seçenekle oy verir | Tek Vote kaydı ve doğru sonuç |
| 9 | Aynı kimlikle tekrar veya eşzamanlı oy istenir | Yalnızca bir oy sayılır |
| 10 | Üye başka cihazdan aynı ankete oy verir | Kullanıcı benzersizliğiyle ikinci oy engellenir |
| 11 | Misafir oyundan sonra giriş | Oy hesaba bağlanır; hesapta mevcut oy varsa misafir oyu kaldırılır |
| 12 | İlk kimlik çerezi olmayan POST | Kimlik oluşturulur; doğrudan oy yazılmaz |
| 13 | Başka ankete ait seçenek ID'si gönderilir | Reddedilir; toplamlar değişmez |
| 14 | Kapalı veya gizlenmiş ankete oy gönderilir | Oy oluşmaz |
| 15 | Oy verme ile kapatma aynı anda yapılır | Kilit sırasına uygun tutarlı sonuç; kapandıktan sonra yeni oy yok |
| 16 | Yetkisiz kişi başkasının anketini kapatır/kaldırır | Sunucu reddeder; veri değişmez |
| 17 | Anket sahibi kendi anketini kapatır | Sonuçlar görünür, oylama durur |
| 18 | Anket kaldırılır/gizlenir | Akıştan çıkar, herkese açık detay 404 döndürür |
| 19 | Anket HTML'i/yanıtları incelenir | Oluşturucunun e-postası, parola hash'i ve çerez özeti bulunmaz |
| 20 | Soruya script veya HTML yazılır | Kod çalışmaz; düz metin olarak güvenle görünür |
| 21 | CSRF olmadan POST gönderilir | Reddedilir |
| 22 | Sıfır oy, eşit oy ve farklı oy dağılımları | Sayılar doğru; yüzde hesaplaması hatasız |
| 23 | Başarılı POST sonrası sayfa yenilenir | Yeni kayıt/oy üretilmez |
| 24 | 360 piksel ekranda uzun Türkçe içerik | Yatay taşma olmadan kullanılabilir |
| 25 | Yalnızca klavye veya JavaScript kapalı kullanım | Temel gezinme ve form akışları çalışır |
| 26 | Vercel URL'si ve yeni tarayıcı oturumu | CSS/JS, kayıt, anket, misafir oy ve kalıcılık çalışır |
| 27 | Aynı tarayıcıda iki farklı kayıtlı hesap oy verir | Her hesap için bir ayrı oy kabul edilir |
| 28 | Misafir oyunu alan hesaptan çıkılıp başka hesaba girilir | Önceden aktarılmış oy yeni hesaba taşınmaz |

Aynı tarayıcıdaki farklı kayıtlı hesapların ayrı oy kullanabilmesi kesinleşmiş ürün kararıdır. Çerez silerek veya kimlik değiştirerek tekrar oy verme sınırlaması belgelenir; kesin kişi doğrulaması garantisi verilmez.

## 17. Her faz sonunda teslim edilecekler

1. Yapılan işin kısa özeti.
2. Oluşturulan/değiştirilen dosyalar.
3. Çalıştırma ve deneme komutları; varsayılan terminal Windows PowerShell.
4. Gerçekten çalıştırılan testler ve sonuçları.
5. Çalıştırılamayan kontroller ve gerekçeleri.
6. Bilinen eksikler, varsayımlar ve bir sonraki faz.
7. Güncellenmiş `docs/PROJE_DURUMU.md`.

Durum dosyası şu başlıkları taşımalı:

```markdown
# Kararsızım — Güncel Durum
## Tamamlanan faz ve işler
## Mevcut sürümler ve mimari kararlar
## Çalıştırma komutları
## Uygulanan migration'lar
## Yapılan testler ve sonuçları
## Bilinen eksikler / doğrulanmamış noktalar
## Sonraki adım
```

Bu dosyada sır, gerçek parola, erişim tokenı veya tam veritabanı bağlantısı bulunmaz.

## 18. ChatGPT için ana prompt

Aşağıdaki metni, bu Markdown belgesiyle birlikte kullan:

```text
Sen Kararsızım projesinde bana yardımcı olan deneyimli bir Python/Django
geliştiricisi ve ürün odaklı arayüz tasarımcısısın.

Eklediğim KARARSIZIM_PROJE_PLANI_VE_PROMPT.md belgesini projenin ana referansı
olarak oku. Amacımız önce çalışan, sade ve anlaşılır bir prototip oluşturmak.

Temel gereksinimler:
- Kullanıcılar en az 2, en fazla 5 seçenekli anketler oluşturur.
- Herkes yayınlanan anketleri görebilir ve üye olmadan oy verebilir.
- Anket oluşturmak için üyelik gerekir.
- Kayıtta kullanıcı adı, e-posta ve parola alınır; anketlerde yalnızca kullanıcı
  adı gösterilir, e-posta herkese açık değildir.
- Takip mekanizması yoktur.
- Python, Django, Supabase PostgreSQL, Vercel ve aynı repoda HTML/CSS/vanilla
  JavaScript kullanılır. Ayrı frontend framework kurulmaz.
- Django Auth üyelik ve oturumu yönetir; Supabase veritabanı olarak kullanılır.
- Açık arka planlı, canlı renk vurgulu, temiz ve mobil uyumlu Türkçe arayüz gerekir.

Çalışma biçimi:
1. Önce belgeyi ve varsa mevcut proje dosyaları ile docs/PROJE_DURUMU.md dosyasını oku.
2. Kullanıcının temel talepleriyle prototip varsayımlarını ayırt et. Sonradan
   verdiğim açık kararları belgede güncelle; eski varsayıma sessizce dönme.
3. Yalnızca seçtiğim fazı uygula; sonraki fazları kendiliğinden başlatma.
4. Seçilen fazın içindeki yetkilendirilmiş işleri gereksiz ara onaylar istemeden
   tamamla. Belirsiz küçük ayrıntılarda en sade seçeneği kullanıp varsayımı belirt.
5. Geri dönüşü zor, ücret doğuran veya mevcut veriyi etkileyen eksik bir karar
   varsa ilgili kısmı netleştir; bundan bağımsız işleri ilerlet.
6. Gereksiz paket, servis, mimari katman ve kapsam dışı özellik ekleme.
7. Güncel Python/Django, Supabase ve Vercel uyumunu resmi belgelerden doğrula.
   Gerekiyorsa kaynağı göster; doğrulayamadığın platform davranışını kesin sunma.
8. Dosya ve terminal erişimin varsa gerçek dosyaları düzenle ve ilgili kontrolleri
   çalıştır. Yoksa dosya yollarını, eksiksiz uygulanabilir içerikleri ve komutları
   ver. Henüz yazmadığın işlevi 'tamamlandı' diye anlatma.
9. Komutları Windows PowerShell için yaz. Komutun hangi klasörde çalışacağını
   ve beklenen çıktıyı açıkla. Terimleri gerektiği kadar, anlaşılır Türkçeyle anlat.
10. Parola, bağlantı adresi ve gizli anahtarları benden sohbete yapıştırmamı isteme;
    bunları kendi ortamıma güvenle ekleyeceğim adımları tarif et.
11. Misafir oylamasının kusursuz kişi doğrulaması olmadığını dikkate al. Belgede
    belirtilen tekrar oy politikasını ve eşzamanlılık kurallarını uygula.
12. CSRF, yetkilendirme, sunucu doğrulaması, e-posta gizliliği ve veritabanı
    benzersizliklerini prototip gerekçesiyle atlama.
13. Kod değişiklikleriyle birlikte anlamlı davranış testlerini çalıştır; gerçek
    test sonucunu, yapılamayan kontrolleri ve sınırlamaları ayrı belirt.
14. Her faz sonunda README ve docs/PROJE_DURUMU.md dosyasını güncelle; kısa bir
    teslim özeti ver ve sonraki faz talebimi bekle.

Şimdi sana ilettiğim faz promptuna göre işe başla.
```

## 19. Faz bazlı kopyalanabilir promptlar

### Faz 1 promptu

```text
Kararsızım belgesine göre yalnızca Faz 1'i uygula.

Mevcut klasörü incele; varsa dosyaları koruyarak ilerle. Django projesini,
accounts ve polls uygulamalarını, ilk migration öncesinde özel User modelini,
Supabase PostgreSQL yapılandırmasını, ortam değişkeni örneğini ve temel
template/static yapısını hazırla. Açık arka planlı, mor vurgulu boş anket akışı
ekranı oluştur. Henüz üyelik formlarını ve oy sistemini geliştirme.

Uyumlu sürümleri seçip sabitle; Windows PowerShell için kurulum ve çalıştırma
adımlarını README'ye ekle. docs/PROJE_DURUMU.md oluştur. Supabase erişimi yoksa
erişimsiz tamamlanabilecek dosyaları tamamla ve benim yapmam gereken bağlantı
adımını açıkla; bağlantı veya migration yapılmış gibi davranma.

Faz sonunda yaptıklarını, çalıştırdığın kontrolleri ve deneme adımlarını paylaş.
Faz 2'ye kendiliğinden geçme.
```

### Faz 2 promptu

```text
Kararsızım belgesini, mevcut kodu ve docs/PROJE_DURUMU.md dosyasını incele.
Yalnızca Faz 2'yi uygula; çalışan temeli gereksiz yere yeniden kurma.

Kayıt/giriş/çıkış, anket oluşturma, herkese açık liste ve detay, misafir ve üye
oylaması, sonuçlar, Anketlerim, sahibin kapatma/kaldırma işlemleri ve Django admin
moderasyonunu tamamla. İki-beş seçenek kuralını sunucuda uygula. E-postaları
herkese açık yanıtlara koyma. Belgede tarif edilen tarayıcı ve hesap temelli oy
benzersizliğini, çerez sürekliliğini ve eşzamanlı istek kontrollerini uygula.

Sade fakat kullanılabilir bir arayüzle gerçek veriye dayalı akışı çalıştır.
Kritik iş kurallarını test et; testlerde canlı veriyi kullanma. README ve durum
dosyasını güncelle. Hangi temel akışın çalıştığını kanıtlarıyla özetle.
Faz 3'e kendiliğinden geçme.
```

### Faz 3 promptu

```text
Kararsızım projesinde yalnızca Faz 3'ü uygula.

Mevcut işlevleri koruyarak belgedeki görsel dili uygula: açık zemin, beyaz kartlar,
mor ana eylemler, mercan/mint küçük vurgular, rahat okunurluk ve mobil yerleşim.
Form, boş durum, yüklenme, hata, sonuç ve kapalı anket ekranlarını tamamla.
Klavye kullanımını, kontrastı, uzun Türkçe içerikleri ve JavaScript kapalı temel
akışı kontrol et. Yeni frontend framework veya ağır tasarım paketi ekleme.

Kabul kriterlerini gözden geçir; yetkisiz işlemler, gizlilik, çift oy ve eşzamanlı
kapatma davranışlarını ilgili testlerle doğrula. PostgreSQL kontrollerini güvenli
test ortamında yap. Gerekirse sorguları sade biçimde iyileştir. Geliştirmeye özel
örnek veri komutu ekle; otomatik olarak gerçek ortama veri yükleme.

Yapılan kontrolleri, yapılamayanları ve bilinen sınırlamaları kaydet. README ve
docs/PROJE_DURUMU.md dosyasını güncelle. Faz 4'e kendiliğinden geçme.
```

### Faz 4 promptu

```text
Kararsızım projesinde yalnızca Faz 4'ü uygula: Vercel üzerinde denenebilir
bir prototip preview dağıtımı hazırla ve mevcut erişim izinleriyle gerçekleştir.

Önce doğru proje, hedef ortam ve prototip veritabanını belirle. Güncel resmi
Vercel Django dağıtım akışını doğrula; giriş noktası, statik dosyalar, ortam
değişkenleri, HTTPS/CSRF ayarları ve Supabase transaction pooler bağlantısını
kontrol et. Migration'ları kontrollü çalıştır; paralel build'lere bağlama.
Gerçek production verisini preview testlerinde kullanma.

Hesap erişimi veya gerekli ayar yoksa hazırlayabildiğin dosyaları tamamla ve
benim yapmam gereken adımları açıkça ver. Gizli bilgileri sohbete isteme.

Dağıtım erişilebilir olduğunda gerçek URL üzerinde kayıt, anket oluşturma,
misafir oy, sonuç, tekrar oy engeli ve statik dosyaları doğrula. URL'yi, dağıtım
durumunu, gerçekten yapılan kontrolleri ve kalan prototip sınırlamalarını raporla.
README ve docs/PROJE_DURUMU.md dosyasını güncelle. Geniş katılımlı production yayını
ve Faz 5 işlerini bu talebin kapsamına kendiliğinden ekleme.
```

### Yeni sohbette devam promptu

```text
Kararsızım geliştirmesine kaldığımız yerden devam edeceğiz. Eklerde ana proje
belgesi, mevcut kaynak kod ve docs/PROJE_DURUMU.md var. Önce bunları incele;
tamamlanmış işleri tekrarlama ve mevcut çalışan davranışları koru.

Bu oturumda hedefim: [faz numarası veya somut iş].
Son doğruladığım çalışan durum: [kısa açıklama].
Varsa hata mesajı: [gizli bilgileri temizlenmiş hata].

Önce mevcut durumu ve bu işin kapsamını kısaca belirt, ardından yetkili olduğun
işleri uygula. Dosya/terminal erişimin yoksa bunu söyle ve uygulanabilir dosya
değişiklikleri ile Windows PowerShell komutlarını ver.
```

## 20. Başarı tanımı

İlk prototipin başarısı şu akışla ölçülür:

> Bir kişi siteye gelir, kullanıcı adı/e-posta/parola ile üye olur, iki-beş
> seçenekli bir soru yayınlar. Başka bir kişi üye olmadan soruyu görür ve oy
> verir. Oy kalıcı kaydedilir, sonuç doğru görünür, aynı hesap/tarayıcı kimliği
> tekrar oy veremez ve hiçbir herkese açık ekranda e-posta adresi görünmez.

Bu akış mobilde rahat kullanılıyor ve Vercel prototip adresinde çalışıyorsa ilk hedef gerçekleşmiştir. Sonraki özellikler kullanıcı geri bildirimiyle seçilir.

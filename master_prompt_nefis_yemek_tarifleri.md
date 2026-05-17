# Master LLM Prompt: Nefis Yemek Tarifleri

> Bu belge frontier modellere (Claude Opus, Gemini Pro, GPT-5) doğrudan yapıştırılmak üzere otomatik sentezlenmiştir.

---

# Feature Request: SmartCook AI

## 1. Platform Tanımı
Platform: universal, cross-platform (MVP: mobil iOS & Android – React Native; ilerleyen fazda web dashboard – Next.js)

## 2. Ürün Vizyonu ve MVP Kapsamı
**ICP:** "Smart Cook" – 25-45 yaş arası, şehirli, yoğun çalışan veya ebeveyn; yemek yapmayı sever ancak zamana karşı yarışır; reklamdan nefret eder, sağlıklı/akıllı beslenmeye önem verir; mobil öncelikli kullanıcı.

**Çözüm Stratejisi:** Nefis Yemek Tarifleri’nin en büyük sürtünmelerinden (aşırı reklam, karmaşık UI, kişiselleştirme eksikliği) arınmış, yapay zeka ile güçlendirilmiş bir "akıllı aşçı asistanı" sunmak. Kullanıcı, evdeki malzemelerle ne pişireceğini doğal dilde sorar, AI anında en uygun tarifleri önerir. Porsiyonlar tek dokunuşla ayarlanır, tarifler çevrimdışı kaydedilebilir. MVP, reklamsız temiz bir deneyimle 5 temel özelliği 3 ayda pazara sunar.

**MVP Kapsamı (0-3 Ay):**
1. **AI Destekli Malzeme Bazlı Tarif Arama (RAG)** – kullanıcının girdiği malzemelerle eşleşen tarifleri doğal dilde önerir.
2. **Porsiyon Hesaplama** – basit lineer oranlama ile tarif malzemelerini istenen kişi sayısına uyarlar.
3. **Temiz, Reklamsız UI** – Material Design 3 uyumlu, üç tablı (Ana Sayfa, Defterim, Profil), hiçbir yerde reklam yok.
4. **Kullanıcı Kaydı ve Oturum** – e-posta + Google/Apple Sign-In, beslenme tercihleri profili.
5. **Çevrimdışı Tarif Görüntüleme** – kaydedilen tariflerin tam metni ve resmi cihazda saklanır, internet yokken erişilebilir.

---

## 3. Temel Veri Modelleri ve Backend İhtiyaçları (FastAPI & SQLModel)

### Veritabanı Tabloları (SQLModel)

| Tablo | Alanlar | Açıklama |
|-------|---------|----------|
| **User** | id (UUID, PK), email (unique), username, password_hash, dietary_preferences (JSON – örn: vejetaryen, vegan, alerjiler), created_at, updated_at | Kullanıcı hesabı |
| **Recipe** | id (UUID, PK), title, description, ingredients (JSON: [{name, amount, unit}]), steps (JSON: [step_text]), image_url, video_url, serving_count (int), prep_time (int, dk), cook_time (int, dk), difficulty (enum: kolay/orta/zor), tags (JSON: [string]), is_popular (bool), season (string: ilkbahar/yaz/sonbahar/kış), created_at | Tarif verisi |
| **SavedRecipe** | id (UUID, PK), user_id (FK -> User), recipe_id (FK -> Recipe), saved_at, notes (text) | Kullanıcının kaydettiği tarifler |
| **Ingredient** | id (UUID, PK), name (unique), unit (string – adet, gram, ml, su bardağı...), category (string – manav, kasap, süt ürünleri, baharat) | Referans malzeme listesi (opsiyonel, MVP’de recipe.ingredients içinde gömülü olabilir) |
| **AILog** | id (UUID, PK), user_id (FK -> User, nullable), query (text), ingredients_used (JSON), response (JSON), created_at, cost (float) | AI sorgu logları (maliyet takibi ve iyileştirme için) |

### Ana API Endpoint’leri (FastAPI)

| HTTP Metod | Endpoint | Açıklama | MVP |
|------------|----------|----------|-----|
| POST | `/auth/register` | E-posta + şifre ile kayıt | ✅ |
| POST | `/auth/login` | E-posta + şifre ile giriş, JWT döner | ✅ |
| POST | `/auth/social` | Google/Apple token ile giriş | ✅ |
| GET | `/recipes` | Sayfalı tarif listesi (filtre: popular, tag, season) | ✅ |
| GET | `/recipes/{id}` | Tek tarif detayı | ✅ |
| POST | `/recipes/search-by-ingredients` | **AI endpoint**: body {ingredients: [string], query?: string} -> en uygun 3 tarif + uyum yüzdesi | ✅ |
| POST | `/recipes/{id}/scale` | body {servings: int} -> malzemelerin lineer ölçeklenmiş hali | ✅ |
| GET | `/users/me/saved-recipes` | Kullanıcının kaydettiği tarifler | ✅ |
| POST | `/users/me/saved-recipes` | body {recipe_id} -> kaydet | ✅ |
| DELETE | `/users/me/saved-recipes/{id}` | Kaydı sil | ✅ |
| GET/PATCH | `/users/me/profile` | Kullanıcı profilini görüntüleme/güncelleme | ✅ |
| GET | `/health` | Sağlık kontrolü | ✅ |

*Not: MVP’de tarifler manuel olarak 100 adet yüklenir (JSON seed). İleride scraping veya kullanıcı katkısıyla genişletilir.*

---

## 4. Kullanıcı Arayüzü ve Frontend İhtiyaçları (React Native)

### Ekranlar / Sayfalar

| Ekran | Alt Bileşenler | Veri Kaynağı | Önemli Notlar |
|-------|----------------|--------------|---------------|
| **Onboarding** | Logo, "Malzemelerle Tarif Bul" tanıtımı, Kayıt/Giriş butonları | - | Sadece ilk açılışta |
| **Auth** | Login / Register formları, Google/Apple butonları | `/auth/*` | Social login öncelikli |
| **Home** | Üst: AI asistan input alanı ("Elimde ne var?"), Ort: Öne çıkan tarifler (yanyana kartlar), Alt: Kategori butonları | `GET /recipes?popular=true`, AI sorgu için ayrı buton | AI input odaklanınca klavye açılır, öneri listesi aşağıda belirir |
| **Recipe Detail** | Büyük resim, başlık, porsiyon seçici (2/4/6/manuel), değişen malzeme listesi, adım adım anlatım, video özeti butonu (MVP’de kullanıcıyı YouTube’a yönlendir), "Defterime Ekle" butonu | `GET /recipes/{id}`, `POST /recipes/{id}/scale` | Porsiyon değişince malzeme miktarları anlık yenilenir; beğenme animasyonu |
| **Defterim (My Recipes)** | Kaydedilmiş tarif kartları (resim, isim, hazırlık süresi), offline etiketi, silme butonu | `GET /users/me/saved-recipes`, local cache (AsyncStorage) | Çevrimdışıyken local veri gösterilir, senkronizasyon simgesi |
| **Profil** | Kullanıcı adı, e-posta, beslenme tercihleri (vejetaryen, vegan, alerji seçimi), premium durumu, çıkış yap | `GET/PATCH /users/me/profile` | Dietary preferences opsiyonel, sonraki AI planlama için kullanılacak |
| **Settings** | Dil seçimi (TR/EN), çevrimdışı depolama temizliği, bildirim tercihleri, sürüm | - | MVP’de minimum |

### UI/UX Beklentileri
- **Tema:** Material Design 3 (Light/Dark mode desteği)
- **Renk Paleti:** Sıcak ve iştah açıcı tonlar (turuncu, kırmızı, krem)
- **Geçişler:** Sayfa arası geçişler yumuşak (react-navigation)
- **Reklam:** Hiçbir yerde reklam gösterilmez; sadece premium badge ve upgrade banner (ayarlar sayfasında)
- **Stabilite:** Scroll donmaları %0 hedef; FlatList performans optimizasyonu
- **Yerelleştirme:** Tüm metinler Türkçe ve İngilizce (i18n)

---

## 5. Yapay Zeka Entegrasyon ve İş Mantığı

### RAG (Retrieval-Augmented Generation) – Malzeme Bazlı Arama

**Akış:**
1. Kullanıcı input alanına "tavuk, brokoli, yoğurt" yazar veya doğal dil cümlesi girer.
2. Frontend, `POST /recipes/search-by-ingredients` endpoint’ine `{ingredients: ["tavuk", "brokoli", "yoğurt"], query: "akşam yemeği için hızlı ne yapabilirim?"}` gönderir.
3. Backend:
   - Gelen malzemeleri embedding vektörüne çevirir (OpenAI ada-002 veya yerel sentence-transformers modeli).
   - Vektör veritabanında (pgvector veya Elasticsearch) benzerlik araması yaparak en uygun 5 tarifi bulur.
   - Bu tarifleri ve kullanıcı sorgusunu bir prompt ile LLM’e (GPT-4-mini veya Mistral 7B) gönderir.
   - Prompt tasarımı:
     ```
     Kullanıcı şu malzemelere sahip: {list}
     Şu anda şunu söylüyor: "{query}"
     Aşağıdaki tariflerden en uygun 3 tanesini seç.
     Her tarif için:
     - Başlık
     - Uyum yüzdesi (malzemelere göre)
     - Kısa bir açıklama (neden uygun olduğu)
     - Eksik malzemeler varsa belirt.
     Tarifler: {recipe_list}
     ```
   - LLM yanıtını JSON olarak yapılandırır: `{results: [{id, title, match_percentage, explanation, missing_ingredients}]}`
4. Yanıt frontend’e döner, kullanıcıya kart şeklinde gösterilir.

**Performans & Maliyet Yönetimi:**
- Sık sorulan sorgular (örn: "kıyma ile ne yapılır") Redis cache’te tutulur.
- Ücretsiz kullanıcı: günde 3 AI sorgu; premium: sınırsız.
- LLM yanıtı stream edilir (Server-Sent Events) – kullanıcı beklerken "düşünüyor" animasyonu.

### Porsiyon Hesaplama (Kural Tabanlı + Ölçekleme)

- `POST /recipes/{id}/scale` endpoint'i, tarifin orijinal `serving_count` değerini alır.
- Kullanıcının istediği `servings` ile oran hesaplar: `scale_factor = new_servings / original_servings`.
- Her malzeme için: `new_amount = old_amount * scale_factor` (lineer).
- Katı/sıvı ayrımı MVP’de yok; ileride ML ile optimize edilecek.
- Yanıt: `{scaled_ingredients: [{name, amount, unit}]}`

### Gelecek AI Özellikleri (Mimaride hazırlık)
- **Agentic Yemek Planlama:** Function calling ile haftalık takvim + market listesi oluşturma (GPT-4 + araç kullanımı).
- **Video Özeti:** Whisper + ffmpeg ile video işleme, adım metinleri çıkarma.
- **Malzeme Tanıma:** Görüntü işleme modeli (YOLO) – MVP’de yok.

---

## 6. Güvenlik ve DevOps Kısıtları (OWASP Standartları)

### Yetkilendirme ve Roller
- **Rol tabanlı erişim:** Sadece `user` rolü MVP’de. Gelecekte `admin` eklenir.
- **JWT token:** Access token (15 dk) + Refresh token (7 gün). Token’lar HTTP-only cookie veya secure storage’da saklanır.
- **API koruması:** Tüm `/users/*` ve `/recipes/search-by-ingredients` endpoint’leri `Authorization: Bearer <token>` gerektirir.
- **Rate Limiting:** AI sorgu endpoint’i için IP başına dakikada 10 istek; kullanıcı başına günde 3 (ücretsiz) / sınırsız (premium). Diğer endpoint’lerde 100 istek/dk.

### Veri Güvenliği
- **Parola hash:** bcrypt (salt ile).
- **Hassas veri:** Kullanıcı e-postası ve beslenme tercihleri TLS üzerinden iletilir; veritabanında şifresiz saklanır (şifreleme gerekmiyor, ancak hash’lenmiş parola yeterli).
- **Input validasyonu:** FastAPI ile Pydantic modelleri kullanılarak tüm girişler doğrulanır (SQL injection önlenir – ORM kullanımı).
- **AI logları:** Kullanıcı ID’si anonimleştirilebilir; kişisel veri loglanmaz.
- **HTTPS zorunlu:** Tüm API istekleri HTTPS üzerinden.

### DevOps Kısıtları
- **CI/CD:** GitHub Actions ile test, lint, build, deploy.
- **Ortamlar:** Development, Staging, Production ayrı.
- **Containerization:** Backend Docker + Docker Compose, PostgreSQL + pgvector.
- **Monitör:** API yanıt süreleri, AI maliyetleri (CloudWatch veya Grafana).
- **Secrets yönetimi:** Ortam değişkenleri (API keys, DB URL) – Vault veya GitHub Secrets.

### OWASP Top 10’a Uyum
- **A01 – Broken Access Control:** Rol bazlı yetkilendirme, token doğrulama.
- **A02 – Cryptographic Failures:** TLS 1.3, bcrypt.
- **A03 – Injection:** ORM kullanımı, parametrik sorgular.
- **A04 – Insecure Design:** Rate limiting, AI sorgu loglama.
- **A05 – Security Misconfiguration:** Varsayılan portlar değil, CORS sadece bilinen domainler.
- **A06 – Vulnerable Components:** Düzenli bağımlılık güncellemesi (Dependabot).
- **A07 – Identification and Auth Failures:** JWT süre yönetimi, social login güvenliği.
- **A08 – Data Integrity:** AI yanıtları için doğrulama (hallucination raporlama butonu).
- **A09 – Security Logging:** Tüm auth ve AI istekleri loglanır.
- **A10 – SSRF:** Backend dışında sadece tanımlı API’lere (OpenAI) erişim.

---

*Bu doküman, üç AI ajanının (Project Architect, Backend Dev, Frontend Dev) bağımsız olarak okuyup kodlamaya başlayabilmesi için yeterli bilgiyi içermektedir. MVP süresi 3 ay olup, Sprint 1-2’de Auth + Temel UI, Sprint 3-4’te RAG + Porsiyon + Çevrimdışı, Sprint 5-6’da test ve mağaza yayını öngörülmüştür.*
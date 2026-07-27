# Görev Takip ve İşbirliği Uygulaması (Task Collaboration App - GoJira)

Bu proje; **Django REST Framework** tabanlı backend, **Vue 3 + Vuetify** tabanlı frontend, **PostgreSQL** veritabanı ve **Docker + Nginx** multi-container ortamını içeren kurumsal bir görev takip, güvenlik ve işbirliği uygulamasıdır.

---

## 🚀 Hızlı Başlangıç (Docker ile Tek Komutla Çalıştırma)

Projenin tüm servisleri (PostgreSQL DB, Django REST API, Nginx Reverse Proxy & Vue Frontend) Docker container'larında yapılandırılmıştır.

Tek yapmanız gereken proje ana dizininde şu komutu çalıştırmaktır:

```bash
docker compose up --build
```

Servisler başladıktan sonra:
- **Uygulama Arayüzü (Frontend):** [http://localhost](http://localhost)
- **Django REST API:** [http://localhost/api/](http://localhost/api/)
- **Django Admin Paneli:** [http://localhost/admin/](http://localhost/admin/)

> **Not:** Container'lar ayağa kalktığında varsayılan kullanıcılar ve veriler otomatik yüklenir.

---

### 🔑 Varsayılan Giriş Bilgileri

| Kullanıcı Rolü | Kullanıcı Adı | Şifre | Yetkiler |
| :--- | :--- | :--- | :--- |
| **Sistem Yöneticisi (Admin)** | `admin` | `AdminPassword123!` | Tüm menülere erişim, Kullanıcı Yönetimi (Users CRUD), Sistem Logları (`/logs`), herkese görev atama. |
| **Geliştirici (User 1)** | `user1` | `User1Password123!` | Görev Panosu, Profil paneli, kendine görev oluşturma, yorum ekleme. |
| **Tasarımcı (User 2)** | `user2` | `User2Password123!` | Görev Panosu, Profil paneli, kendine görev oluşturma, yorum ekleme. |

---

## 💻 Manuel (Yerel) Geliştirme Kurulumu

### 1. Backend (Django REST Framework + PostgreSQL / SQLite)

```bash
cd backend

# Sanal ortamı oluşturun ve aktif edin
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Veritabanı migrasyonlarını uygulayın
python manage.py migrate

# Backend sunucusunu başlatın
python manage.py runserver
```

### 2. Frontend (Vue 3 + Vuetify)

```bash
cd frontend

# Bağımlılıkları yükleyin
npm install

# Geliştirme sunucusunu başlatın
npm run dev
```

---

## 🏗️ Mimari ve Teknolojik Unsurlar

### Multi-Container Docker Mimarisi
```text
               +----------------------------------+
               |        Nginx Container (Port 80) |
               | (Frontend SPA & Reverse Proxy)   |
               +----------------+-----------------+
                                |
             +------------------+------------------+
             |                                     |
    /api/ ve /admin/ istekleri            Vue Static Files
             |                                     |
             v                                     v
+---------------------------+            +-------------------+
|  Django Backend (Port 8000)|            | Single Page App   |
+------------+--------------+            +-------------------+
             |
             v
+---------------------------+
| PostgreSQL DB (Port 5432) |
+---------------------------+
```

---

## 📋 Proje Özellikleri ve Karşılanan Gereksinimler

### 🔄 Sprint & Backlog Yönetimi (Agile / Scrum Modülü)
- ✅ **Sprint Modeli (`Sprint`)**: İsmi, Hedefi, Başlangıç/Bitiş Tarihleri ve Durumu (`future`, `active`, `completed`) ile tam çevik süreç takibi.
- ✅ **Story Points (Efor Puanlama)**: Görevlerin eforunu gösteren puanlama rozetleri (`1`, `2`, `3`, `5`, `8`, `13 pts`).
- ✅ **Jira Tarzı Backlog & Sprint Planlama Arayüzü (`/backlog`)**:
  - Üstte Aktif Sprint kartı, efor özeti ve *"Sprinti Tamamla"* / *"Sprinti Başlat"* butonları.
  - Altta Backlog Havuzu (Planlanacak Görevler) ve tek tıkla *"Sprint'e Ekle"* / *"Backlog'a Al"* aktarımı.
- ✅ **Zengin Örnek Veri Seti**: Sunum ve gösterim için 8 farklı kullanıcı (PM, QA, Developer, Designer) ve 11 adet eforlanmış örnek görev/story verisi.

### 🛡️ Part 2 & Güvenlik Özellikleri
- ✅ **Parola Karmaşıklık Kontrolü**: En az 8 karakter, rakam, sembol (`!@#$%^&*` vb.), büyük ve küçük harf içerme zorunluluğu (`validators.py`).
- ✅ **2 Aşamalı OTP ile Giriş**: Kullanıcı adı/parola doğrulamasının ardından 6 haneli OTP kodu üretilerek e-posta atılır ve terminale yazdırılır. 5 dakika geçerlik süreli OTP doğrulanmadan Token verilmez.
- ✅ **Standart Hata Mesajı**: User Enumeration saldırılarını engellemek için tüm kullanıcı adı/parola/OTP hatalarında standart olarak `"girdiğiniz bilgiler hatalı"` mesajı dönülür.
- ✅ **Şifremi Unuttum ve Sıfırlama Akışı**: E-posta adresi ile şifre sıfırlama linki (`/reset-password?uid=...&token=...`) gönderilir ve yeni şifre parola politikasına göre güncellenir.
- ✅ **FE ve BE Uçtan Uca Veri Şifreleme (`ENCRYPTION_KEY`)**: 
  - Backend üzerindeki hassas uç noktalar (`/api/profile/`, `/api/tasks/summary/`, `/api/logs/`) AES-256-CBC ile şifreli paket (`encrypted_data`, `iv`) döndürür.
  - Ağ (Network) sekmesinde veriler şifreli görünür. Frontend Axios interceptor'ı (`api.js`) Web Crypto API kullanarak verileri otomatik çözer.
- ✅ **Admin-Only "Sistem Logları" Ekranı (`/logs`)**:
  - `RequestLogMiddleware` ile atılan *bütün* HTTP isteklerinin IP adresi, kullanıcı, User-Agent, metod, endpoint ve durum kodu kaydedilir.
  - Sadece Admin (`is_staff`) yetkisine sahip kullanıcıların erişebildiği aranabilir ve filtrelenebilir **Sistem Logları** ekranı sunulur.

### 📋 Part 1 & Temel Özellikler
- ✅ **Kullanıcı Modeli (`User`)**: `AbstractUser` tabanlı, kullanıcı adı, şifre, e-posta, ad, soyad, doğum günü, departman, `otp_code` ve `otp_created_at` alanları.
- ✅ **Görev Modeli (`Task`)**: Durumlar (`TO DO`, `IN PROGRESS`, `DONE` vb.), öncelik, tip, süre, teslim tarihi ve self-referencing `parent` alanı ile **Subtask (Alt Görev)** desteği.
- ✅ **Yorum ve Alt Görev Yönetimi**: Görevlere yorum ekleme, yorum sahibi veya admin düzenleme/silme yetkileri.
- ✅ **Interaktif Üst Bar ve Menüler**: Çalışma Alanları, Projeler, Filtreler, Panolar, Arama ve Yardım dokümantasyon modalları.

---

## 🧪 Birim Testlerin (Unit Tests) Çalıştırılması

Tüm backend güvenlik, OTP, şifreleme, permission ve loglama testlerini çalıştırmak için:

```bash
cd backend
python manage.py test tasks
```

---

## 📌 Commit Geçmişi

Projedeki tüm Part 2 geliştirmeleri modüler commit'ler ile saklanmıştır:
- `83195b2` - `feat: parola karmaşıklık politikası ve kontrol mekanizması eklendi`
- `70dd37d` - `feat: 2 aşamalı OTP ile giriş özelliği ve standart hata mesajları eklendi`
- `6d4196a` - `feat: e-posta ile şifremi unuttum ve şifre sıfırlama akışı eklendi`
- `0c77ec6` - `feat: FE ve BE hassas veri iletimi için AES şifreleme altyapısı eklendi`
- `1c66c4a` - `feat: admin istek loglama middleware ve Logs ekranı eklendi`
- `08a91bc` - `refactor: genel kod temizlikleri, home view iyileştirmeleri ve kapsamlı birim testler eklendi`
- `521b636` & `31dc53d` - `fix: üst bar butonlarının açılır menüleri ve tıklama yönlendirmeleri düzeltildi`

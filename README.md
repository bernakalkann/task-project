# Görev Takip ve İşbirliği Uygulaması (Task Collaboration App)

Bu proje; **Django REST Framework** tabanlı backend, **Vue 3 + Vuetify** tabanlı frontend, **PostgreSQL** veritabanı ve **Docker + Nginx** multi-container ortamını içeren kurumsal bir görev takip ve işbirliği uygulamasıdır.

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

> **Not:** Container'lar ayağa kalktığında `database_init` betiği otomatik olarak çalışır ve varsayılan kullanıcıları ve verileri yükler.

### 🔑 Varsayılan Giriş Bilgileri

| Kullanıcı Rolü | Kullanıcı Adı | Şifre | Yetkiler |
| :--- | :--- | :--- | :--- |
| **Sistem Yöneticisi (Admin)** | `admin` | `adminpassword` | Tüm menülere erişim, Kullanıcı Yönetimi (Users CRUD), herkese görev atama. |
| **Geliştirici (User 1)** | `user1` | `user1password` | Sadece Görevler ve Profil paneli, kendine görev oluşturma, yorum ekleme. |
| **Tasarımcı (User 2)** | `user2` | `user2password` | Sadece Görevler ve Profil paneli, kendine görev oluşturma, yorum ekleme. |

---

## 💻 Manuel (Yerel) Geliştirme Kurulumu

### 1. Backend (Django REST Framework + PostgreSQL)

```bash
cd backend

# Sanal ortamı oluşturun ve aktif edin
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Veritabanını oluşturun ve varsayılan verileri yükleyin
python manage.py database_init

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

## 📋 Proje Gereksinimleri ve Karşılanan Özellikler

### Part 1 & Genel Gereksinimler
- ✅ **Kullanıcı Modeli (`User`)**: `AbstractUser` tabanlı, kullanıcı adı, şifre, e-posta, ad, soyad, doğum günü ve departman alanları.
- ✅ **Görev Modeli (`Task`)**: Durumlar (`TODO`, `IN PROGRESS`, `DONE` vb.), öncelik, tip, süre, teslim tarihi ve self-referencing `parent` alanı ile **Subtask (Alt Görev)** desteği.
- ✅ **Giriş (Login) Ekranı**: Username + Password ile giriş ve Token tabanlı kimlik doğrulama.
- ✅ **Yetkilendirme ve Güvenlik**:
  - Admin kullanıcılar sol menüde **Users** ekranını görür ve kullanıcılar üzerinde tam CRUD (Ekleme, Arama, Silme onayı) yapabilir.
  - Normal kullanıcılar **Users** ekranını göremez, API seviyesinde 403 engeli uygulanır.
  - Normal kullanıcılar sadece kendilerine `Task` oluşturabilir (Admin herkes adına oluşturabilir).
- ✅ **Yorum ve Alt Görev Yönetimi**: Görevlere herkes yorum ekleyebilir. Yorum sahibi veya admin yorumları düzenleyebilir/silebilir. Alt görevler dinamik yönetilebilir.
- ✅ **Dashboard (Home)**: Normal kullanıcılar kendilerine atanan görev durumlarını panellerde görür, admin ise sistem geneli istatistikleri inceler.
- ✅ **DRF Serializers**: Tüm veriler backend ve frontend arasında serializers üzerinden geçer.
- ✅ **REST API Search/Filter**: Arama ve filtreleme PostgreSQL sorguları üzerinden yürütülür.

---

## 🧪 Testlerin Çalıştırılması

Backend birim testlerini koşturmak için:

```bash
cd backend
python manage.py test
```

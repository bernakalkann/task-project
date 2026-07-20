# Görev Takip ve İşbirliği Uygulaması (Task Collaboration App)

Bu proje, Django REST Framework tabanlı bir backend ile modern Vuetify (Vue 3) bileşenlerini kullanan bir frontend içeren çok kullanıcılı bir görev takip ve işbirliği uygulamasıdır.

## Proje Yapısı

* **backend/**: Python + Django REST Framework + PostgreSQL.
* **frontend/**: Vue 3 + Vite + Vuetify + Axios + Pinia.

---

## Kurulum ve Çalıştırma Talimatları

### 1. Backend Kurulumu

Backend dizinine geçip sanal ortamı aktif hale getirin ve bağımlılıkları yükleyin:

```bash
cd backend
# Sanal ortamı aktif edin (macOS/Linux)
source venv/bin/activate
# Veya Windows'ta: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

#### Veritabanı ve Migration İşlemleri
Proje varsayılan olarak `core/settings.py` dosyasında PostgreSQL veritabanı ayarlarını kullanmaktadır. PostgreSQL veritabanı sunucunuzun çalışır durumda olduğundan emin olun.

Veritabanı tablolarını oluşturmak ve örnek verileri (admin ve test kullanıcıları) yüklemek için aşağıdaki özel komutu çalıştırmanız yeterlidir:

```bash
python manage.py database_init
```

Bu komut:
1. Tüm Django migrasyonlarını otomatik çalıştırır.
2. Default olarak aşağıdaki kullanıcıları oluşturur:
   * **Admin Kullanıcısı:** `admin` (Şifre: `adminpassword`)
   * **Kullanıcı 1:** `user1` (Şifre: `user1password`)
   * **Kullanıcı 2:** `user2` (Şifre: `user2password`)
3. Örnek görevleri ve yorumları sisteme ekler.

#### Backend Sunucusunu Başlatma
Sunucuyu lokal ortamda çalıştırmak için:

```bash
python manage.py runserver
```

Backend sunucusu varsayılan olarak `http://127.0.0.1:8000` adresinde çalışacaktır.

---

### 2. Frontend Kurulumu

Frontend dizinine geçip npm bağımlılıklarını kurun ve geliştirici sunucusunu başlatın:

```bash
cd frontend
npm install
npm run dev
```

Frontend uygulaması varsayılan olarak `http://localhost:3000` veya terminalde belirtilen adreste çalışacaktır.

---

## Proje Özellikleri ve Yetkiler

### Kullanıcı Tipleri
1. **Admin (Staff):**
   * Sol tarafta yer alan **Kullanıcılar (Users)** menüsünü görebilir.
   * Tüm kullanıcılara yeni görev atayabilir ve kullanıcı ekleme/güncelleme/silme işlemlerini yapabilir.
   * Panodaki tüm görevleri görüntüleyebilir ve durumlarını değiştirebilir.
   * Tüm yorumları düzenleyebilir ve silebilir.
   * Anasayfa panellerinde sistemdeki tüm görevlerin toplam sayılarını görür.

2. **Normal Kullanıcı:**
   * **Kullanıcılar (Users)** menüsünü göremez ve bu API'lere erişemez (403 engeli).
   * Yalnızca kendine atanan görevleri görüntüleyebilir.
   * Sadece kendine ait görev yaratabilir (atanan kişi zorunlu olarak kendisi seçilir).
   * Herhangi bir göreve yorum ekleyebilir. Yalnızca kendi yazdığı yorumları düzenleyebilir veya silebilir.
   * Anasayfa panellerinde sadece kendine atanmış olan aktif görevlerin istatistiklerini görür.

### Kanban Durumları (States)
* `TODO` (Yapılacaklar)
* `IN PROGRESS` (İşlemde)
* `DONE` (Tamamlandı)

---

## Testlerin Çalıştırılması

Backend API testlerini çalıştırmak için `backend/` dizini altındayken:

```bash
python manage.py test
```

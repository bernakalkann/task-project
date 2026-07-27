# 🚀 GoJira - Kurumsal Görev Takip ve İşbirliği Platformu

**GoJira**, Jira stili Agile/Scrum süreç yönetimi, canlı WebSocket senkronizasyonu (Redis + Channels) ve Telegram 2FA güvenlik altyapısına sahip kurumsal bir görev takip platformudur.

---

## ⚡ Hızlı Başlangıç (Docker ile Tek Komut)

Projenin tüm servisleri (**PostgreSQL 15**, **Redis 7**, **Django Daphne ASGI Backend**, **Nginx Vue 3 Frontend**) Docker ortamında hazırlanmıştır.

```bash
docker compose up -d --build
```

- 🌐 **Uygulama (Frontend):** [http://localhost](http://localhost)
- ⚙️ **REST API:** [http://localhost/api/](http://localhost/api/)
- 🛡️ **Admin Paneli:** [http://localhost/admin/](http://localhost/admin/)

---

## 🔑 Varsayılan Giriş Bilgileri

| Rol | Kullanıcı Adı | Şifre | Açıklama |
| :--- | :--- | :--- | :--- |
| **Sistem Yöneticisi (Admin)** | `beyza` | `Beyza1234!` | Tam Yetkili Admin & Kullanıcı Yönetimi |
| **Admin Yöneticisi** | `admin` | `AdminPassword123!` | Sistem Yönetimi ve Log Ekranı (`/logs`) |
| **Yazılım Geliştirici** | `ahmet.dev` | `User1Password123!` | Görev Panosu, Yorumlar, Subtask'ler |

---

## 🛠️ Öne Çıkan Özellikler ve Mimari

### 🟢 1. Canlı WebSocket ve Redis Katmanı (Real-Time Sync)
- **Django Channels & Daphne (ASGI)**: Polling yapmadan milisaniyelik canlı sayfa güncellemeleri.
- **Redis 7 Katmanı**: Çoklu sunucu/container ortamlarında kesintisiz canlı yayın veritabanı.

### 🔐 2. Telegram Bot 2FA Güvenlik Altyapısı
- **Çoklu Kullanıcı (Multi-User) Telegram 2FA**: Giriş ve şifre sıfırlama işlemlerinde 6 haneli OTP kodu doğrudan kullanıcının kişisel Telegram hesabına (`@gojira_task_auth_bot`) iletilir.
- **Zırhlanmış Güvenlik**: PBKDF2 hash'li OTP saklama, race-condition koruması (`select_for_update`) ve AES-256 Fernet veri şifreleme.

### 📋 3. Agile/Scrum & Görev Yönetimi
- **Kanban Pano & Sprint Planlama (`/backlog`)**: Aktif sprint, efor puanlama (Story Points), görev sürükle-bırak.
- **Jira Tempo Worklog (`Timeline`)**: Kullanıcı bazlı günlük/haftalık çalışma saatleri matris raporu.
- **Jira Easy Calendar & ICS Feed Export (`Calendar`)**: 31 günlük takvim matrisi ve Google/Outlook/Apple Calendar (.ics) aktarımı.
- **Yönetici Raporları (`Reports`)**: KPI kartları, 8 durumlu ilerleme çubukları ve analitik grafikler.

---

## 🏗️ Docker Container Mimarisi

```text
               +-----------------------------------+
               |     Nginx Container (Port 80)     |
               | (Frontend SPA & Reverse Proxy)    |
               +-----------------+-----------------+
                                 |
              +------------------+------------------+
              |                                     |
    /api/, /ws/ ve /admin/                  Vue Static Files
              |                                     |
              v                                     v
+---------------------------+             +-------------------+
|  Django Daphne ASGI       |             | Single Page App   |
|  Backend (Port 8000)      |             +-------------------+
+------+---------------+----+
       |               |
       v               v
+--------------+ +--------------+
| PostgreSQL   | | Redis 7      |
| DB (Port 5433)| | (Port 6379)  |
+--------------+ +--------------+
```

---

## 🧪 Birim Testler (Unit Tests)

Backend güvenlik ve API birim testlerini çalıştırmak için:

```bash
cd backend
python manage.py test tasks
```

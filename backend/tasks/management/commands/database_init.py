import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from tasks.models import Task, Comment, Sprint

User = get_user_model()

class Command(BaseCommand):
    help = 'Runs migrations and seeds database with 26+ tasks distributed evenly across all 8 Kanban states.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Running database migrations..."))
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS("Migrations completed successfully."))

        self.stdout.write(self.style.WARNING("Seeding database users..."))

        users_data = [
            ('admin', 'admin@example.com', 'AdminPassword123!', True, 'Yönetim'),
            ('beyza', 'beyza@example.com', 'BeyzaPassword123!', True, 'Yönetim'),
            ('user1', 'user1@example.com', 'User1Password123!', False, 'Backend Development'),
            ('user2', 'user2@example.com', 'User2Password123!', False, 'Frontend Development'),
            ('ahmet.dev', 'ahmet@example.com', 'AhmetPassword123!', False, 'Fullstack Development'),
            ('canan.qa', 'canan@example.com', 'CananPassword123!', False, 'QA & Testing'),
            ('mehmet.pm', 'mehmet@example.com', 'MehmetPassword123!', False, 'Product Management'),
            ('zeynep.ui', 'zeynep@example.com', 'ZeynepPassword123!', False, 'UI/UX Design')
        ]

        created_users = {}
        for username, email, pwd, is_staff, dept in users_data:
            u, created = User.objects.get_or_create(username=username, defaults={
                'email': email,
                'is_staff': is_staff,
                'is_superuser': is_staff,
                'department': dept
            })
            if created or not u.check_password(pwd):
                u.set_password(pwd)
                u.save()
            created_users[username] = u

        admin_user = created_users['admin']
        beyza_user = created_users['beyza']
        user1 = created_users['user1']
        user2 = created_users['user2']
        ahmet = created_users['ahmet.dev']
        canan = created_users['canan.qa']
        mehmet = created_users['mehmet.pm']
        zeynep = created_users['zeynep.ui']

        self.stdout.write(self.style.WARNING("Seeding sprints..."))

        sprint_active, _ = Sprint.objects.get_or_create(
            name="Sprint 14 - Güvenlik & Sprint Yönetimi",
            defaults={
                'goal': "OTP 2-step kimlik doğrulama, AES veri şifreleme ve Sprint & Backlog ekranlarının canlıya alınması.",
                'start_date': date.today() - timedelta(days=3),
                'end_date': date.today() + timedelta(days=11),
                'status': 'active'
            }
        )

        sprint_future, _ = Sprint.objects.get_or_create(
            name="Sprint 15 - Real-time Collaboration & WebSockets",
            defaults={
                'goal': "Django Channels ile canlı pano senkronizasyonu ve @mention bildirimlerinin eklenmesi.",
                'start_date': date.today() + timedelta(days=12),
                'end_date': date.today() + timedelta(days=26),
                'status': 'future'
            }
        )

        self.stdout.write(self.style.WARNING("Seeding comprehensive tasks across all 8 states..."))

        tasks_list = [
            # --- 1. TO DO (4 Görev) ---
            {
                'title': "GitHub Webhook & Auto PR Status Integration",
                'definition': "Commit atıldığında veya PR birleştirildiğinde ilgili kartın otomatik DONE yapılması.",
                'creator': mehmet, 'assignee': ahmet, 'sprint': sprint_future, 'state': 'to do',
                'priority': 'high', 'task_type': 'story', 'duration': 14, 'story_points': 8, 'due_date': '2026-08-10', 'epic': 'DevOps Entegrasyon'
            },
            {
                'title': "Slack Kanalı Anlık Bildirim Botu Entegrasyonu",
                'definition': "Kritik seviyede bir Hata (Bug) açıldığında Slack kanalına otomatik webhook mesajı atılması.",
                'creator': mehmet, 'assignee': user1, 'sprint': sprint_future, 'state': 'to do',
                'priority': 'medium', 'task_type': 'task', 'duration': 8, 'story_points': 3, 'due_date': '2026-08-12', 'epic': 'DevOps Entegrasyon'
            },
            {
                'title': "Fatura & Abonelik Modülü Arayüz Tasarımı",
                'definition': "Kurumsal müşteriler için paket seçimi ve kredi kartı ödeme adımlarının çizimi.",
                'creator': zeynep, 'assignee': zeynep, 'sprint': None, 'state': 'to do',
                'priority': 'low', 'task_type': 'story', 'duration': 12, 'story_points': 2, 'due_date': '2026-08-20', 'epic': 'Ödeme & Fatura'
            },
            {
                'title': "Otomatik Veritabanı Yedeği ve S3 Entegrasyonu",
                'definition': "Gece 03:00'te PostgreSQL dump alınarak AWS S3 bucket'a şifreli yedeklenmesi.",
                'creator': admin_user, 'assignee': user1, 'sprint': None, 'state': 'to do',
                'priority': 'high', 'task_type': 'task', 'duration': 10, 'story_points': 5, 'due_date': '2026-08-25', 'epic': 'Sistem Altyapısı'
            },

            # --- 2. IN PROGRESS (3 Görev) ---
            {
                'title': "AES-256 Payload Encryption Interceptor",
                'definition': "Backend ve Frontend arasında hassas verilerin şifreli iletilmesi için Axios interceptor yazılması.",
                'creator': mehmet, 'assignee': user2, 'sprint': sprint_active, 'state': 'in progress',
                'priority': 'high', 'task_type': 'story', 'duration': 16, 'story_points': 5, 'due_date': '2026-07-29', 'epic': 'Güvenlik & OTP'
            },
            {
                'title': "Backlog & Sprint Planlama Ekran Tasarımı",
                'definition': "Jira tarzı drag-and-drop Sprint ve Backlog planlama arayüzünün Vuetify ile kodlanması.",
                'creator': zeynep, 'assignee': user2, 'sprint': sprint_active, 'state': 'in progress',
                'priority': 'medium', 'task_type': 'story', 'duration': 20, 'story_points': 5, 'due_date': '2026-07-30', 'epic': 'Kanban & Sprint'
            },
            {
                'title': "Kullanıcı Profili Karanlık Tema (Dark Mode) Desteği",
                'definition': "Vuetify 3 temasının koyu mod seçeneği ile kullanıcı tercihlerine göre saklanması.",
                'creator': beyza_user, 'assignee': zeynep, 'sprint': sprint_active, 'state': 'in progress',
                'priority': 'low', 'task_type': 'task', 'duration': 6, 'story_points': 2, 'due_date': '2026-08-02', 'epic': 'UI/UX'
            },

            # --- 3. IN CODE REVIEW (3 Görev) ---
            {
                'title': "OTP 2-Step Authentication & Throttling",
                'definition': "Giriş ekranında 6 haneli OTP kodu üretimi, secrets modülü entegrasyonu ve rate limiting eklenmesi.",
                'creator': admin_user, 'assignee': ahmet, 'sprint': sprint_active, 'state': 'in code review',
                'priority': 'critical', 'task_type': 'task', 'duration': 8, 'story_points': 8, 'due_date': '2026-07-28', 'epic': 'Güvenlik & OTP'
            },
            {
                'title': "Parola Karmaşıklık Kontrolü & Birim Testleri",
                'definition': "RegEx parola politikası kurallarının ve APITestCase validator testlerinin yazılması.",
                'creator': beyza_user, 'assignee': user1, 'sprint': sprint_active, 'state': 'in code review',
                'priority': 'high', 'task_type': 'task', 'duration': 6, 'story_points': 3, 'due_date': '2026-07-29', 'epic': 'Güvenlik & OTP'
            },
            {
                'title': "CSV Dışa Aktarım Türkçe Karakter (UTF-8 BOM) Desteği",
                'definition': "Excel'de açılan görev listesi CSV dosyasının Türkçe karakter uyumunun sağlanması.",
                'creator': mehmet, 'assignee': ahmet, 'sprint': sprint_active, 'state': 'in code review',
                'priority': 'medium', 'task_type': 'task', 'duration': 4, 'story_points': 2, 'due_date': '2026-07-30', 'epic': 'Raporlama'
            },

            # --- 4. BLOCKED (DEV) (3 Görev) ---
            {
                'title': "Mobil Bildirim Servisinde Gecikme Hatası",
                'definition': "Android ve iOS bildirim servisinde Firebase mesaj iletim sürelerinin incelenmesi.",
                'creator': canan, 'assignee': ahmet, 'sprint': sprint_active, 'state': 'blocked dev',
                'priority': 'critical', 'task_type': 'bug', 'duration': 18, 'story_points': 5, 'due_date': '2026-08-05', 'epic': 'Kalite & Test'
            },
            {
                'title': "Redis Bağlantı Havuzu Bellek Sızıntısı Hatası",
                'definition': "Staging ortamında Celery worker'larının Redis hafızasını doldurup kilitlenmesi engellendi.",
                'creator': user1, 'assignee': user1, 'sprint': sprint_active, 'state': 'blocked dev',
                'priority': 'high', 'task_type': 'bug', 'duration': 14, 'story_points': 8, 'due_date': '2026-08-03', 'epic': 'Sistem Altyapısı'
            },
            {
                'title': "Lokal Docker Nginx Port Çakışma Hatası",
                'definition': "MacOS Sequoia güncellemesi sonrası 8000 portunun sistem tarafından tutulması.",
                'creator': user1, 'assignee': ahmet, 'sprint': sprint_active, 'state': 'blocked dev',
                'priority': 'medium', 'task_type': 'bug', 'duration': 8, 'story_points': 3, 'due_date': '2026-08-01', 'epic': 'Sistem Altyapısı'
            },

            # --- 5. READY FOR TEST (3 Görev) ---
            {
                'title': "Profil Güncelleme & Avatar Resim Yükleme",
                'definition': "Kullanıcı profil fotoğraflarının Base64 olarak kaydedilmesi ve kırpılması arayüzü.",
                'creator': zeynep, 'assignee': user2, 'sprint': sprint_active, 'state': 'ready for test',
                'priority': 'high', 'task_type': 'story', 'duration': 10, 'story_points': 3, 'due_date': '2026-07-30', 'epic': 'Kullanıcı Yönetimi'
            },
            {
                'title': "Admin Log İzleme Ekranı Arama Filtreleri",
                'definition': "IP adresi, HTTP metodu ve status code bazlı anlık arama motorunun test edilmesi.",
                'creator': beyza_user, 'assignee': canan, 'sprint': sprint_active, 'state': 'ready for test',
                'priority': 'medium', 'task_type': 'task', 'duration': 8, 'story_points': 5, 'due_date': '2026-07-31', 'epic': 'Loglama'
            },
            {
                'title': "Tek Kullanımlık Şifre Sıfırlama Token İptali",
                'definition': "Şifre değiştirildikten sonra eski OTP kodunun tekrar kullanılamadığının doğrulanması.",
                'creator': admin_user, 'assignee': canan, 'sprint': sprint_active, 'state': 'ready for test',
                'priority': 'high', 'task_type': 'task', 'duration': 6, 'story_points': 3, 'due_date': '2026-07-30', 'epic': 'Güvenlik & OTP'
            },

            # --- 6. IN TEST (3 Görev) ---
            {
                'title': "QA Otomasyon Testlerinin Koşulması",
                'definition': "Giriş, OTP, Şifre Sıfırlama ve Yetki kontrolleri için Selenium/Playwright E2E testleri.",
                'creator': admin_user, 'assignee': canan, 'sprint': sprint_active, 'state': 'in test',
                'priority': 'high', 'task_type': 'task', 'duration': 10, 'story_points': 3, 'due_date': '2026-07-31', 'epic': 'Kalite & Test'
            },
            {
                'title': "Cypress E2E Giriş & OTP Senaryo Testi",
                'definition': "Başarısız ve başarılı 2 aşamalı giriş adımlarının otomatize test koşumu.",
                'creator': canan, 'assignee': canan, 'sprint': sprint_active, 'state': 'in test',
                'priority': 'medium', 'task_type': 'task', 'duration': 12, 'story_points': 5, 'due_date': '2026-08-01', 'epic': 'Kalite & Test'
            },
            {
                'title': "Çapraz Tarayıcı (Safari / Firefox) Ekran Testleri",
                'definition': "Vuetify 3 duyarlı arayüzünün Safari ve Firefox mobil görünümlerinin testi.",
                'creator': zeynep, 'assignee': canan, 'sprint': sprint_active, 'state': 'in test',
                'priority': 'low', 'task_type': 'task', 'duration': 6, 'story_points': 2, 'due_date': '2026-08-02', 'epic': 'UI/UX'
            },

            # --- 7. BLOCKED (TEST) (3 Görev) ---
            {
                'title': "Mobil Bildirim Test Ortamı Bağlantı Hatası",
                'definition': "Test sunucusunda SSL sertifikası eksikliği nedeniyle push notification testi engellendi.",
                'creator': user2, 'assignee': canan, 'sprint': sprint_active, 'state': 'blocked test',
                'priority': 'critical', 'task_type': 'bug', 'duration': 20, 'story_points': 5, 'due_date': '2026-07-28', 'epic': 'Kalite & Test'
            },
            {
                'title': "Test Veritabanı SQLite Mock Data Yükleme Hatası",
                'definition': "SQLite veritabanı bellek modunda Foreign Key kısıtlamalarının testi engellemesi.",
                'creator': canan, 'assignee': canan, 'sprint': sprint_active, 'state': 'blocked test',
                'priority': 'high', 'task_type': 'bug', 'duration': 10, 'story_points': 3, 'due_date': '2026-07-29', 'epic': 'Kalite & Test'
            },
            {
                'title': "Safari CORS Preflight Header Engelleme Hatası",
                'definition': "Safari 17+ güncellemelerinde custom header şifreleme isteklerinin bloklanması.",
                'creator': ahmet, 'assignee': canan, 'sprint': sprint_active, 'state': 'blocked test',
                'priority': 'medium', 'task_type': 'bug', 'duration': 8, 'story_points': 2, 'due_date': '2026-07-30', 'epic': 'Güvenlik & OTP'
            },

            # --- 8. DONE (4 Görev) ---
            {
                'title': "Sistem Altyapı Kurulumu ve PostgreSQL Entegrasyonu",
                'definition': "PostgreSQL veritabanı kurulumu ve Django ORM ayarlarının yapılması.",
                'creator': admin_user, 'assignee': user1, 'sprint': sprint_active, 'state': 'done',
                'priority': 'high', 'task_type': 'task', 'duration': 12, 'story_points': 5, 'due_date': '2026-07-15', 'epic': 'Kullanıcı Yönetimi'
            },
            {
                'title': "Admin Log İzleme Ekranı ve Middleware",
                'definition': "RequestLogMiddleware ile tüm HTTP isteklerinin kaydedilmesi ve izlenmesi.",
                'creator': admin_user, 'assignee': user1, 'sprint': sprint_active, 'state': 'done',
                'priority': 'medium', 'task_type': 'task', 'duration': 6, 'story_points': 3, 'due_date': '2026-07-26', 'epic': 'Loglama'
            },
            {
                'title': "Vuetify 3 Arayüz Temizlikleri & Dropdown İyileştirmeleri",
                'definition': "Üst bar menü butonlarının açılır kartlarının ve yönlendirme linklerinin düzeltilmesi.",
                'creator': beyza_user, 'assignee': user2, 'sprint': sprint_active, 'state': 'done',
                'priority': 'low', 'task_type': 'story', 'duration': 8, 'story_points': 2, 'due_date': '2026-07-24', 'epic': 'UI/UX'
            },
            {
                'title': "OTP Kod Hash'leme ve Rate Limiting Güvenliği",
                'definition': "OTP kodunun veritabanında make_password ile saklanması ve Brute-force önlemleri.",
                'creator': admin_user, 'assignee': ahmet, 'sprint': sprint_active, 'state': 'done',
                'priority': 'critical', 'task_type': 'task', 'duration': 14, 'story_points': 8, 'due_date': '2026-07-25', 'epic': 'Güvenlik & OTP'
            }
        ]

        for item in tasks_list:
            t, created = Task.objects.get_or_create(
                title=item['title'],
                defaults=item
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Task '{t.title}' created."))

        self.stdout.write(self.style.SUCCESS("Database initialization and seeding finished successfully with 26+ tasks!"))

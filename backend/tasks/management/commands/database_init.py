import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from tasks.models import Task, Comment, Sprint

User = get_user_model()

class Command(BaseCommand):
    help = 'Runs migrations and initializes the database with default admin, users, sprints, and sample tasks/comments.'

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
            self.stdout.write(self.style.SUCCESS(f"User '{username}' ready."))

        admin_user = created_users['admin']
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

        self.stdout.write(self.style.WARNING("Seeding sample tasks..."))

        tasks_list = [
            # Active Sprint Tasks
            {
                'title': "Sistem Altyapı Kurulumu ve Docker Entegrasyonu",
                'definition': "PostgreSQL veritabanı kurulumu, Nginx reverse proxy ve Docker Compose ortamının hazırlanması.",
                'creator': admin_user, 'assignee': user1, 'sprint': sprint_active, 'state': 'done',
                'priority': 'high', 'task_type': 'task', 'duration': 12, 'story_points': 5, 'due_date': '2026-08-01', 'epic': 'Kullanıcı Yönetimi'
            },
            {
                'title': "OTP 2-Step Authentication & Throttling",
                'definition': "Giriş ekranında 6 haneli OTP kodu üretimi, secrets modülü entegrasyonu ve rate limiting eklenmesi.",
                'creator': admin_user, 'assignee': ahmet, 'sprint': sprint_active, 'state': 'in code review',
                'priority': 'critical', 'task_type': 'task', 'duration': 8, 'story_points': 8, 'due_date': '2026-07-28', 'epic': 'Güvenlik & OTP'
            },
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
                'title': "Admin Log İzleme Ekranı ve Filtreleme",
                'definition': "RequestLogMiddleware ile atılan isteklerin IP, User-Agent ve Endpoint bazlı filtrelenmesi.",
                'creator': admin_user, 'assignee': user1, 'sprint': sprint_active, 'state': 'done',
                'priority': 'medium', 'task_type': 'task', 'duration': 6, 'story_points': 3, 'due_date': '2026-07-26', 'epic': 'Loglama'
            },
            {
                'title': "QA Otomasyon Testlerinin Koşulması",
                'definition': "Giriş, OTP, Şifre Sıfırlama ve Yetki kontrolleri için Selenium/Playwright E2E testleri.",
                'creator': admin_user, 'assignee': canan, 'sprint': sprint_active, 'state': 'in test',
                'priority': 'high', 'task_type': 'task', 'duration': 10, 'story_points': 3, 'due_date': '2026-07-31', 'epic': 'Kalite & Test'
            },

            # Backlog Tasks (sprint = None)
            {
                'title': "GitHub Webhook & Auto PR Status Integration",
                'definition': "Commit atıldığında veya PR birleştirildiğinde ilgili kartın otomatik DONE yapılması.",
                'creator': mehmet, 'assignee': ahmet, 'sprint': None, 'state': 'to do',
                'priority': 'high', 'task_type': 'story', 'duration': 14, 'story_points': 8, 'due_date': '2026-08-10', 'epic': 'DevOps Entegrasyon'
            },
            {
                'title': "Slack Kanalı Anlık Bildirim Botu",
                'definition': "Kritik seviyede bir Hata (Bug) açıldığında Slack kanalına otomatik webhook mesajı atılması.",
                'creator': mehmet, 'assignee': user1, 'sprint': None, 'state': 'to do',
                'priority': 'medium', 'task_type': 'task', 'duration': 8, 'story_points': 3, 'due_date': '2026-08-12', 'epic': 'DevOps Entegrasyon'
            },
            {
                'title': "WebSocket (Django Channels) Canlı Pano Güncellemesi",
                'definition': "Panoda bir kart sürüklendiğinde diğer kullanıcıların ekranında sayfa yenilenmeden güncellenmesi.",
                'creator': zeynep, 'assignee': user2, 'sprint': None, 'state': 'to do',
                'priority': 'critical', 'task_type': 'story', 'duration': 30, 'story_points': 13, 'due_date': '2026-08-15', 'epic': 'Kanban & Sprint'
            },
            {
                'title': "Mobil Bildirim Servisinde Gecikme Hatası",
                'definition': "Android ve iOS bildirim servisinde Firebase mesaj iletim sürelerinin incelenmesi.",
                'creator': canan, 'assignee': ahmet, 'sprint': None, 'state': 'blocked dev',
                'priority': 'critical', 'task_type': 'bug', 'duration': 18, 'story_points': 5, 'due_date': '2026-08-05', 'epic': 'Kalite & Test'
            },
            {
                'title': "Fatura & Abonelik Modülü Arayüz Tasarımı",
                'definition': "Kurumsal müşteriler için paket seçimi ve kredi kartı ödeme adımlarının çizimi.",
                'creator': zeynep, 'assignee': zeynep, 'sprint': None, 'state': 'to do',
                'priority': 'low', 'task_type': 'story', 'duration': 12, 'story_points': 2, 'due_date': '2026-08-20', 'epic': 'Ödeme & Fatura'
            }
        ]

        for item in tasks_list:
            t, created = Task.objects.get_or_create(
                title=item['title'],
                defaults=item
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Task '{t.title}' created."))

        self.stdout.write(self.style.SUCCESS("Database initialization and seeding finished successfully!"))

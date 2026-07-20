import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from tasks.models import Task, Comment

User = get_user_model()

class Command(BaseCommand):
    help = 'Runs migrations and initializes the database with default admin, standard users, and sample tasks/comments.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Running database migrations..."))
        # Run migrations
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS("Migrations completed successfully."))

        self.stdout.write(self.style.WARNING("Seeding database users..."))

        # Create Admin
        admin_username = 'admin'
        admin_email = 'admin@example.com'
        admin_password = 'adminpassword'
        
        admin_user, created = User.objects.get_or_create(username=admin_username, defaults={
            'email': admin_email,
            'is_staff': True,
            'is_superuser': True,
            'department': 'Yönetim'
        })
        if created:
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Superuser '{admin_username}' created successfully."))
        else:
            self.stdout.write(self.style.NOTICE(f"Superuser '{admin_username}' already exists."))

        # Create user1
        user1_username = 'user1'
        user1_email = 'user1@example.com'
        user1_password = 'user1password'
        
        user1, created = User.objects.get_or_create(username=user1_username, defaults={
            'email': user1_email,
            'is_staff': False,
            'is_superuser': False,
            'department': 'Backend Development'
        })
        if created:
            user1.set_password(user1_password)
            user1.save()
            self.stdout.write(self.style.SUCCESS(f"User '{user1_username}' created successfully."))
        else:
            self.stdout.write(self.style.NOTICE(f"User '{user1_username}' already exists."))

        # Create user2
        user2_username = 'user2'
        user2_email = 'user2@example.com'
        user2_password = 'user2password'
        
        user2, created = User.objects.get_or_create(username=user2_username, defaults={
            'email': user2_email,
            'is_staff': False,
            'is_superuser': False,
            'department': 'Frontend Development'
        })
        if created:
            user2.set_password(user2_password)
            user2.save()
            self.stdout.write(self.style.SUCCESS(f"User '{user2_username}' created successfully."))
        else:
            self.stdout.write(self.style.NOTICE(f"User '{user2_username}' already exists."))

        self.stdout.write(self.style.WARNING("Seeding sample tasks..."))

        # Create Task 1
        t1, created = Task.objects.get_or_create(
            title="Sistem Altyapı Kurulumu",
            defaults={
                'definition': "PostgreSQL veritabanı kurulumu ve Django ayarlarının yapılması.",
                'creator': admin_user,
                'assignee': user1,
                'state': 'to do',
                'priority': 'medium',
                'task_type': 'task',
                'duration': 12,
                'due_date': '2026-08-01',
                'epic': 'Kullanıcı Yönetimi',
                'version': 'v1.0'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Task '{t1.title}' created."))

        # Create Task 2
        t2, created = Task.objects.get_or_create(
            title="API Endpoint'lerinin Entegrasyonu",
            defaults={
                'definition': "Kullanıcı CRUD ve Görev yönetim API'lerinin REST standartlarına göre hazırlanması.",
                'creator': admin_user,
                'assignee': user1,
                'state': 'in progress',
                'priority': 'high',
                'task_type': 'task',
                'duration': 8,
                'due_date': '2026-07-25',
                'epic': 'Kullanıcı Yönetimi',
                'version': 'v1.0'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Task '{t2.title}' created."))
            
            # Add comments
            Comment.objects.create(
                task=t2,
                user=user1,
                description="API testleri lokal ortamda tamamlandı, staging sunucusuna deploy edilecek."
            )
            Comment.objects.create(
                task=t2,
                user=admin_user,
                description="Harika, ellerine sağlık. Database migrasyonlarını kontrol ettin mi?"
            )
            self.stdout.write(self.style.SUCCESS("Sample comments added to API task."))

        # Create Task 3
        t3, created = Task.objects.get_or_create(
            title="Arayüz Tasarımı ve Hata Düzeltmeleri",
            defaults={
                'definition': "Vuetify bileşenlerinin entegre edilmesi ve responsive side menu tasarımının tamamlanması.",
                'creator': admin_user,
                'assignee': user2,
                'state': 'done',
                'priority': 'low',
                'task_type': 'story',
                'duration': 24,
                'due_date': '2026-07-15',
                'epic': 'Kanban Panosu',
                'version': 'v1.1'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Task '{t3.title}' created."))

        # Create Task 4
        t4, created = Task.objects.get_or_create(
            title="Kod Gözden Geçirme (Code Review)",
            defaults={
                'definition': "Yazılan yeni API endpoint'lerinin ve serializer validasyon kurallarının PR üzerinden incelenmesi.",
                'creator': admin_user,
                'assignee': user1,
                'state': 'in code review',
                'priority': 'medium',
                'task_type': 'task',
                'duration': 4,
                'due_date': '2026-07-28',
                'epic': 'Kanban Panosu',
                'version': 'v1.1'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Task '{t4.title}' created."))

        # Create Task 5
        t5, created = Task.objects.get_or_create(
            title="Docker Yapılandırma Hatası",
            defaults={
                'definition': "Lokal Docker ortamında Nginx port çakışması nedeniyle geliştirme engellendi.",
                'creator': user1,
                'assignee': user1,
                'state': 'blocked dev',
                'priority': 'critical',
                'task_type': 'bug',
                'duration': 16,
                'due_date': '2026-07-22',
                'epic': 'Raporlama & CSV',
                'version': 'v1.1'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Task '{t5.title}' created."))

        # Create Task 6
        t6, created = Task.objects.get_or_create(
            title="Profil Sayfası Test Hazırlığı",
            defaults={
                'definition': "Yeni eklenen profil güncelleme ve Base64 resim yükleme fonksiyonlarının test senaryolarının yazılması.",
                'creator': admin_user,
                'assignee': user2,
                'state': 'ready for test',
                'priority': 'high',
                'task_type': 'story',
                'duration': 18,
                'due_date': '2026-07-30',
                'epic': 'Kullanıcı Yönetimi',
                'version': 'v2.0'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Task '{t6.title}' created."))

        # Create Task 7
        t7, created = Task.objects.get_or_create(
            title="Entegrasyon Testlerinin Koşulması",
            defaults={
                'definition': "Frontend ve Backend arasındaki API haberleşmesinin uçtan uca (E2E) test edilmesi.",
                'creator': admin_user,
                'assignee': user2,
                'state': 'in test',
                'priority': 'medium',
                'task_type': 'task',
                'duration': 6,
                'due_date': '2026-07-27',
                'epic': 'Kanban Panosu',
                'version': 'v2.0'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Task '{t7.title}' created."))

        # Create Task 8
        t8, created = Task.objects.get_or_create(
            title="Mobil Bildirim Test Hatası",
            defaults={
                'definition': "Test ortamında mobil cihazlara anlık bildirimlerin ulaşmaması hatası araştırılıyor.",
                'creator': user2,
                'assignee': user2,
                'state': 'blocked test',
                'priority': 'critical',
                'task_type': 'bug',
                'duration': 20,
                'due_date': '2026-07-23',
                'epic': 'Raporlama & CSV',
                'version': 'v2.0'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Task '{t8.title}' created."))

        self.stdout.write(self.style.SUCCESS("Database initialization and seeding finished successfully!"))

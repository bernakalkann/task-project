from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import User, Task, Comment, UserProfile

class TaskCollaborationAppTests(APITestCase):

    def setUp(self):
        # Admin kullanıcı oluştur
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        # Normal kullanıcıları oluştur
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1password'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user2password'
        )

        # Görev oluştur
        self.task1 = Task.objects.create(
            title="Task 1",
            definition="Task 1 definition",
            creator=self.admin_user,
            assignee=self.user1,
            state="to do"
        )

        # Yorum oluştur
        self.comment1 = Comment.objects.create(
            task=self.task1,
            user=self.user1,
            description="User1 comment"
        )

    def test_user_serializer_hashes_password(self):
        """UserSerializer ile oluşturulan kullanıcının şifresi veritabanında hashlenmiş olmalı."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "first_name": "New",
            "last_name": "User"
        }
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/api/users/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Kullanıcıyı veritabanından çekip kontrol edelim
        new_user = User.objects.get(username="newuser")
        self.assertTrue(new_user.check_password("newpassword"))

    def test_regular_user_cannot_assign_task_to_others(self):
        """Normal bir kullanıcı başka bir kullanıcıya görev atayamamalı."""
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "New User Task",
            "definition": "User assigning to someone else",
            "assignee": self.user2.id,
            "state": "to do"
        }
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assignee", response.data)

    def test_regular_user_can_assign_task_to_themselves(self):
        """Normal bir kullanıcı kendine görev atayabilmeli."""
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "New User Task",
            "definition": "User assigning to self",
            "assignee": self.user1.id,
            "state": "to do"
        }
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_edit_delete_permissions(self):
        """Bir kullanıcı başkasının yorumunu düzenleyememeli veya silememeli, kendi yorumunu düzenleyebilmeli."""
        # user2, user1'e ait olan comment1'i değiştirmeye çalışıyor
        self.client.force_authenticate(user=self.user2)
        url = f"/api/comments/{self.comment1.id}/"
        
        # Güncelleme testi (Başarısız olmalı)
        response = self.client.patch(url, {"description": "Hacked comment"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Silme testi (Başarısız olmalı)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Sahibi (user1) düzenleyebilmeli
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(url, {"description": "Updated comment"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin silebilmeli
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_export_excel(self):
        """export_excel endpoint'inin kimlik doğrulama gerektirdiğini ve doğru CSV formatını döndüğünü doğrula."""
        # Giriş yapmadan dene (Kimlik doğrulaması hatası almalı)
        response = self.client.get("/api/tasks/export_excel/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Giriş yaparak dene
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/tasks/export_excel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('gorevler.csv', response['Content-Disposition'])

    def test_profile_creation_and_api(self):
        """Kullanıcı oluşturulduğunda profilin otomatik oluştuğunu ve profil API'sinin çalıştığını doğrula."""
        # Yeni bir kullanıcı oluşturalım, post_save sinyalinin çalıştığını görelim
        new_user = User.objects.create_user(
            username='profiletest',
            email='pt@example.com',
            password='testpassword'
        )
        # Profil otomatik oluşmuş mu kontrol et
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())
        profile = new_user.profile
        self.assertEqual(profile.department, 'Yazılım')  # varsayılan değer

        # Giriş yapmadan profil API'sini oku (Kimlik doğrulaması hatası almalı)
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Giriş yaparak profil API'sini oku
        self.client.force_authenticate(user=new_user)
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profiletest')
        self.assertEqual(response.data['department'], 'Yazılım')

        # Profili güncelle
        data = {
            "first_name": "TestAd",
            "last_name": "TestSoyad",
            "department": "Tasarım",
            "position": "Lead Designer",
            "phone": "555-1234"
        }
        response = self.client.patch("/api/profile/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Veritabanında güncellendi mi kontrol et
        new_user.refresh_from_db()
        self.assertEqual(new_user.first_name, "TestAd")
        self.assertEqual(new_user.last_name, "TestSoyad")
        self.assertEqual(new_user.profile.department, "Tasarım")
        self.assertEqual(new_user.profile.position, "Lead Designer")

    def test_task_detailed_fields(self):
        """Görev oluştururken veya güncellerken detaylı alanların (öncelik, tip, süre, teslim tarihi) doğrulandığını doğrula."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "title": "Detailed Task",
            "definition": "Creating a very detailed task",
            "assignee": self.user1.id,
            "state": "to do",
            "priority": "critical",
            "task_type": "bug",
            "duration": 40,
            "due_date": "2026-12-31"
        }
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['priority'], 'critical')
        self.assertEqual(response.data['task_type'], 'bug')
        self.assertEqual(response.data['duration'], 40)
        self.assertEqual(response.data['due_date'], '2026-12-31')

    def test_attachment_upload_and_retrieval(self):
        """Görev ve yorumlar için dosya ekleme (attachment) API'sinin çalıştığını doğrula."""
        self.client.force_authenticate(user=self.admin_user)
        # 1. Görev oluştur
        task_data = {
            "title": "Task with Attachment",
            "definition": "A task that will have an attachment",
            "assignee": self.user1.id,
            "state": "to do"
        }
        task_response = self.client.post("/api/tasks/", task_data)
        task_id = task_response.data['id']

        # 2. Göreve dosya ekle
        attachment_data = {
            "task": task_id,
            "name": "test_document.pdf",
            "file_data": "data:application/pdf;base64,dGVzdF9jb250ZW50",
            "file_type": "application/pdf"
        }
        attach_response = self.client.post("/api/attachments/", attachment_data, format='json')
        self.assertEqual(attach_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(attach_response.data['name'], 'test_document.pdf')
        self.assertEqual(attach_response.data['file_type'], 'application/pdf')

        # 3. Görev detayını çekerek ekin geldiğini doğrula
        task_detail_res = self.client.get(f"/api/tasks/{task_id}/")
        self.assertEqual(len(task_detail_res.data['attachments']), 1)
        self.assertEqual(task_detail_res.data['attachments'][0]['name'], 'test_document.pdf')

    def test_subtask_creation_and_retrieval(self):
        """Alt görev oluşturulabildiğini ve üst görev çekildiğinde alt görevlerin listelendiğini doğrula."""
        self.client.force_authenticate(user=self.admin_user)
        
        # 2. Alt görev oluştur
        subtask_data = {
            "title": "Subtask 1",
            "definition": "Subtask of task1",
            "parent": self.task1.id,
            "assignee": self.user1.id,
            "state": "to do"
        }
        response = self.client.post("/api/tasks/", subtask_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parent'], self.task1.id)
        
        # 3. Ana görevi getiren detay endpoint'ini çağır
        detail_res = self.client.get(f"/api/tasks/{self.task1.id}/")
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertIn('subtasks', detail_res.data)
        self.assertEqual(len(detail_res.data['subtasks']), 1)
        self.assertEqual(detail_res.data['subtasks'][0]['title'], "Subtask 1")

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import User, Task, Comment

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

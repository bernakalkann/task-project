from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import User, Task, Comment, UserProfile, RequestLog
from tasks.crypto_utils import decrypt_data

class TaskCollaborationAppTests(APITestCase):

    def setUp(self):
        # Admin kullanıcı oluştur
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!'
        )
        
        # Normal kullanıcıları oluştur
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='User1Password123!'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='User2Password123!'
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

    def test_password_policy_validation(self):
        """Parola politikası kurallarının (8+ krk, rakam, büyük/küçük harf, sembol) çalıştığını doğrula."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Geçersiz parolalar (Sırasıyla: <8 krk, rakam yok, büyük harf yok, küçük harf yok, sembol yok)
        invalid_passwords = ["Short1!", "NoDigits!", "nodigitsorcaps!", "NODIGITSORLOWER!", "NoSpecialChar123"]
        for pwd in invalid_passwords:
            data = {
                "username": f"user_{pwd[:4]}",
                "email": "test@example.com",
                "password": pwd
            }
            response = self.client.post("/api/users/", data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_serializer_hashes_password(self):
        """UserSerializer ile oluşturulan kullanıcının şifresi veritabanında hashlenmiş olmalı."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "ValidPassword123!",
            "first_name": "New",
            "last_name": "User"
        }
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/api/users/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        new_user = User.objects.get(username="newuser")
        self.assertTrue(new_user.check_password("ValidPassword123!"))

    def test_otp_login_flow(self):
        """2 aşamalı OTP giriş akışını ve hatalı girişte 'girdiğiniz bilgiler hatalı' mesajını doğrula."""
        # 1. Aşama: Hatalı kullanıcı adı / parola
        res_fail = self.client.post("/api/login/", {"username": "user1", "password": "WrongPassword"})
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_fail.data['detail'], 'girdiğiniz bilgiler hatalı')

        # 1. Aşama: Doğru kullanıcı adı / parola (OTP Gönderimi)
        res_step1 = self.client.post("/api/login/", {"username": "user1", "password": "User1Password123!"})
        self.assertEqual(res_step1.status_code, status.HTTP_200_OK)
        self.assertTrue(res_step1.data['otp_required'])
        self.assertEqual(res_step1.data['user_id'], self.user1.id)

        # 2. Aşama: Hatalı OTP kodu
        res_otp_fail = self.client.post("/api/login/verify-otp/", {"user_id": self.user1.id, "otp_code": "000000"})
        self.assertEqual(res_otp_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_otp_fail.data['detail'], 'girdiğiniz bilgiler hatalı')

        # 2. Aşama: Doğru OTP kodu
        self.user1.refresh_from_db()
        correct_otp = self.user1.otp_code
        res_otp_success = self.client.post("/api/login/verify-otp/", {"user_id": self.user1.id, "otp_code": correct_otp})
        self.assertEqual(res_otp_success.status_code, status.HTTP_200_OK)
        self.assertIn('token', res_otp_success.data)

    def test_forgot_and_reset_password_flow(self):
        """Yöntem 2: Şifremi unuttum 6 haneli OTP doğrulama kodu ile şifre sıfırlama akışını doğrula."""
        # 1. Şifremi unuttum isteği at (6 haneli kod üretilir ve mail atılır)
        forgot_res = self.client.post("/api/forgot-password/", {"email": "user1@example.com"})
        self.assertEqual(forgot_res.status_code, status.HTTP_200_OK)

        # 2. Üretilen sıfırlama kodunu veritabanından çek
        self.user1.refresh_from_db()
        reset_code = self.user1.otp_code
        self.assertIsNotNone(reset_code)

        # 3. 6 Haneli kod ve yeni şifre ile reset yap
        reset_res = self.client.post("/api/reset-password/", {
            "email": "user1@example.com",
            "reset_code": reset_code,
            "new_password": "BrandNewPassword123!"
        })
        self.assertEqual(reset_res.status_code, status.HTTP_200_OK)
        
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.check_password("BrandNewPassword123!"))

    def test_profile_creation_and_api_encryption(self):
        """Profil API'sinin şifrelenmiş veri döndüğünü ve şifrenin çözülebildiğini doğrula."""
        new_user = User.objects.create_user(
            username='profiletest',
            email='pt@example.com',
            password='TestPassword123!'
        )
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

        self.client.force_authenticate(user=new_user)
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Yanıtın şifreli olduğunu doğrula
        self.assertTrue(response.data.get('is_encrypted'))
        
        # Şifreli veriyi çözüp kontrol et
        decrypted = decrypt_data(response.data)
        self.assertEqual(decrypted['username'], 'profiletest')
        self.assertEqual(decrypted['department'], 'Yazılım')

    def test_request_log_middleware_and_admin_logs(self):
        """RequestLogMiddleware'in istekleri kaydettiğini ve sadece adminin logs ekranına eriştiğini doğrula."""
        # 1. Normal kullanıcı istek atıyor
        self.client.force_authenticate(user=self.user1)
        self.client.get("/api/tasks/")

        # 2. Normal kullanıcı logs ekranına erişememeli
        log_res_user = self.client.get("/api/logs/")
        self.assertEqual(log_res_user.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Admin logs ekranına erişebilmeli ve loglar listelenmeli
        self.client.force_authenticate(user=self.admin_user)
        log_res_admin = self.client.get("/api/logs/")
        self.assertEqual(log_res_admin.status_code, status.HTTP_200_OK)
        
        decrypted_logs = decrypt_data(log_res_admin.data)
        self.assertTrue(len(decrypted_logs) > 0)

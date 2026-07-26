from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.test import override_settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import User, Task, Comment, UserProfile, RequestLog
from tasks.crypto_utils import decrypt_data

@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
    }
)
class TaskCollaborationAppTests(APITestCase):

    def setUp(self):
        cache.clear()
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

    def test_otp_hashing_and_verification_flow(self):
        """OTP'nin DB'de düz metin saklanmadığını, hash'lendiğini ve tek kullanımlık olduğunu doğrula."""
        # 1. Aşama Login (OTP İsteği)
        res_step1 = self.client.post("/api/login/", {"username": "user1", "password": "User1Password123!"})
        self.assertEqual(res_step1.status_code, status.HTTP_200_OK)
        self.assertTrue(res_step1.data['otp_required'])

        # DB'deki OTP'yi kontrol et (Düz metin saklanmamalı)
        self.user1.refresh_from_db()
        self.assertIsNotNone(self.user1.otp_code)
        self.assertFalse(self.user1.otp_code.isdigit())  # Düz 6 haneli rakam değil PBKDF2 hash'i olmalı

        # 2. Aşama: Hatalı OTP ile deneme
        res_fail = self.client.post("/api/login/verify-otp/", {"user_id": self.user1.id, "otp_code": "000000"})
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_fail.data['detail'], 'Girdiğiniz bilgiler hatalı.')

        # Raw OTP'yi doğrula: check_password() ile test için geçici raw OTP ataması yapıp doğrulayalım
        raw_otp = "123456"
        from django.contrib.auth.hashers import make_password
        self.user1.otp_code = make_password(raw_otp)
        self.user1.otp_created_at = timezone.now()
        self.user1.save()

        # Doğru OTP ile doğrulama yap
        res_otp_success = self.client.post("/api/login/verify-otp/", {"user_id": self.user1.id, "otp_code": raw_otp})
        self.assertEqual(res_otp_success.status_code, status.HTTP_200_OK)
        self.assertIn('token', res_otp_success.data)

        # Doğrulamadan sonra OTP tükendi mi? (Single-Use Token)
        self.user1.refresh_from_db()
        self.assertIsNone(self.user1.otp_code)
        self.assertIsNone(self.user1.otp_created_at)

        # Tekrar aynı OTP ile doğrulama isteği reddedilmeli
        res_reuse = self.client.post("/api/login/verify-otp/", {"user_id": self.user1.id, "otp_code": raw_otp})
        self.assertEqual(res_reuse.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res_reuse.data['detail'], 'Girdiğiniz bilgiler hatalı.')

    def test_otp_expiration_and_attempt_limit(self):
        """Süresi geçmiş OTP ve otp_created_at=None durumlarının reddedildiğini ve 5 denemede iptal olduğunu doğrula."""
        from django.contrib.auth.hashers import make_password

        # Case 1: otp_created_at=None iken istek reddedilmeli
        self.user1.otp_code = make_password("123456")
        self.user1.otp_created_at = None
        self.user1.save()
        res_none_time = self.client.post("/api/login/verify-otp/", {"user_id": self.user1.id, "otp_code": "123456"})
        self.assertEqual(res_none_time.status_code, status.HTTP_400_BAD_REQUEST)

        # Case 2: 5 dakikayı geçmiş OTP reddedilmeli ve temizlenmeli
        self.user1.otp_code = make_password("123456")
        self.user1.otp_created_at = timezone.now() - timedelta(minutes=6)
        self.user1.save()
        res_expired = self.client.post("/api/login/verify-otp/", {"user_id": self.user1.id, "otp_code": "123456"})
        self.assertEqual(res_expired.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.user1.refresh_from_db()
        self.assertIsNone(self.user1.otp_code)

        # Case 3: 5 Hatalı deneme sonrası OTP iptal edilmeli
        cache.clear()
        self.user1.otp_code = make_password("654321")
        self.user1.otp_created_at = timezone.now()
        self.user1.otp_attempt_count = 0
        self.user1.save()

        for _ in range(5):
            self.client.post("/api/login/verify-otp/", {"user_id": self.user1.id, "otp_code": "000000"})
        
        self.user1.refresh_from_db()
        self.assertIsNone(self.user1.otp_code)

    def test_forgot_and_reset_password_security(self):
        """User Enumeration engeli, tek kullanımlık reset OTP ve set_password() kontrolü."""
        # 1. Kayıtlı olmayan e-posta ile istek (User enumeration sızdırmamalı)
        res_anon = self.client.post("/api/forgot-password/", {"email": "nonexistent@example.com"})
        self.assertEqual(res_anon.status_code, status.HTTP_200_OK)
        self.assertNotIn("email", res_anon.data)  # E-posta varlığı sızdırılmamalı

        # 2. Kayıtlı e-posta ile şifremi unuttum isteği
        forgot_res = self.client.post("/api/forgot-password/", {"email": "user1@example.com"})
        self.assertEqual(forgot_res.status_code, status.HTTP_200_OK)

        # Test için bilinen bir raw reset kodu hashleyelim
        from django.contrib.auth.hashers import make_password
        raw_reset = "888999"
        self.user1.otp_code = make_password(raw_reset)
        self.user1.otp_created_at = timezone.now()
        self.user1.save()

        # 3. Yeni şifre sıfırlama
        reset_res = self.client.post("/api/reset-password/", {
            "email": "user1@example.com",
            "reset_code": raw_reset,
            "new_password": "BrandNewPassword123!"
        })
        self.assertEqual(reset_res.status_code, status.HTTP_200_OK)
        
        # Parola set_password() ile hash'lendi mi?
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.check_password("BrandNewPassword123!"))
        self.assertIsNone(self.user1.otp_code)

        # 4. Aynı reset kodu tekrar kullanılamamalı
        reuse_res = self.client.post("/api/reset-password/", {
            "email": "user1@example.com",
            "reset_code": raw_reset,
            "new_password": "AnotherPassword123!"
        })
        self.assertEqual(reuse_res.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertTrue(response.data.get('is_encrypted'))
        
        decrypted = decrypt_data(response.data)
        self.assertEqual(decrypted['username'], 'profiletest')
        self.assertEqual(decrypted['department'], 'Yazılım')

    def test_request_log_middleware_and_admin_logs(self):
        """RequestLogMiddleware'in istekleri kaydettiğini ve sadece adminin logs ekranına eriştiğini doğrula."""
        self.client.force_authenticate(user=self.user1)
        self.client.get("/api/tasks/")

        log_res_user = self.client.get("/api/logs/")
        self.assertEqual(log_res_user.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin_user)
        log_res_admin = self.client.get("/api/logs/")
        self.assertEqual(log_res_admin.status_code, status.HTTP_200_OK)
        
        decrypted_logs = decrypt_data(log_res_admin.data)
        self.assertTrue(len(decrypted_logs) > 0)

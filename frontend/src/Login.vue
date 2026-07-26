<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        
        <!-- GİRİŞ VE OTP KARTI -->
        <v-card class="elevation-12 rounded-xl border">
          <v-toolbar color="primary" dark flat class="px-2">
            <v-icon :icon="step === 1 ? 'mdi-account-lock' : 'mdi-shield-key'" class="mr-2" size="large"></v-icon>
            <v-toolbar-title class="font-weight-bold">
              {{ step === 1 ? 'Giriş Yap' : 'E-posta Doğrulama (OTP)' }}
            </v-toolbar-title>
          </v-toolbar>

          <v-card-text class="pa-6">
            <!-- Genel Hata Uyarısı -->
            <v-alert
              v-if="errorMessage"
              type="error"
              variant="tonal"
              class="mb-4 font-weight-medium"
              closable
              @click:close="errorMessage = ''"
            >
              {{ errorMessage }}
            </v-alert>

            <!-- Başarı Bilgilendirme Uyarısı -->
            <v-alert
              v-if="infoMessage"
              type="info"
              variant="tonal"
              class="mb-4"
              closable
              @click:close="infoMessage = ''"
            >
              {{ infoMessage }}
            </v-alert>

            <!-- AŞAMA 1: KULLANICI ADI & ŞİFRE -->
            <v-form v-if="step === 1" @submit.prevent="handleStep1Login">
              <v-text-field
                v-model="username"
                label="Kullanıcı Adı"
                prepend-inner-icon="mdi-account"
                type="text"
                variant="outlined"
                density="comfortable"
                class="mb-3"
                required
              />

              <v-text-field
                v-model="password"
                label="Şifre"
                prepend-inner-icon="mdi-lock"
                type="password"
                variant="outlined"
                density="comfortable"
                class="mb-2"
                required
              />

              <div class="d-flex justify-end mb-4">
                <v-btn
                  variant="text"
                  color="primary"
                  size="small"
                  class="text-capitalize font-weight-medium px-0"
                  @click="forgotDialog = true"
                >
                  Şifremi Unuttum?
                </v-btn>
              </div>

              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                class="text-capitalize font-weight-bold"
                :loading="loading"
              >
                Devam Et
              </v-btn>
            </v-form>

            <!-- AŞAMA 2: OTP DOĞRULAMA KODU -->
            <v-form v-else @submit.prevent="handleVerifyOTP">
              <p class="text-body-2 text-grey-darken-1 mb-4">
                <strong>{{ maskedEmail }}</strong> adresine gönderilen 6 haneli doğrulama (OTP) kodunu giriniz.
              </p>

              <v-text-field
                v-model="otpCode"
                label="OTP Kodu (6 Haneli)"
                prepend-inner-icon="mdi-numeric"
                type="text"
                maxlength="6"
                placeholder="123456"
                variant="outlined"
                density="comfortable"
                class="mb-4 font-weight-bold text-center"
                required
              />

              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                class="text-capitalize font-weight-bold mb-3"
                :loading="loading"
              >
                Doğrula ve Giriş Yap
              </v-btn>

              <v-btn
                variant="outlined"
                color="grey-darken-1"
                block
                size="small"
                class="text-capitalize"
                @click="resetToStep1"
              >
                <v-icon size="small" class="mr-1">mdi-arrow-left</v-icon> Geri Dön
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- ŞİFREMİ UNUTTUM DIALOG -->
        <v-dialog v-model="forgotDialog" max-width="450">
          <v-card class="rounded-xl">
            <v-card-title class="bg-primary text-white py-3 px-4 font-weight-bold">
              Şifremi Unuttum
            </v-card-title>
            <v-card-text class="pa-6">
              <p class="text-body-2 text-grey-darken-1 mb-4">
                Hesabınıza bağlı e-posta adresinizi giriniz. Size şifre sıfırlama bağlantısı göndereceğiz.
              </p>

              <v-alert v-if="forgotAlert" :type="forgotAlertType" variant="tonal" class="mb-4">
                {{ forgotAlert }}
              </v-alert>

              <v-text-field
                v-model="forgotEmail"
                label="E-posta Adresi"
                prepend-inner-icon="mdi-email-outline"
                type="email"
                variant="outlined"
                density="comfortable"
              />
            </v-card-text>
            <v-card-actions class="pa-4 bg-grey-lighten-4">
              <v-spacer></v-spacer>
              <v-btn variant="text" color="grey-darken-2" @click="forgotDialog = false">İptal</v-btn>
              <v-btn
                color="primary"
                variant="flat"
                :loading="forgotLoading"
                @click="sendForgotPasswordLink"
              >
                Bağlantı Gönder
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from './api'

const router = useRouter()

const step = ref(1) // 1: User/Pass, 2: OTP
const username = ref('')
const password = ref('')
const otpCode = ref('')
const userId = ref(null)
const maskedEmail = ref('')

const errorMessage = ref('')
const infoMessage = ref('')
const loading = ref(false)

// Şifremi unuttum modal değişkenleri
const forgotDialog = ref(false)
const forgotEmail = ref('')
const forgotLoading = ref(false)
const forgotAlert = ref('')
const forgotAlertType = ref('info')

// 1. Aşama: Giriş yapma ve OTP tetikleme
const handleStep1Login = async () => {
  errorMessage.value = ''
  infoMessage.value = ''

  if (!username.value || !password.value) {
    errorMessage.value = 'girdiğiniz bilgiler hatalı'
    return
  }

  loading.value = true
  try {
    const response = await api.post('login/', {
      username: username.value,
      password: password.value
    })

    if (response.data.otp_required) {
      userId.value = response.data.user_id
      maskedEmail.value = response.data.email
      infoMessage.value = response.data.message || 'OTP kodu e-posta adresinize gönderildi.'
      step.value = 2
    }
  } catch (error) {
    console.error("Giriş 1. Aşama Hatası:", error)
    // Şart gereği genel uyarı mesajı kullanılıyor
    errorMessage.value = 'girdiğiniz bilgiler hatalı'
  } finally {
    loading.value = false
  }
}

// 2. Aşama: OTP Doğrulama
const handleVerifyOTP = async () => {
  errorMessage.value = ''
  infoMessage.value = ''

  if (!otpCode.value || otpCode.value.length !== 6) {
    errorMessage.value = 'girdiğiniz bilgiler hatalı'
    return
  }

  loading.value = true
  try {
    const response = await api.post('login/verify-otp/', {
      user_id: userId.value,
      otp_code: otpCode.value
    })

    const token = response.data.token
    const isStaff = response.data.is_staff
    const usernameVal = response.data.username
    const userIdVal = response.data.user_id

    localStorage.setItem('token', token)
    localStorage.setItem('is_staff', String(isStaff))
    localStorage.setItem('username', usernameVal)
    localStorage.setItem('user_id', String(userIdVal))

    router.push('/')
  } catch (error) {
    console.error("OTP Doğrulama Hatası:", error)
    // Şart gereği genel uyarı mesajı kullanılıyor
    errorMessage.value = 'girdiğiniz bilgiler hatalı'
  } finally {
    loading.value = false
  }
}

const resetToStep1 = () => {
  step.value = 1
  otpCode.value = ''
  errorMessage.value = ''
  infoMessage.value = ''
}

// Şifremi Unuttum Bağlantısı Gönder
const sendForgotPasswordLink = async () => {
  if (!forgotEmail.value) {
    forgotAlert.value = 'Lütfen e-posta adresinizi giriniz.'
    forgotAlertType.value = 'warning'
    return
  }

  forgotLoading.value = true
  forgotAlert.value = ''
  try {
    const response = await api.post('forgot-password/', { email: forgotEmail.value })
    forgotAlert.value = response.data.message || 'Şifre sıfırlama bağlantısı gönderildi.'
    forgotAlertType.value = 'success'
    setTimeout(() => {
      forgotDialog.value = false
      forgotEmail.value = ''
      forgotAlert.value = ''
    }, 2000)
  } catch (error) {
    forgotAlert.value = 'Şifre sıfırlama bağlantısı gönderilirken bir hata oluştu.'
    forgotAlertType.value = 'error'
  } finally {
    forgotLoading.value = false
  }
}
</script>
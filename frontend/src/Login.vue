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
                  @click="openForgotDialog"
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

        <!-- ŞİFREMİ UNUTTUM DIALOG (YÖNTEM 2: KOD İLE MODAL İÇİ SIFIRLAMA) -->
        <v-dialog v-model="forgotDialog" max-width="480">
          <v-card class="rounded-xl">
            <v-card-title class="bg-primary text-white py-3 px-4 font-weight-bold d-flex align-center">
              <v-icon icon="mdi-lock-reset" class="mr-2"></v-icon>
              Şifremi Unuttum
            </v-card-title>
            
            <v-card-text class="pa-6">
              <v-alert v-if="forgotAlert" :type="forgotAlertType" variant="tonal" class="mb-4">
                {{ forgotAlert }}
              </v-alert>

              <!-- DIALOG ADIM 1: E-POSTA GİRİŞİ -->
              <div v-if="forgotStep === 1">
                <p class="text-body-2 text-grey-darken-1 mb-4">
                  Hesabınıza bağlı e-posta adresinizi giriniz. Size 6 haneli şifre sıfırlama kodu göndereceğiz.
                </p>

                <v-text-field
                  v-model="forgotEmail"
                  label="E-posta Adresi"
                  prepend-inner-icon="mdi-email-outline"
                  type="email"
                  variant="outlined"
                  density="comfortable"
                  class="mb-2"
                />
              </div>

              <!-- DIALOG ADIM 2: 6 HANELİ KOD VE YENİ ŞİFRE GİRİŞİ -->
              <div v-else>
                <p class="text-body-2 text-grey-darken-1 mb-4">
                  <strong>{{ forgotEmail }}</strong> adresine gönderilen 6 haneli sıfırlama kodunu ve yeni şifrenizi giriniz.
                </p>

                <v-text-field
                  v-model="forgotCode"
                  label="Sıfırlama Kodu (6 Haneli)"
                  prepend-inner-icon="mdi-numeric"
                  type="text"
                  maxlength="6"
                  placeholder="123456"
                  variant="outlined"
                  density="comfortable"
                  class="mb-3 font-weight-bold text-center"
                />

                <v-text-field
                  v-model="forgotNewPassword"
                  label="Yeni Şifre"
                  prepend-inner-icon="mdi-lock-outline"
                  type="password"
                  variant="outlined"
                  density="comfortable"
                  class="mb-2"
                />

                <v-text-field
                  v-model="forgotConfirmPassword"
                  label="Yeni Şifre (Tekrar)"
                  prepend-inner-icon="mdi-lock-check-outline"
                  type="password"
                  variant="outlined"
                  density="comfortable"
                  class="mb-3"
                />

                <!-- ŞİFRE ŞARTLARI CHECKLIST -->
                <v-card variant="tonal" color="indigo" class="pa-3 mb-2 rounded-lg text-caption">
                  <div class="font-weight-bold mb-1">Güvenli Şifre Kuralları:</div>
                  <div :class="rulesStatus.length ? 'text-success' : 'text-grey-darken-1'">
                    <v-icon size="small" :icon="rulesStatus.length ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                    En az 8 karakter
                  </div>
                  <div :class="rulesStatus.digit ? 'text-success' : 'text-grey-darken-1'">
                    <v-icon size="small" :icon="rulesStatus.digit ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                    En az 1 rakam (0-9)
                  </div>
                  <div :class="rulesStatus.upper ? 'text-success' : 'text-grey-darken-1'">
                    <v-icon size="small" :icon="rulesStatus.upper ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                    En az 1 büyük harf (A-Z)
                  </div>
                  <div :class="rulesStatus.lower ? 'text-success' : 'text-grey-darken-1'">
                    <v-icon size="small" :icon="rulesStatus.lower ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                    En az 1 küçük harf (a-z)
                  </div>
                  <div :class="rulesStatus.symbol ? 'text-success' : 'text-grey-darken-1'">
                    <v-icon size="small" :icon="rulesStatus.symbol ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                    En az 1 sembol (!@#$%^&* vb.)
                  </div>
                </v-card>
              </div>
            </v-card-text>

            <v-card-actions class="pa-4 bg-grey-lighten-4">
              <v-btn v-if="forgotStep === 2" variant="text" size="small" @click="forgotStep = 1">
                <v-icon size="small" class="mr-1">mdi-arrow-left</v-icon> Geri
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn variant="text" color="grey-darken-2" @click="forgotDialog = false">İptal</v-btn>
              
              <v-btn
                v-if="forgotStep === 1"
                color="primary"
                variant="flat"
                :loading="forgotLoading"
                @click="sendForgotCode"
              >
                Sıfırlama Kodu Gönder
              </v-btn>

              <v-btn
                v-else
                color="primary"
                variant="flat"
                :loading="forgotLoading"
                :disabled="!isForgotFormValid"
                @click="resetPasswordWithCode"
              >
                Şifreyi Güncelle
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
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

// Şifremi unuttum modal (Yöntem 2) değişkenleri
const forgotDialog = ref(false)
const forgotStep = ref(1) // 1: Email, 2: Code & New Password
const forgotEmail = ref('')
const forgotCode = ref('')
const forgotNewPassword = ref('')
const forgotConfirmPassword = ref('')
const forgotLoading = ref(false)
const forgotAlert = ref('')
const forgotAlertType = ref('info')

const rulesStatus = computed(() => {
  const pwd = forgotNewPassword.value || ''
  return {
    length: pwd.length >= 8,
    digit: /\d/.test(pwd),
    upper: /[A-Z]/.test(pwd),
    lower: /[a-z]/.test(pwd),
    symbol: /[^A-Za-z0-9]/.test(pwd)
  }
})

const isForgotFormValid = computed(() => {
  return (
    forgotCode.value.length === 6 &&
    rulesStatus.value.length &&
    rulesStatus.value.digit &&
    rulesStatus.value.upper &&
    rulesStatus.value.lower &&
    rulesStatus.value.symbol &&
    forgotNewPassword.value === forgotConfirmPassword.value
  )
})

const openForgotDialog = () => {
  forgotDialog.value = true
  forgotStep.value = 1
  forgotEmail.value = ''
  forgotCode.value = ''
  forgotNewPassword.value = ''
  forgotConfirmPassword.value = ''
  forgotAlert.value = ''
}

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

// YÖNTEM 2 - Adım 1: Sıfırlama Kodu Gönder
const sendForgotCode = async () => {
  if (!forgotEmail.value) {
    forgotAlert.value = 'Lütfen e-posta adresinizi giriniz.'
    forgotAlertType.value = 'warning'
    return
  }

  forgotLoading.value = true
  forgotAlert.value = ''
  try {
    const response = await api.post('forgot-password/', { email: forgotEmail.value })
    forgotAlert.value = response.data.message || 'Şifre sıfırlama kodu gönderildi.'
    forgotAlertType.value = 'success'
    forgotStep.value = 2
  } catch (error) {
    forgotAlert.value = 'Şifre sıfırlama kodu gönderilirken bir hata oluştu.'
    forgotAlertType.value = 'error'
  } finally {
    forgotLoading.value = false
  }
}

// YÖNTEM 2 - Adım 2: 6 Haneli Kod ve Yeni Şifre İle Sıfırla
const resetPasswordWithCode = async () => {
  if (!isForgotFormValid.value) return

  forgotLoading.value = true
  forgotAlert.value = ''
  try {
    const response = await api.post('reset-password/', {
      email: forgotEmail.value,
      reset_code: forgotCode.value,
      new_password: forgotNewPassword.value
    })
    forgotAlert.value = response.data.message || 'Şifreniz başarıyla güncellendi!'
    forgotAlertType.value = 'success'
    setTimeout(() => {
      forgotDialog.value = false
      infoMessage.value = 'Şifreniz başarıyla güncellendi. Yeni şifrenizle giriş yapabilirsiniz.'
    }, 2000)
  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail) {
      forgotAlert.value = error.response.data.detail
    } else {
      forgotAlert.value = 'Şifre güncellenirken bir hata oluştu.'
    }
    forgotAlertType.value = 'error'
  } finally {
    forgotLoading.value = false
  }
}
</script>
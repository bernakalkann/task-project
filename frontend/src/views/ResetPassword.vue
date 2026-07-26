<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <v-card class="elevation-12 rounded-xl border">
          <v-toolbar color="indigo-darken-3" dark flat class="px-2">
            <v-icon icon="mdi-lock-reset" class="mr-2" size="large"></v-icon>
            <v-toolbar-title class="font-weight-bold">Şifre Sıfırlama</v-toolbar-title>
          </v-toolbar>

          <v-card-text class="pa-6">
            <v-alert v-if="errorMessage" type="error" variant="tonal" class="mb-4" closable @click:close="errorMessage = ''">
              {{ errorMessage }}
            </v-alert>
            <v-alert v-if="successMessage" type="success" variant="tonal" class="mb-4">
              {{ successMessage }}
            </v-alert>

            <v-form v-if="!successMessage" @submit.prevent="submitReset">
              <v-text-field
                v-model="email"
                label="E-posta Adresi"
                prepend-inner-icon="mdi-email-outline"
                type="email"
                variant="outlined"
                density="comfortable"
                class="mb-2"
                :rules="[v => !!v || 'E-posta zorunludur']"
              />

              <v-text-field
                v-model="resetCode"
                label="6 Haneli Doğrulama Kodu"
                prepend-inner-icon="mdi-numeric"
                type="text"
                maxlength="6"
                placeholder="123456"
                variant="outlined"
                density="comfortable"
                class="mb-2 font-weight-bold text-center"
                :rules="[v => (v && v.length === 6) || '6 haneli kod zorunludur']"
              />

              <v-text-field
                v-model="newPassword"
                label="Yeni Şifre"
                prepend-inner-icon="mdi-lock-outline"
                type="password"
                variant="outlined"
                density="comfortable"
                class="mb-2"
                :rules="[v => !!v || 'Şifre alanı zorunludur']"
              />

              <v-text-field
                v-model="confirmPassword"
                label="Yeni Şifre (Tekrar)"
                prepend-inner-icon="mdi-lock-check-outline"
                type="password"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                :rules="[v => v === newPassword || 'Şifreler eşleşmiyor']"
              />

              <!-- PAROLA ŞARTLARI CHECKLIST -->
              <v-card variant="tonal" color="indigo" class="pa-3 mb-6 rounded-lg text-caption">
                <div class="font-weight-bold mb-1">Güvenli Şifre Kuralları:</div>
                <div :class="rulesStatus.length ? 'text-success' : 'text-grey-darken-1'">
                  <v-icon size="small" :icon="rulesStatus.length ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                  En az 8 karakter uzunluğunda olmalı
                </div>
                <div :class="rulesStatus.digit ? 'text-success' : 'text-grey-darken-1'">
                  <v-icon size="small" :icon="rulesStatus.digit ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                  En az 1 rakam içermeli (0-9)
                </div>
                <div :class="rulesStatus.upper ? 'text-success' : 'text-grey-darken-1'">
                  <v-icon size="small" :icon="rulesStatus.upper ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                  En az 1 büyük harf içermeli (A-Z)
                </div>
                <div :class="rulesStatus.lower ? 'text-success' : 'text-grey-darken-1'">
                  <v-icon size="small" :icon="rulesStatus.lower ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                  En az 1 küçük harf içermeli (a-z)
                </div>
                <div :class="rulesStatus.symbol ? 'text-success' : 'text-grey-darken-1'">
                  <v-icon size="small" :icon="rulesStatus.symbol ? 'mdi-check-circle' : 'mdi-circle-outline'"></v-icon>
                  En az 1 sembol (!@#$%^&* vb.) içermeli
                </div>
              </v-card>

              <v-btn
                type="submit"
                color="indigo-darken-3"
                block
                size="large"
                class="text-capitalize font-weight-bold"
                :loading="loading"
                :disabled="!isFormValid"
              >
                Şifreyi Güncelle
              </v-btn>
            </v-form>

            <div v-else class="text-center mt-4">
              <v-btn color="indigo-darken-3" variant="outlined" to="/login">
                Giriş Ekranına Git
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const email = ref('')
const resetCode = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const loading = ref(false)

const rulesStatus = computed(() => {
  const pwd = newPassword.value || ''
  return {
    length: pwd.length >= 8,
    digit: /\d/.test(pwd),
    upper: /[A-Z]/.test(pwd),
    lower: /[a-z]/.test(pwd),
    symbol: /[^A-Za-z0-9]/.test(pwd)
  }
})

const isFormValid = computed(() => {
  return (
    email.value.length > 0 &&
    resetCode.value.length === 6 &&
    rulesStatus.value.length &&
    rulesStatus.value.digit &&
    rulesStatus.value.upper &&
    rulesStatus.value.lower &&
    rulesStatus.value.symbol &&
    newPassword.value === confirmPassword.value
  )
})

const submitReset = async () => {
  errorMessage.value = ''
  successMessage.value = ''

  loading.value = true
  try {
    const response = await api.post('reset-password/', {
      email: email.value,
      reset_code: resetCode.value,
      new_password: newPassword.value
    })
    successMessage.value = response.data.message || 'Şifreniz başarıyla güncellendi!'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    if (err.response && err.response.data && err.response.data.detail) {
      errorMessage.value = err.response.data.detail
    } else {
      errorMessage.value = 'Şifre güncellenirken bir hata oluştu.'
    }
  } finally {
    loading.value = false
  }
}
</script>

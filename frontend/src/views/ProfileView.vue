<template>
  <v-container class="py-8 fill-height" fluid>
    <v-row justify="center" class="align-stretch">
      
      <!-- SOL TARAF: AVATAR VE GENEL KART -->
      <v-col cols="12" md="4" class="d-flex">
        <v-card class="w-100 pa-6 text-center rounded-xl d-flex flex-column align-center justify-center position-relative" elevation="3" border>
          <!-- Arka Plan Gradient Efekti -->
          <div class="header-gradient position-absolute top-0 left-0 right-0 w-100 rounded-t-xl" style="height: 120px; z-index: 0;"></div>
          
          <div style="z-index: 1;" class="mt-8">
            <!-- Profil Fotoğrafı Alanı -->
            <div class="avatar-container position-relative mb-4">
              <v-avatar size="150" color="indigo-lighten-4" class="elevation-4">
                <v-img v-if="profile.avatar" :src="profile.avatar" alt="Avatar"></v-img>
                <span v-else class="text-h3 font-weight-bold text-indigo-darken-3">
                  {{ initials }}
                </span>
              </v-avatar>
              
              <!-- Düzenleme İkon Butonu (Hover & Click) -->
              <v-btn
                v-if="isEditing"
                icon="mdi-camera"
                color="indigo"
                size="small"
                class="position-absolute bottom-0 right-0 elevation-2 rounded-circle"
                @click="triggerFileInput"
                title="Profil Resmi Değiştir"
              ></v-btn>
              
              <input
                type="file"
                ref="fileInputRef"
                style="display: none"
                accept="image/*"
                @change="onFileChange"
              />
            </div>
            
            <h2 class="text-h5 font-weight-bold text-indigo-darken-4 mb-1">
              {{ profile.first_name }} {{ profile.last_name }}
            </h2>
            <p class="text-subtitle-2 text-grey-darken-1 font-weight-medium mb-3">
              @{{ profile.username }}
            </p>
            
            <v-chip color="indigo" class="font-weight-bold text-uppercase px-4 py-3 elevation-1" size="small" variant="flat">
              {{ profile.department || 'Yazılım' }}
            </v-chip>
          </div>

          <v-divider class="w-100 my-6"></v-divider>

          <div class="w-100 text-left px-4" style="z-index: 1;">
            <div class="d-flex align-center mb-3">
              <v-icon icon="mdi-account-tie" class="mr-2" color="indigo"></v-icon>
              <div>
                <div class="text-caption text-grey-darken-1 font-weight-medium">Pozisyon</div>
                <div class="text-body-2 font-weight-bold text-grey-darken-4">{{ profile.position || 'Belirtilmemiş' }}</div>
              </div>
            </div>

            <div class="d-flex align-center">
              <v-icon icon="mdi-calendar-clock" class="mr-2" color="indigo"></v-icon>
              <div>
                <div class="text-caption text-grey-darken-1 font-weight-medium">Üyelik Tarihi</div>
                <div class="text-body-2 font-weight-bold text-grey-darken-4">{{ formatMembershipDate(profile.created_at) }}</div>
              </div>
            </div>
          </div>
        </v-card>
      </v-col>

      <!-- SAĞ TARAF: DETAYLI BİLGİ KARTLARI -->
      <v-col cols="12" md="8" class="d-flex">
        <v-card class="w-100 pa-8 rounded-xl d-flex flex-column" elevation="3" border>
          <div class="d-flex justify-space-between align-center mb-6">
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
              <v-icon icon="mdi-account-circle-outline" class="mr-2" color="indigo" size="large"></v-icon>
              Profil Bilgileri
            </h1>
            
            <!-- Düzenleme Modu Butonları -->
            <div>
              <v-btn
                v-if="!isEditing"
                color="indigo"
                prepend-icon="mdi-pencil"
                variant="flat"
                elevation="2"
                rounded="lg"
                @click="startEditing"
              >
                Profili Düzenle
              </v-btn>
              <div v-else class="d-flex gap-2">
                <v-btn
                  color="grey"
                  variant="outlined"
                  rounded="lg"
                  @click="cancelEditing"
                >
                  İptal
                </v-btn>
                <v-btn
                  color="indigo"
                  prepend-icon="mdi-check"
                  variant="flat"
                  elevation="2"
                  rounded="lg"
                  :loading="saving"
                  @click="saveProfile"
                >
                  Kaydet
                </v-btn>
              </div>
            </div>
          </div>

          <v-divider class="mb-6"></v-divider>

          <!-- GÖSTERİM VE DÜZENLEME FORMU -->
          <v-form ref="formRef" class="flex-grow-1">
            <!-- Başarı / Hata Alertleri -->
            <v-alert v-if="successMsg" type="success" variant="tonal" class="mb-4 rounded-lg" closable>
              {{ successMsg }}
            </v-alert>
            <v-alert v-if="errorMsg" type="error" variant="tonal" class="mb-4 rounded-lg" closable>
              {{ errorMsg }}
            </v-alert>

            <v-row>
              <!-- AD -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editForm.first_name"
                  label="Ad"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-account"
                  :readonly="!isEditing"
                  :bg-color="!isEditing ? 'grey-lighten-4' : 'surface'"
                ></v-text-field>
              </v-col>

              <!-- SOYAD -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editForm.last_name"
                  label="Soyad"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-account-outline"
                  :readonly="!isEditing"
                  :bg-color="!isEditing ? 'grey-lighten-4' : 'surface'"
                ></v-text-field>
              </v-col>

              <!-- E-POSTA -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editForm.email"
                  label="E-posta"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-email"
                  type="email"
                  :readonly="!isEditing"
                  :bg-color="!isEditing ? 'grey-lighten-4' : 'surface'"
                ></v-text-field>
              </v-col>

              <!-- TELEFON -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editForm.phone"
                  label="Telefon"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-phone"
                  :readonly="!isEditing"
                  :bg-color="!isEditing ? 'grey-lighten-4' : 'surface'"
                ></v-text-field>
              </v-col>

              <!-- DEPARTMAN -->
              <v-col cols="12" sm="6">
                <v-select
                  v-if="isEditing"
                  v-model="editForm.department"
                  :items="departments"
                  label="Departman"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-briefcase"
                ></v-select>
                <v-text-field
                  v-else
                  :model-value="profile.department"
                  label="Departman"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-briefcase"
                  readonly
                  bg-color="grey-lighten-4"
                ></v-text-field>
              </v-col>

              <!-- POZİSYON -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="editForm.position"
                  label="Pozisyon"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-badge-account-horizontal"
                  :readonly="!isEditing"
                  :bg-color="!isEditing ? 'grey-lighten-4' : 'surface'"
                ></v-text-field>
              </v-col>

              <!-- BİYOGRAFİ -->
              <v-col cols="12">
                <v-textarea
                  v-model="editForm.bio"
                  label="Hakkımda (Biyografi)"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-text-short"
                  rows="4"
                  :readonly="!isEditing"
                  :bg-color="!isEditing ? 'grey-lighten-4' : 'surface'"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card>
      </v-col>
      
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const profile = ref({
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  department: '',
  position: '',
  bio: '',
  phone: '',
  avatar: '',
  created_at: null,
})

const editForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  department: '',
  position: '',
  bio: '',
  phone: '',
  avatar: '',
})

const isEditing = ref(false)
const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const fileInputRef = ref(null)
const departments = ['İK', 'Yazılım', 'Satış', 'Tasarım']

// İsim Baş Harflerini Çöz (Placeholder için)
const initials = computed(() => {
  const f = profile.value.first_name || ''
  const l = profile.value.last_name || ''
  if (!f && !l) return profile.value.username ? profile.value.username.substring(0, 2).toUpperCase() : 'U'
  return `${f.charAt(0)}${l.charAt(0)}`.toUpperCase()
})

// Profil Verilerini Çek
const fetchProfile = async () => {
  try {
    const response = await api.get('profile/')
    profile.value = response.data
  } catch (error) {
    console.error("Profil verisi çekilirken hata oluştu:", error)
    errorMsg.value = "Profil bilgileri yüklenemedi."
  }
}

// Üyelik Tarihini Formatla
const formatMembershipDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { year: 'numeric', month: 'long', day: 'numeric' })
}

// Düzenlemeyi Başlat
const startEditing = () => {
  editForm.value = {
    first_name: profile.value.first_name,
    last_name: profile.value.last_name,
    email: profile.value.email,
    department: profile.value.department,
    position: profile.value.position,
    bio: profile.value.bio,
    phone: profile.value.phone,
    avatar: profile.value.avatar,
  }
  successMsg.value = ''
  errorMsg.value = ''
  isEditing.value = true
}

// Düzenlemeyi İptal Et
const cancelEditing = () => {
  isEditing.value = false
  successMsg.value = ''
  errorMsg.value = ''
}

// Dosya Seçiciyi Tetikle
const triggerFileInput = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

// Dosya Değiştiğinde Base64 Oku
const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    // 2MB sınır kontrolü (base64 boyutu artıracağı için)
    if (file.size > 2 * 1024 * 1024) {
      alert("Dosya boyutu 2MB'den küçük olmalıdır.")
      return
    }
    const reader = new FileReader()
    reader.onload = (event) => {
      editForm.value.avatar = event.target.result
    }
    reader.readAsDataURL(file)
  }
}

// Profili Kaydet
const saveProfile = async () => {
  saving.value = true
  successMsg.value = ''
  errorMsg.value = ''
  try {
    const response = await api.put('profile/', editForm.value)
    profile.value = response.data
    isEditing.value = false
    successMsg.value = "Profiliniz başarıyla güncellendi!"
    window.dispatchEvent(new CustomEvent('profile-updated'))
  } catch (error) {
    console.error("Profil kaydedilirken hata oluştu:", error)
    if (error.response && error.response.data) {
      // Hataları birleştirip göster
      const details = Object.entries(error.response.data)
        .map(([key, val]) => `${key}: ${val}`)
        .join(', ')
      errorMsg.value = `Kaydetme hatası: ${details}`
    } else {
      errorMsg.value = "Bilinmeyen bir hata nedeniyle profil güncellenemedi."
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.header-gradient {
  background: linear-gradient(135deg, #3f51b5 0%, #00bcd4 100%);
}
.avatar-container {
  display: inline-block;
}
.gap-2 {
  gap: 8px;
}
.rounded-xl {
  border-radius: 16px !important;
}
</style>

<!-- eslint-disable vue/valid-v-slot -->
<template>
  <v-container class="py-8">
    <!-- Başlık ve Üst Kart -->
    <v-row class="mb-6" align="center">
      <v-col cols="12" sm="6">
        <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
          <v-icon icon="mdi-account-group" class="mr-2" color="indigo"></v-icon>
          Kullanıcı Yönetimi
        </h1>
        <p class="text-subtitle-1 text-grey-darken-1">Sistemdeki tüm kayıtlı kullanıcıları yönetin ve yenilerini ekleyin.</p>
      </v-col>
      
      <!-- Kullanıcı Ekle Butonu -->
      <v-col cols="12" sm="6" class="text-sm-right">
        <v-btn
          color="indigo-darken-2"
          prepend-icon="mdi-account-plus"
          size="large"
          elevation="2"
          @click="openAddDialog"
        >
          Kullanıcı Ekle
        </v-btn>
      </v-col>
    </v-row>

    <!-- Filtreleme ve Arama Kartı -->
    <v-card class="mb-6 pa-4" elevation="1">
      <v-row align="center">
        <v-col cols="12" md="8">
          <v-text-field
            v-model="searchQuery"
            label="Kullanıcı adı, e-posta, ad veya soyada göre ara..."
            prepend-inner-icon="mdi-magnify"
            clearable
            hide-details
            variant="outlined"
            density="comfortable"
            @keyup.enter="fetchUsers"
            @click:clear="clearSearch"
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="4" class="d-flex gap-2">
          <v-btn
            color="indigo"
            prepend-icon="mdi-magnify"
            variant="flat"
            height="48"
            class="flex-grow-1"
            @click="fetchUsers"
          >
            Ara
          </v-btn>
          <v-btn
            color="grey-lighten-2"
            variant="flat"
            height="48"
            @click="clearSearch"
          >
            Temizle
          </v-btn>
        </v-col>
      </v-row>
    </v-card>

    <!-- Tablo Kartı -->
    <v-card elevation="1">
      <v-data-table
        :headers="headers"
        :items="users"
        :loading="loading"
        loading-text="Kullanıcılar yükleniyor..."
        no-data-text="Kayıtlı kullanıcı bulunamadı."
        class="elevation-0"
      >
        <!-- Doğum Tarihi Formatlama -->
        <template v-slot:item.birthday="{ item }">
          {{ formatDate(item.birthday) }}
        </template>

        <!-- Departman Boş Değer Kontrolü -->
        <template v-slot:item.department="{ item }">
          <span :class="item.department ? 'text-black' : 'text-grey-darken-1 italic'">
            {{ item.department || 'Belirtilmemiş' }}
          </span>
        </template>

        <!-- İşlemler (Actions) Sütunu -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            color="red-darken-1"
            variant="text"
            size="small"
            @click="confirmDelete(item)"
            title="Kullanıcıyı Sil"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- KULLANICI EKLEME DİYALOGU (POP-UP) -->
    <v-dialog v-model="addDialog" max-width="600px" persistent>
      <v-card class="pa-4">
        <v-card-title class="text-h5 font-weight-bold text-indigo-darken-3">
          <v-icon icon="mdi-account-plus" class="mr-2" color="indigo"></v-icon>
          Yeni Kullanıcı Ekle
        </v-card-title>
        
        <v-card-text>
          <v-form ref="formRef">
            <v-row class="mt-2">
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.username"
                  label="Kullanıcı Adı *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="apiErrors.username"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.password"
                  label="Şifre *"
                  type="password"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="apiErrors.password"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="form.email"
                  label="E-posta *"
                  type="email"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="apiErrors.email"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.first_name"
                  label="Ad *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="apiErrors.first_name"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.last_name"
                  label="Soyad *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="apiErrors.last_name"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.birthday"
                  label="Doğum Tarihi"
                  type="date"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="apiErrors.birthday"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.department"
                  label="Departman"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="apiErrors.department"
                ></v-text-field>
              </v-col>
            </v-row>
            <p class="text-caption text-grey-darken-1 mt-2">* işaretli alanların doldurulması zorunludur.</p>
          </v-form>
        </v-card-text>

        <v-card-actions class="px-6 py-4">
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="closeAddDialog">İptal</v-btn>
          <v-btn color="indigo-darken-2" variant="flat" :loading="saving" @click="saveUser">Kaydet</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- SİLME ONAY DİYALOGU -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card class="pa-2">
        <v-card-title class="text-h6 font-weight-bold text-red-darken-3">
          <v-icon icon="mdi-alert-circle" class="mr-2" color="red"></v-icon>
          Kullanıcıyı Sil
        </v-card-title>
        <v-card-text class="pt-2">
          <strong>{{ userToDelete?.username }}</strong> adlı kullanıcıyı silmek istediğinize emin misiniz? Bu işlem geri alınamaz.
        </v-card-text>
        <v-card-actions class="px-4 py-3">
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="deleteDialog = false">Hayır</v-btn>
          <v-btn color="red-darken-1" variant="flat" :loading="deleting" @click="deleteUser">Evet, Sil</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const users = ref([])
const loading = ref(false)
const searchQuery = ref('')

// İletişim Kutusu (Dialog) Kontrolleri
const addDialog = ref(false)
const deleteDialog = ref(false)
const saving = ref(false)
const deleting = ref(false)

const userToDelete = ref(null)

// Form Modeli
const form = ref({
  username: '',
  password: '',
  email: '',
  first_name: '',
  last_name: '',
  birthday: '',
  department: '',
})

// Backend'den gelen spesifik alan doğrulama hataları
const apiErrors = ref({})

// Tablo Sütunları
const headers = [
  { title: 'Kullanıcı Adı', key: 'username', align: 'start' },
  { title: 'E-posta', key: 'email' },
  { title: 'Ad', key: 'first_name' },
  { title: 'Soyad', key: 'last_name' },
  { title: 'Doğum Tarihi', key: 'birthday' },
  { title: 'Departman', key: 'department' },
  { title: 'İşlemler', key: 'actions', sortable: false, align: 'center' },
]

// Kullanıcıları Getir (Opsiyonel olarak arama kelimesi içerir)
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value && searchQuery.value.trim() !== '') {
      params.search = searchQuery.value.trim()
    }
    const response = await api.get('users/', { params })
    users.value = response.value || response.data
  } catch (error) {
    console.error("Kullanıcılar yüklenirken hata oluştu:", error)
  } finally {
    loading.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  fetchUsers()
}

// Tarih Formatlama
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR')
}

// Ekleme Diyaloğunu Aç
const openAddDialog = () => {
  apiErrors.value = {}
  form.value = {
    username: '',
    password: '',
    email: '',
    first_name: '',
    last_name: '',
    birthday: null,
    department: '',
  }
  addDialog.value = true
}

// Ekleme Diyaloğunu Kapat
const closeAddDialog = () => {
  addDialog.value = false
  apiErrors.value = {}
}

// Kullanıcıyı Kaydet
const saveUser = async () => {
  // Basit frontend doğrulaması (boş veri girişine izin verme)
  apiErrors.value = {}
  let hasClientError = false

  const requiredFields = ['username', 'password', 'email', 'first_name', 'last_name']
  requiredFields.forEach(field => {
    if (!form.value[field] || form.value[field].trim() === '') {
      apiErrors.value[field] = ['Bu alan zorunludur.']
      hasClientError = true
    }
  })

  if (hasClientError) return

  saving.value = true
  try {
    // Backend API'ye gönder (django veri girişini serializers.py üzerinden yakalar)
    await api.post('users/', form.value)
    addDialog.value = false
    fetchUsers() // listeyi yenile
  } catch (error) {
    console.error("Kullanıcı kaydedilirken hata oluştu:", error)
    if (error.response && error.response.status === 400) {
      // Backend'den gelen alan bazlı doğrulamaları forma yansıt
      apiErrors.value = error.response.data
    } else {
      alert("Kullanıcı eklenirken bilinmeyen bir hata oluştu.")
    }
  } finally {
    saving.value = false
  }
}

// Silme Onay Ekranını Aç
const confirmDelete = (item) => {
  // Farklı Vuetify versiyonlarında item direkt ham nesne olabilir ya da raw alanı içerebilir
  userToDelete.value = item.raw || item
  deleteDialog.value = true
}

// Kullanıcıyı Sil
const deleteUser = async () => {
  if (!userToDelete.value) return
  deleting.value = true
  try {
    const id = userToDelete.value.id
    await api.delete(`users/${id}/`)
    deleteDialog.value = false
    fetchUsers() // listeyi yenile
  } catch (error) {
    console.error("Kullanıcı silinirken hata oluştu:", error)
    alert("Kullanıcı silinemedi. Yetkiniz olmayabilir veya bir hata oluştu.")
  } finally {
    deleting.value = false
    userToDelete.value = null
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>

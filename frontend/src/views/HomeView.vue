<template>
  <v-container class="py-8" fluid>
    <v-row justify="center">
      <v-col cols="12" lg="10">
        
        <!-- ÜST BANNER: HOŞ GELDİNİZ VE GENEL İLERLEME -->
        <v-card class="pa-8 mb-8 rounded-xl text-white position-relative overflow-hidden elevation-3" border>
          <div class="banner-bg position-absolute top-0 left-0 right-0 bottom-0"></div>
          
          <div class="position-relative" style="z-index: 1;">
            <v-row align="center">
              <v-col cols="12" md="8">
                <h1 class="text-h3 font-weight-bold mb-2">
                  {{ greetingText }}
                </h1>
                <p class="text-subtitle-1 text-cyan-accent-1 font-weight-medium mb-4">
                  <span v-if="userProfile?.department">{{ userProfile.department }} Departmanı • </span>
                  {{ isStaff ? 'Sistem Yöneticisi Paneli' : 'Kişisel İş Takip Paneli' }}
                </p>
                <p class="text-body-1 opacity-90 max-width-600">
                  Bugün iş akışınızda toplam <strong>{{ totalTasks }}</strong> görev bulunuyor. 
                  Aşağıdaki grafiklerden görev dağılımını inceleyebilir veya doğrudan panoya gidebilirsiniz.
                </p>
              </v-col>
              
              <!-- GENEL TAMAMLANMA ORANI (LİNEAR PROGRESS) -->
              <v-col cols="12" md="4" class="text-md-right mt-4 mt-md-0">
                <v-card class="bg-white-transparent pa-6 rounded-lg text-center" flat>
                  <div class="text-subtitle-1 font-weight-bold mb-1">Genel İlerleme</div>
                  <div class="text-h3 font-weight-bold mb-3">%{{ donePercentage }}</div>
                  <v-progress-linear
                    v-model="donePercentage"
                    height="8"
                    rounded
                    color="cyan-accent-3"
                    class="bg-white-opacity-20"
                  ></v-progress-linear>
                </v-card>
              </v-col>
            </v-row>
          </div>
        </v-card>

        <!-- KANBAN ÖZET KARTLARI (PROGRESS CIRCLES) -->
        <h2 class="text-h5 font-weight-bold text-indigo-darken-4 mb-6">
          <v-icon icon="mdi-chart-pie" class="mr-2" color="indigo"></v-icon>
          Görev İstatistikleri
        </h2>
        
        <v-row class="mb-8">
          <v-col 
            v-for="status in statusMetadata" 
            :key="status.key" 
            cols="12" 
            sm="6" 
            md="3"
          >
            <v-card class="pa-6 rounded-xl text-center hover-elevate d-flex flex-column align-center" elevation="2" border>
              <div class="text-subtitle-2 font-weight-bold text-grey-darken-1 mb-4 text-truncate w-100">{{ status.title }}</div>
              <v-progress-circular
                :model-value="totalTasks > 0 ? ((summary[status.key] || 0) / totalTasks) * 100 : 0"
                size="90"
                width="8"
                :color="status.color"
                class="mb-4 font-weight-bold text-h6"
              >
                {{ summary[status.key] || 0 }}
              </v-progress-circular>
              <div class="text-caption text-grey-darken-1">Toplam görevin %{{ totalTasks > 0 ? Math.round(((summary[status.key] || 0) / totalTasks) * 100) : 0 }}'si</div>
            </v-card>
          </v-col>
        </v-row>

        <!-- HIZLI ERİŞİM VE KISAYOLLAR -->
        <h2 class="text-h5 font-weight-bold text-indigo-darken-4 mb-6">
          <v-icon icon="mdi-flash" class="mr-2" color="indigo"></v-icon>
          Hızlı Erişim Kısayolları
        </h2>
        
        <v-row>
          <!-- Görevler Kısayolu -->
          <v-col cols="12" sm="6" :md="isStaff ? 4 : 6">
            <v-card class="pa-6 rounded-xl hover-elevate text-center" elevation="2" border to="/tasks">
              <v-avatar color="indigo-lighten-5" size="64" class="mb-3">
                <v-icon icon="mdi-clipboard-text-multiple" color="indigo" size="large"></v-icon>
              </v-avatar>
              <h3 class="text-h6 font-weight-bold mb-1">Görev Panosu</h3>
              <p class="text-body-2 text-grey-darken-1">Kanban panosuna git, görevlerini düzenle veya sürükle.</p>
            </v-card>
          </v-col>

          <!-- Profilim Kısayolu -->
          <v-col cols="12" sm="6" :md="isStaff ? 4 : 6">
            <v-card class="pa-6 rounded-xl hover-elevate text-center" elevation="2" border to="/profile">
              <v-avatar color="teal-lighten-5" size="64" class="mb-3">
                <v-icon icon="mdi-account-circle" color="teal" size="large"></v-icon>
              </v-avatar>
              <h3 class="text-h6 font-weight-bold mb-1">Profil Ayarlarım</h3>
              <p class="text-body-2 text-grey-darken-1">Kişisel bilgilerini düzenle ve profil resmini güncelle.</p>
            </v-card>
          </v-col>

          <!-- Kullanıcı Yönetimi Kısayolu (Sadece Admin) -->
          <v-col v-if="isStaff" cols="12" sm="12" md="4">
            <v-card class="pa-6 rounded-xl hover-elevate text-center" elevation="2" border to="/users">
              <v-avatar color="cyan-lighten-5" size="64" class="mb-3">
                <v-icon icon="mdi-account-group" color="cyan-darken-2" size="large"></v-icon>
              </v-avatar>
              <h3 class="text-h6 font-weight-bold mb-1">Kullanıcı Yönetimi</h3>
              <p class="text-body-2 text-grey-darken-1">Sistemdeki tüm kayıtlı kullanıcıları ve rolleri yönet.</p>
            </v-card>
          </v-col>
        </v-row>

      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const summary = ref({})
const userProfile = ref(null)
const isStaff = ref(localStorage.getItem('is_staff') === 'true')

const statusMetadata = [
  { key: 'to do', title: 'TO DO', color: 'grey-darken-2' },
  { key: 'in progress', title: 'IN PROGRESS', color: 'blue-darken-2' },
  { key: 'in code review', title: 'IN CODE REVIEW', color: 'deep-purple-darken-2' },
  { key: 'blocked dev', title: 'BLOCKED (DEV)', color: 'red-darken-2' },
  { key: 'ready for test', title: 'READY FOR TEST', color: 'orange-darken-2' },
  { key: 'in test', title: 'IN TEST', color: 'indigo-darken-2' },
  { key: 'blocked test', title: 'BLOCKED (TEST)', color: 'red-darken-4' },
  { key: 'done', title: 'DONE', color: 'green-darken-2' }
]

// Görev toplamlarını ve tamamlanma oranını hesapla
const totalTasks = computed(() => {
  return Object.values(summary.value).reduce((sum, count) => sum + count, 0)
})

const donePercentage = computed(() => {
  if (totalTasks.value === 0) return 0
  return Math.round(((summary.value['done'] || 0) / totalTasks.value) * 100)
})

// Dinamik saat bazlı karşılama mesajı
const greetingText = computed(() => {
  const hrs = new Date().getHours()
  const name = userProfile.value?.first_name || localStorage.getItem('username') || 'Kullanıcı'
  if (hrs < 12) return `Günaydın, ${name}! ☀️`
  if (hrs < 17) return `İyi günler, ${name}! ☕`
  if (hrs < 22) return `İyi akşamlar, ${name}! 🌙`
  return `İyi geceler, ${name}! 😴`
})

const fetchSummary = async () => {
  try {
    const response = await api.get('tasks/summary/')
    summary.value = response.data
  } catch (error) {
    console.error("Özet verisi çekilemedi:", error)
  }
}

const fetchProfile = async () => {
  try {
    const response = await api.get('profile/')
    userProfile.value = response.data
  } catch (e) {
    console.error("Profil verisi çekilemedi:", e)
  }
}

onMounted(() => {
  fetchSummary()
  fetchProfile()
})
</script>

<style scoped>
.banner-bg {
  background: linear-gradient(135deg, #3f51b5 0%, #00bcd4 100%);
  opacity: 0.9;
  z-index: 0;
}
.bg-white-transparent {
  background-color: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.bg-white-opacity-20 {
  background-color: rgba(255, 255, 255, 0.2) !important;
}
.rounded-xl {
  border-radius: 20px !important;
}
.max-width-600 {
  max-width: 600px;
}
.hover-elevate {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}
.hover-elevate:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08) !important;
}
</style>

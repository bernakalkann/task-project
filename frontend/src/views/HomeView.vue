<template>
  <v-container class="py-6 px-6" fluid>
    <v-row justify="center">
      <v-col cols="12" lg="11" xl="10">

        <!-- 1. ÜST HERO HERO BANNER: HOŞ GELDİNİZ VE KURUMSAL İLERLEME -->
        <v-card class="pa-8 mb-8 rounded-2xl text-white position-relative overflow-hidden elevation-4 hero-banner">
          <div class="banner-overlay position-absolute top-0 left-0 right-0 bottom-0"></div>
          
          <div class="position-relative" style="z-index: 2;">
            <v-row align="center">
              <v-col cols="12" md="7" lg="8">
                <div class="d-flex align-center mb-3">
                  <v-chip color="cyan-accent-3" size="small" variant="flat" class="font-weight-bold mr-2 text-uppercase">
                    <v-icon icon="mdi-pulse" size="14" class="mr-1"></v-icon> REAL-TIME DASHBOARD
                  </v-chip>
                  <span class="text-caption opacity-80">{{ todayFormatted }}</span>
                </div>

                <h1 class="text-h3 font-weight-bold mb-3 tracking-tight">
                  {{ greetingText }}, {{ displayName }}! 👋
                </h1>
                
                <p class="text-body-1 opacity-90 mb-4 max-width-650">
                  <span v-if="userProfile?.department" class="font-weight-medium text-cyan-lighten-4">
                    {{ userProfile.department }} Departmanı • 
                  </span>
                  Projenizde toplam <strong>{{ totalTasks }}</strong> görev ve <strong>{{ totalStoryPoints }}</strong> story point efor takibi yapılıyor.
                </p>

                <div class="d-flex flex-wrap ga-3">
                  <v-btn
                    color="cyan-accent-3"
                    variant="flat"
                    size="large"
                    class="text-capitalize font-weight-bold text-grey-darken-4 elevation-2"
                    to="/backlog"
                  >
                    <v-icon icon="mdi-format-list-bulleted-triangle" class="mr-2"></v-icon>
                    Backlog & Sprintler
                  </v-btn>

                  <v-btn
                    color="white"
                    variant="outlined"
                    size="large"
                    class="text-capitalize font-weight-bold"
                    to="/tasks"
                  >
                    <v-icon icon="mdi-developer-board" class="mr-2"></v-icon>
                    Kanban Panosuna Git
                  </v-btn>
                </div>
              </v-col>

              <!-- GENEL İLERLEME DAİRESEL ROZETİ -->
              <v-col cols="12" md="5" lg="4" class="text-md-right mt-6 mt-md-0">
                <v-card class="bg-white-glass pa-6 rounded-xl text-center border elevation-2" flat>
                  <div class="text-subtitle-2 font-weight-bold text-uppercase tracking-wider text-cyan-accent-1 mb-2">
                    Proje Tamamlanma Oranı
                  </div>
                  
                  <div class="d-flex align-center justify-center my-3">
                    <v-progress-circular
                      :model-value="donePercentage"
                      size="110"
                      width="10"
                      color="cyan-accent-3"
                      class="font-weight-bold text-h4"
                    >
                      %{{ donePercentage }}
                    </v-progress-circular>
                  </div>

                  <div class="text-caption text-cyan-lighten-4 mt-2">
                    <strong>{{ summary['done'] || 0 }} / {{ totalTasks }}</strong> Görev Tamamlandı
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </div>
        </v-card>

        <!-- 2. KPI METRİK KARTLARI (4'LÜ ADAPTİF GRID) -->
        <v-row class="mb-8">
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-5 rounded-xl border elevation-2 hover-card" color="surface">
              <div class="d-flex justify-space-between align-start mb-3">
                <div>
                  <div class="text-caption font-weight-bold text-grey-darken-1 text-uppercase">Yapılacak (TO DO)</div>
                  <div class="text-h4 font-weight-bold text-grey-darken-3 mt-1">{{ summary['to do'] || 0 }}</div>
                </div>
                <v-avatar color="blue-lighten-5" rounded="lg" size="44">
                  <v-icon icon="mdi-clock-outline" color="blue-darken-2"></v-icon>
                </v-avatar>
              </div>
              <v-progress-linear :model-value="getPercentage('to do')" color="blue" height="6" rounded></v-progress-linear>
              <div class="text-caption text-grey-darken-1 mt-2">Toplam işlerin %{{ getPercentage('to do') }}'si</div>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-5 rounded-xl border elevation-2 hover-card" color="surface">
              <div class="d-flex justify-space-between align-start mb-3">
                <div>
                  <div class="text-caption font-weight-bold text-grey-darken-1 text-uppercase">Geliştirmede (DEV)</div>
                  <div class="text-h4 font-weight-bold text-indigo-darken-3 mt-1">
                    {{ (summary['in progress'] || 0) + (summary['in code review'] || 0) }}
                  </div>
                </div>
                <v-avatar color="indigo-lighten-5" rounded="lg" size="44">
                  <v-icon icon="mdi-code-tags" color="indigo-darken-2"></v-icon>
                </v-avatar>
              </div>
              <v-progress-linear :model-value="getPercentage('in progress') + getPercentage('in code review')" color="indigo" height="6" rounded></v-progress-linear>
              <div class="text-caption text-grey-darken-1 mt-2">In Progress & Code Review</div>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-5 rounded-xl border elevation-2 hover-card" color="surface">
              <div class="d-flex justify-space-between align-start mb-3">
                <div>
                  <div class="text-caption font-weight-bold text-grey-darken-1 text-uppercase">Test Sürecinde (QA)</div>
                  <div class="text-h4 font-weight-bold text-amber-darken-4 mt-1">
                    {{ (summary['ready for test'] || 0) + (summary['in test'] || 0) }}
                  </div>
                </div>
                <v-avatar color="amber-lighten-5" rounded="lg" size="44">
                  <v-icon icon="mdi-test-tube" color="amber-darken-3"></v-icon>
                </v-avatar>
              </div>
              <v-progress-linear :model-value="getPercentage('ready for test') + getPercentage('in test')" color="amber-darken-3" height="6" rounded></v-progress-linear>
              <div class="text-caption text-grey-darken-1 mt-2">Ready for Test & In Test</div>
            </v-card>
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-5 rounded-xl border elevation-2 hover-card" color="surface">
              <div class="d-flex justify-space-between align-start mb-3">
                <div>
                  <div class="text-caption font-weight-bold text-red-darken-2 text-uppercase">Engellenen (BLOCKED)</div>
                  <div class="text-h4 font-weight-bold text-red-darken-3 mt-1">
                    {{ (summary['blocked dev'] || 0) + (summary['blocked test'] || 0) }}
                  </div>
                </div>
                <v-avatar color="red-lighten-5" rounded="lg" size="44">
                  <v-icon icon="mdi-alert-octagon-outline" color="red-darken-2"></v-icon>
                </v-avatar>
              </div>
              <v-progress-linear :model-value="getPercentage('blocked dev') + getPercentage('blocked test')" color="red" height="6" rounded></v-progress-linear>
              <div class="text-caption text-red-darken-2 font-weight-medium mt-2">Dev & Test engelleri var!</div>
            </v-card>
          </v-col>
        </v-row>

        <!-- 3. İŞ AKIŞI BARI VE AKTİF SPRINT ANALİZİ -->
        <v-row class="mb-8">
          <v-col cols="12" md="8">
            <v-card class="pa-6 rounded-2xl border elevation-2" color="surface">
              <div class="d-flex justify-space-between align-center mb-6">
                <div>
                  <h2 class="text-h6 font-weight-bold text-grey-darken-3 mb-1">
                    <v-icon icon="mdi-chart-bar" color="indigo" class="mr-2"></v-icon>
                    8 Kademeli İş Akışı Dağılımı (Workflow Analytics)
                  </h2>
                  <p class="text-caption text-grey-darken-1 mb-0">Tüm görevlerin Kanban aşamalarına göre anlık oranları</p>
                </div>
                <v-chip color="indigo" variant="tonal" class="font-weight-bold" size="small">
                  {{ totalTasks }} Görev
                </v-chip>
              </div>

              <!-- DETAYLI PROGESS BARS -->
              <div v-for="status in statusMetadata" :key="status.key" class="mb-4">
                <div class="d-flex justify-space-between align-center mb-1 text-body-2 font-weight-medium">
                  <span class="d-flex align-center">
                    <v-icon :icon="status.icon" :color="status.color" size="18" class="mr-2"></v-icon>
                    {{ status.title }}
                  </span>
                  <span>
                    <strong>{{ summary[status.key] || 0 }}</strong> Görev 
                    <span class="text-caption text-grey-darken-1 ml-1">(%{{ getPercentage(status.key) }})</span>
                  </span>
                </div>
                <v-progress-linear
                  :model-value="getPercentage(status.key)"
                  height="10"
                  rounded
                  :color="status.color"
                  class="bg-grey-lighten-3"
                ></v-progress-linear>
              </div>
            </v-card>
          </v-col>

          <!-- SAĞ SÜTUN: HIZLI ERİŞİM VE SİSTEM EYLEMLERİ -->
          <v-col cols="12" md="4">
            <v-card class="pa-6 rounded-2xl border elevation-2 mb-6" color="surface">
              <h2 class="text-h6 font-weight-bold text-grey-darken-3 mb-4">
                <v-icon icon="mdi-lightning-bolt" color="amber-darken-3" class="mr-2"></v-icon>
                Hızlı Erişim Hub
              </h2>

              <v-list density="comfortable" nav class="pa-0">
                <v-list-item
                  prepend-icon="mdi-format-list-bulleted-triangle"
                  title="Backlog & Sprintler"
                  subtitle="Sprint planlama ve story puanlama"
                  to="/backlog"
                  color="indigo"
                  class="border rounded-xl mb-3 py-2"
                ></v-list-item>

                <v-list-item
                  prepend-icon="mdi-developer-board"
                  title="Görev Panosu (Kanban)"
                  subtitle="Kartları sürükle, aşamaları yönet"
                  to="/tasks"
                  color="indigo"
                  class="border rounded-xl mb-3 py-2"
                ></v-list-item>

                <v-list-item
                  prepend-icon="mdi-account-cog"
                  title="Profil Ayarlarım"
                  subtitle="Kişisel bilgi ve resim güncelleme"
                  to="/profile"
                  color="indigo"
                  class="border rounded-xl mb-3 py-2"
                ></v-list-item>

                <v-list-item
                  v-if="isStaff"
                  prepend-icon="mdi-shield-text-outline"
                  title="Sistem Logları"
                  subtitle="Admin IP ve network izleme paneli"
                  to="/logs"
                  color="indigo"
                  class="border rounded-xl py-2"
                ></v-list-item>
              </v-list>
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
const recentTasks = ref([])

const displayName = computed(() => {
  if (userProfile.value && userProfile.value.first_name) {
    return `${userProfile.value.first_name}`
  }
  return localStorage.getItem('username') || 'Kullanıcı'
})

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Günaydın'
  if (hour < 18) return 'İyi Günler'
  return 'İyi Akşamlar'
})

const todayFormatted = computed(() => {
  const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  return new Date().toLocaleDateString('tr-TR', options)
})

const statusMetadata = [
  { key: 'to do', title: 'TO DO (Yapılacak)', color: 'grey-darken-2', icon: 'mdi-clock-outline' },
  { key: 'in progress', title: 'IN PROGRESS (Devam Ediyor)', color: 'blue-darken-2', icon: 'mdi-progress-wrench' },
  { key: 'in code review', title: 'IN CODE REVIEW (Kod İncelemesi)', color: 'deep-purple-darken-2', icon: 'mdi-code-json' },
  { key: 'blocked dev', title: 'BLOCKED (DEV Engeli)', color: 'red-darken-2', icon: 'mdi-alert-octagon' },
  { key: 'ready for test', title: 'READY FOR TEST (Teste Hazır)', color: 'orange-darken-2', icon: 'mdi-test-tube' },
  { key: 'in test', title: 'IN TEST (Test Ediliyor)', color: 'indigo-darken-2', icon: 'mdi-checkbox-multiple-marked' },
  { key: 'blocked test', title: 'BLOCKED (TEST Engeli)', color: 'red-darken-4', icon: 'mdi-bug-outline' },
  { key: 'done', title: 'DONE (Tamamlandı)', color: 'emerald', icon: 'mdi-check-circle' }
]

const totalTasks = computed(() => {
  return Object.values(summary.value).reduce((sum, count) => sum + count, 0)
})

const totalStoryPoints = computed(() => {
  return recentTasks.value.reduce((acc, t) => acc + (t.story_points || 1), 0)
})

const donePercentage = computed(() => {
  if (totalTasks.value === 0) return 0
  return Math.round(((summary.value['done'] || 0) / totalTasks.value) * 100)
})

const getPercentage = (key) => {
  if (totalTasks.value === 0) return 0
  return Math.round(((summary.value[key] || 0) / totalTasks.value) * 100)
}

onMounted(async () => {
  try {
    const [summaryRes, profileRes, taskRes] = await Promise.all([
      api.get('tasks/summary/'),
      api.get('profile/'),
      api.get('tasks/')
    ])
    summary.value = summaryRes.data || {}
    userProfile.value = profileRes.data || null
    recentTasks.value = taskRes.data.results || taskRes.data || []
  } catch (error) {
    console.error("Anasayfa verileri yüklenemedi:", error)
  }
})
</script>

<style scoped>
.hero-banner {
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #1e40af 100%);
}

.banner-overlay {
  background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.15), transparent 60%);
}

.bg-white-glass {
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
}

.hover-card {
  transition: all 0.25s ease-in-out;
}

.hover-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.12) !important;
}

.max-width-650 {
  max-width: 650px;
}
</style>

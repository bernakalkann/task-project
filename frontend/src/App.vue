<template>
  <v-app :theme="currentTheme">
    <v-navigation-drawer
      v-if="isLoggedIn"
      v-model="drawer"
      :rail="rail"
      permanent
      app
      color="indigo-darken-4"
      theme="dark"
      elevation="4"
    >
      <v-list-item class="px-4 py-6">
        <template v-slot:prepend>
          <v-icon icon="mdi-orbit" color="cyan-accent-3" size="28" class="mr-2"></v-icon>
        </template>
        <v-list-item-title v-if="!rail" class="text-h6 font-weight-bold text-uppercase tracking-wider">
          GÖREV TAKİP
        </v-list-item-title>
      </v-list-item>
      <v-divider></v-divider>
      <v-list density="compact" nav class="mt-4">
        <v-list-item prepend-icon="mdi-home" title="Anasayfa" value="home" to="/" color="cyan-accent-3"></v-list-item>
        <v-list-item prepend-icon="mdi-format-list-bulleted-triangle" title="Backlog & Sprintler" value="backlog" to="/backlog" color="cyan-accent-3"></v-list-item>
        <v-list-item prepend-icon="mdi-clipboard-text-multiple" title="Görevler (Kanban)" value="tasks" to="/tasks" color="cyan-accent-3"></v-list-item>
        <v-list-item prepend-icon="mdi-account-circle" title="Profilim" value="profile" to="/profile" color="cyan-accent-3"></v-list-item>
        <v-list-item v-if="isStaff" prepend-icon="mdi-account-group" title="Kullanıcılar" value="users" to="/users" color="cyan-accent-3"></v-list-item>
        <v-list-item v-if="isStaff" prepend-icon="mdi-shield-text-outline" title="Sistem Logları" value="logs" to="/logs" color="cyan-accent-3"></v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2 text-right border-t">
          <v-btn
            icon
            variant="text"
            color="grey-lighten-1"
            size="small"
            @click="rail = !rail"
            :title="rail ? 'Menüyü Genişlet' : 'Menüyü Daralt'"
          >
            <v-icon :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"></v-icon>
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- Top Bar (Jira Style) -->
    <v-app-bar v-if="isLoggedIn" app color="surface" elevation="0" border class="px-3">
      <!-- Left Drawer Hamburger Toggle Button -->
      <v-btn icon variant="text" color="grey-darken-2" class="mr-1" @click="drawer = !drawer" title="Sol Menüyü Aç/Kapat">
        <v-icon>mdi-menu</v-icon>
      </v-btn>
      
      <!-- Nine Dots App Switcher Menu -->
      <v-menu location="bottom start">
        <template v-slot:activator="{ props }">
          <v-btn icon variant="text" color="grey-darken-2" class="mr-1" v-bind="props" title="Uygulamalar">
            <v-icon size="24">mdi-apps</v-icon>
          </v-btn>
        </template>
        <v-card width="260" class="rounded-lg elevation-4 border pa-2">
          <v-list density="compact" nav>
            <v-list-subheader class="font-weight-bold text-uppercase">GoJira Uygulamaları</v-list-subheader>
            <v-divider class="my-1"></v-divider>
            <v-list-item prepend-icon="mdi-format-list-bulleted-triangle" title="Backlog & Sprintler" @click="router.push('/backlog')"></v-list-item>
            <v-list-item prepend-icon="mdi-clipboard-text-multiple" title="Görev Panosu (Kanban)" @click="router.push('/tasks')"></v-list-item>
            <v-list-item prepend-icon="mdi-chart-pie" title="Anasayfa Panosu" @click="router.push('/')"></v-list-item>
            <v-list-item prepend-icon="mdi-account-cog" title="Profilim" @click="router.push('/profile')"></v-list-item>
            <v-list-item v-if="isStaff" prepend-icon="mdi-account-group" title="Kullanıcı Yönetimi" @click="router.push('/users')"></v-list-item>
            <v-list-item v-if="isStaff" prepend-icon="mdi-shield-text-outline" title="Sistem Logları" @click="router.push('/logs')"></v-list-item>
          </v-list>
        </v-card>
      </v-menu>
      
      <!-- Jira Logo & Brand -->
      <div class="d-flex align-center cursor-pointer mr-6" @click="router.push('/')">
        <v-icon color="blue-darken-2" size="28" class="mr-2">mdi-jira</v-icon>
        <span class="font-weight-black text-body-1 text-grey-darken-3 tracking-wide" style="font-family: sans-serif;">GoJira</span>
      </div>

      <!-- Çalışma Alanları Dropdown Menu -->
      <v-menu location="bottom start" open-on-click>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="text"
            class="text-capitalize text-grey-darken-3 font-weight-medium px-2 mr-2 d-none d-sm-flex"
            size="small"
            v-bind="props"
            @click="router.push('/tasks')"
          >
            Çalışma Alanları <v-icon size="16" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-card width="280" class="rounded-lg elevation-4 border pa-2">
          <v-list density="compact">
            <v-list-subheader class="font-weight-bold">Mevcut Çalışma Alanı</v-list-subheader>
            <v-list-item prepend-icon="mdi-briefcase-check" title="GoJira Görev Takip Alanı" subtitle="Aktif Alan" color="indigo" active @click="router.push('/tasks')"></v-list-item>
            <v-divider class="my-2"></v-divider>
            <v-list-item prepend-icon="mdi-view-dashboard-variant-outline" title="Tüm Çalışma Alanlarını Gör" @click="router.push('/tasks')"></v-list-item>
          </v-list>
        </v-card>
      </v-menu>

      <!-- Projeler Dropdown Menu -->
      <v-menu location="bottom start" open-on-click>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="text"
            class="text-capitalize text-grey-darken-3 font-weight-medium px-2 mr-2 d-none d-sm-flex"
            size="small"
            v-bind="props"
            @click="router.push('/tasks')"
          >
            Projeler <v-icon size="16" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-card width="280" class="rounded-lg elevation-4 border pa-2">
          <v-list density="compact">
            <v-list-subheader class="font-weight-bold">Son Projeler</v-list-subheader>
            <v-list-item prepend-icon="mdi-folder-text-outline" title="MSP Task Board" subtitle="Yazılım Projesi" @click="router.push('/tasks')"></v-list-item>
            <v-list-item prepend-icon="mdi-bug-outline" title="Sprint & Bug Tracker" subtitle="Hata Takip" @click="router.push('/tasks')"></v-list-item>
            <v-divider class="my-2"></v-divider>
            <v-list-item prepend-icon="mdi-format-list-bulleted" title="Tüm Projeleri İncele" @click="router.push('/tasks')"></v-list-item>
          </v-list>
        </v-card>
      </v-menu>

      <!-- Filtreler Dropdown Menu -->
      <v-menu location="bottom start" open-on-click>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="text"
            class="text-capitalize text-grey-darken-3 font-weight-medium px-2 mr-2 d-none d-sm-flex"
            size="small"
            v-bind="props"
            @click="router.push('/tasks')"
          >
            Filtreler <v-icon size="16" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-card width="260" class="rounded-lg elevation-4 border pa-2">
          <v-list density="compact">
            <v-list-subheader class="font-weight-bold">Hızlı Filtreler</v-list-subheader>
            <v-list-item prepend-icon="mdi-account-check-outline" title="Bana Atanan Görevler" @click="navigateToFilter('assigned_me')"></v-list-item>
            <v-list-item prepend-icon="mdi-alert-decagram-outline" title="Acil (Critical) Görevler" @click="navigateToFilter('critical')"></v-list-item>
            <v-list-item prepend-icon="mdi-bug-outline" title="Hata (Bug) Görevleri" @click="navigateToFilter('bug')"></v-list-item>
            <v-divider class="my-2"></v-divider>
            <v-list-item prepend-icon="mdi-filter-off-outline" title="Tüm Görevleri Gör" @click="router.push('/tasks')"></v-list-item>
          </v-list>
        </v-card>
      </v-menu>

      <!-- Panolar Dropdown Menu -->
      <v-menu location="bottom start" open-on-click>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="text"
            class="text-capitalize text-grey-darken-3 font-weight-medium px-2 mr-6 d-none d-sm-flex"
            size="small"
            v-bind="props"
            @click="router.push('/tasks')"
          >
            Panolar <v-icon size="16" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-card width="260" class="rounded-lg elevation-4 border pa-2">
          <v-list density="compact">
            <v-list-subheader class="font-weight-bold">Mevcut Panolar</v-list-subheader>
            <v-list-item prepend-icon="mdi-format-list-bulleted-triangle" title="Backlog & Sprint Panosu" @click="router.push('/backlog')"></v-list-item>
            <v-list-item prepend-icon="mdi-developer-board" title="Kanban Pano" @click="router.push('/tasks')"></v-list-item>
            <v-list-item prepend-icon="mdi-chart-line" title="İstatistik Panosu" @click="router.push('/')"></v-list-item>
            <v-list-item v-if="isStaff" prepend-icon="mdi-shield-text-outline" title="Admin Log Panosu" @click="router.push('/logs')"></v-list-item>
          </v-list>
        </v-card>
      </v-menu>

      <!-- Create Button -->
      <v-btn color="blue-darken-2" variant="flat" size="small" class="text-capitalize font-weight-bold px-4 mr-4" rounded="sm" @click="triggerGlobalCreate">
        Oluştur
      </v-btn>

      <!-- Search Bar -->
      <div style="width: 220px;" class="mr-auto d-none d-lg-block">
        <v-text-field
          v-model="globalSearch"
          placeholder="Görevlerde ara..."
          variant="outlined"
          density="compact"
          hide-details
          prepend-inner-icon="mdi-magnify"
          style="max-height: 40px;"
          @keyup.enter="handleSearchSubmit"
        ></v-text-field>
      </div>

      <v-spacer class="d-lg-none"></v-spacer>

      <!-- Notification Badge & Menu -->
      <v-menu location="bottom end" :close-on-content-click="false">
        <template v-slot:activator="{ props }">
          <v-btn icon variant="text" color="grey-darken-2" class="mr-1" v-bind="props" title="Bildirimler">
            <v-badge :content="unreadCount" color="error" :model-value="unreadCount > 0">
              <v-icon size="22">mdi-bell-outline</v-icon>
            </v-badge>
          </v-btn>
        </template>

        <v-card width="340" class="rounded-xl elevation-4 border">
          <!-- BAŞLIK VE TÜMÜNÜ OKUNDU İŞARETLE -->
          <div class="px-4 py-3 d-flex align-center justify-space-between bg-grey-lighten-4 border-b">
            <div class="d-flex align-center">
              <v-icon icon="mdi-bell-ring-outline" color="indigo" class="mr-2" size="small"></v-icon>
              <span class="font-weight-bold text-subtitle-2 text-indigo-darken-4">Bildirimler</span>
              <v-chip v-if="unreadCount > 0" size="x-small" color="error" class="ml-2 font-weight-bold" variant="flat">
                {{ unreadCount }} Okunmamış
              </v-chip>
            </div>
            <v-btn
              v-if="unreadCount > 0"
              size="x-small"
              color="indigo"
              variant="text"
              class="font-weight-bold text-capitalize"
              @click="markAllAsRead"
            >
              Tümünü Okundu İşaretle
            </v-btn>
          </div>

          <!-- BİLDİRİM LİSTESİ (5'ERLİ) -->
          <v-list density="comfortable" class="pa-1 overflow-y-auto" style="max-height: 320px;">
            <v-list-item 
              v-for="notif in visibleNotifications" 
              :key="notif.id" 
              class="rounded-lg mb-1 pa-2 border-b-dotted cursor-pointer"
              :class="{'bg-blue-lighten-5': !notif.is_read}"
              @click="markRead(notif.id)"
            >
              <template v-slot:prepend>
                <v-icon :icon="notif.is_read ? 'mdi-bell-check-outline' : 'mdi-circle-medium'" :color="notif.is_read ? 'grey' : 'blue-darken-2'" size="small" class="mr-2"></v-icon>
              </template>
              <v-list-item-title class="text-caption font-weight-medium text-wrap">
                {{ notif.message }}
              </v-list-item-title>
            </v-list-item>

            <v-list-item v-if="notifications.length === 0" class="text-center py-4">
              <v-list-item-title class="text-caption text-grey-darken-1">Henüz bildirim bulunmuyor.</v-list-item-title>
            </v-list-item>
          </v-list>

          <!-- ALTTAN 5'ER ARTIRAN DAHA FAZLA GÖSTER BUTONU -->
          <div v-if="notifications.length > displayedNotifCount" class="pa-2 border-t text-center bg-grey-lighten-5">
            <v-btn
              size="small"
              variant="text"
              color="indigo"
              class="font-weight-bold text-capitalize w-100"
              @click="loadMoreNotifications"
            >
              Daha Fazla Göster (+5)
            </v-btn>
          </div>
        </v-card>
      </v-menu>

      <!-- Help Icon (Yardım Modalı Tetikler) -->
      <v-btn icon variant="text" color="grey-darken-2" class="mr-1 d-none d-sm-flex" @click="helpDialog = true" title="Yardım ve Dokümantasyon">
        <v-icon size="22">mdi-help-circle-outline</v-icon>
      </v-btn>

      <!-- Settings Icon (Profil & Ayarlara Yönlendirir) -->
      <v-btn icon variant="text" color="grey-darken-2" class="mr-1 d-none d-sm-flex" @click="router.push('/profile')" title="Ayarlar">
        <v-icon size="22">mdi-cog-outline</v-icon>
      </v-btn>

      <!-- Theme Switcher -->
      <v-btn icon variant="text" color="grey-darken-2" class="mr-2" @click="toggleTheme" title="Tema Değiştir">
        <v-icon size="22">{{ currentTheme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>

      <!-- Logout -->
      <v-btn icon variant="text" color="red-darken-1" class="mr-2" @click="logout" title="Çıkış Yap">
        <v-icon size="22">mdi-logout</v-icon>
      </v-btn>

      <!-- User Avatar / Initials -->
      <v-avatar color="indigo-darken-2" size="32" class="cursor-pointer font-weight-bold elevation-1 mr-2" @click="router.push('/profile')" title="Profilim">
        <v-img v-if="userAvatar" :src="userAvatar"></v-img>
        <span v-else>{{ username.substring(0, 2).toUpperCase() }}</span>
      </v-avatar>

    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>

    <!-- YARDIM VE REHBER MODALI -->
    <v-dialog v-model="helpDialog" max-width="550">
      <v-card class="rounded-xl">
        <v-card-title class="bg-indigo-darken-4 text-white py-3 px-4 font-weight-bold d-flex align-center">
          <v-icon icon="mdi-help-circle" class="mr-2"></v-icon>
          GoJira Kullanım Rehberi & Yardım
        </v-card-title>
        <v-card-text class="pa-6">
          <v-list density="compact" border rounded class="mb-4">
            <v-list-item prepend-icon="mdi-numeric-1-circle" title="Görev Panosu" subtitle="Kanban panosu üzerinden görev durumlarını sürükleyip bırakarak güncelleyebilirsiniz."></v-list-item>
            <v-divider></v-divider>
            <v-list-item prepend-icon="mdi-numeric-2-circle" title="Yeni Görev Oluştur" subtitle="Üst bardaki 'Oluştur' butonuna tıklayarak yeni görev ekleyebilirsiniz."></v-list-item>
            <v-divider></v-divider>
            <v-list-item prepend-icon="mdi-numeric-3-circle" title="Şifre Güvenliği" subtitle="Parolalar en az 8 karakter, rakam, sembol, büyük ve küçük harf içermelidir."></v-list-item>
            <v-divider></v-divider>
            <v-list-item prepend-icon="mdi-numeric-4-circle" title="OTP ile Giriş" subtitle="Giriş yaparken e-posta adresinize 6 haneli doğrulama kodu (OTP) iletilir."></v-list-item>
            <v-divider></v-divider>
            <v-list-item v-if="isStaff" prepend-icon="mdi-numeric-5-circle" title="Admin Logları" subtitle="Yöneticiler sol menüdeki 'Sistem Logları' ekranından tüm HTTP isteklerini inceleyebilir."></v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions class="pa-4 bg-grey-lighten-4">
          <v-spacer></v-spacer>
          <v-btn color="indigo-darken-4" variant="flat" @click="helpDialog = false">Anladım</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-app>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import api from './api'

const route = useRoute()
const router = useRouter()
const theme = useTheme()

const isLoggedIn = ref(false)
const isStaff = ref(false)
const username = ref('')
const notifications = ref([])
const globalSearch = ref('')
const helpDialog = ref(false)
const drawer = ref(true)
const rail = ref(false)

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)
const currentTheme = computed(() => theme.global.name.value)

const userAvatar = ref('')

// Bildirimleri getir
const fetchNotifications = async () => {
  if (!isLoggedIn.value) return
  try {
    const response = await api.get('notifications/')
    notifications.value = response.data
  } catch (e) {
    console.error("Bildirimler yüklenemedi", e)
  }
}

// Profil bilgilerini getir
const fetchUserProfile = async () => {
  if (!isLoggedIn.value) return
  try {
    const response = await api.get('profile/')
    userAvatar.value = response.data.avatar || ''
  } catch (e) {
    console.error("Profil yüklenemedi", e)
  }
}

const displayedNotifCount = ref(5)

const visibleNotifications = computed(() => {
  return (notifications.value || []).slice(0, displayedNotifCount.value)
})

const loadMoreNotifications = () => {
  displayedNotifCount.value += 5
}

// Tümünü okundu olarak işaretle
const markAllAsRead = async () => {
  try {
    await api.post('notifications/mark_all_as_read/')
    await fetchNotifications()
  } catch (e) {
    console.error("Tümünü okundu işaretleme başarısız", e)
  }
}

// Okundu olarak işaretle
const markRead = async (id) => {
  try {
    await api.post(`notifications/${id}/mark_as_read/`)
    fetchNotifications() // Listeyi güncelle
  } catch (e) {
    console.error("Okundu işareti başarısız", e)
  }
}

const updateLoginStatus = () => {
  isLoggedIn.value = !!localStorage.getItem('token')
  isStaff.value = localStorage.getItem('is_staff') === 'true'
  username.value = localStorage.getItem('username') || ''
  if (isLoggedIn.value) {
    fetchNotifications()
    fetchUserProfile()
  } else {
    userAvatar.value = ''
  }
}

const toggleTheme = () => {
  const newTheme = theme.global.name.value === 'dark' ? 'light' : 'dark'
  theme.global.name.value = newTheme
  localStorage.setItem('theme', newTheme)
}

onMounted(() => {
  updateLoginStatus()
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) theme.global.name.value = savedTheme
  
  // Bildirimleri her 60 saniyede bir otomatik tazele
  setInterval(fetchNotifications, 60000)

  // Profil resmi güncelleme olayını dinle
  window.addEventListener('profile-updated', fetchUserProfile)
})

onUnmounted(() => {
  window.removeEventListener('profile-updated', fetchUserProfile)
})

watch(() => route.path, () => updateLoginStatus())

const logout = () => {
  localStorage.clear()
  isLoggedIn.value = false
  router.push('/login')
  window.location.reload()
}

const triggerGlobalCreate = () => {
  if (route.path === '/tasks') {
    window.dispatchEvent(new CustomEvent('open-create-task'))
  } else {
    router.push({ path: '/tasks', query: { create: 'true' } })
  }
}

const handleSearchSubmit = () => {
  if (!globalSearch.value) return
  router.push({ path: '/tasks', query: { search: globalSearch.value } })
}

const navigateToFilter = (filterType) => {
  router.push({ path: '/tasks', query: { filter: filterType } })
}
</script>
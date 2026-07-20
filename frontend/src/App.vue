<template>
  <v-app :theme="currentTheme">
    <!-- Nav Drawer -->
    <v-navigation-drawer
      v-if="isLoggedIn"
      v-model="drawer"
      app
      color="indigo-darken-4"
      theme="dark"
      elevation="4"
    >
      <v-list-item class="px-4 py-6">
        <v-list-item-title class="text-h6 font-weight-bold text-uppercase tracking-wider">
          <v-icon icon="mdi-orbit" class="mr-2" color="cyan-accent-3"></v-icon>
          GÖREV TAKİP
        </v-list-item-title>
      </v-list-item>
      <v-divider></v-divider>
      <v-list density="compact" nav class="mt-4">
        <v-list-item prepend-icon="mdi-home" title="Anasayfa" value="home" to="/" color="cyan-accent-3"></v-list-item>
        <v-list-item prepend-icon="mdi-clipboard-text-multiple" title="Görevler" value="tasks" to="/tasks" color="cyan-accent-3"></v-list-item>
        <v-list-item prepend-icon="mdi-account-circle" title="Profilim" value="profile" to="/profile" color="cyan-accent-3"></v-list-item>
        <v-list-item v-if="isStaff" prepend-icon="mdi-account-group" title="Kullanıcılar" value="users" to="/users" color="cyan-accent-3"></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Top Bar (Jira Style) -->
    <v-app-bar v-if="isLoggedIn" app color="surface" elevation="0" border class="px-3">
      <!-- Nine Dots App Switcher -->
      <v-btn icon variant="text" color="grey-darken-2" class="mr-1">
        <v-icon size="24">mdi-apps</v-icon>
      </v-btn>
      
      <!-- Jira Logo & Brand -->
      <div class="d-flex align-center cursor-pointer mr-6" @click="router.push('/')">
        <v-icon color="blue-darken-2" size="28" class="mr-2">mdi-jira</v-icon>
        <span class="font-weight-black text-body-1 text-grey-darken-3 tracking-wide" style="font-family: sans-serif;">GoJira</span>
      </div>

      <!-- Left Links -->
      <v-btn variant="text" class="text-capitalize text-grey-darken-3 font-weight-medium px-2 mr-2 d-none d-lg-flex" size="small">Çalışma Alanları <v-icon size="16">mdi-chevron-down</v-icon></v-btn>
      <v-btn variant="text" class="text-capitalize text-grey-darken-3 font-weight-medium px-2 mr-2 d-none d-lg-flex" size="small">Projeler <v-icon size="16">mdi-chevron-down</v-icon></v-btn>
      <v-btn variant="text" class="text-capitalize text-grey-darken-3 font-weight-medium px-2 mr-2 d-none d-lg-flex" size="small">Filtreler <v-icon size="16">mdi-chevron-down</v-icon></v-btn>
      <v-btn variant="text" class="text-capitalize text-grey-darken-3 font-weight-medium px-2 mr-6 d-none d-lg-flex" size="small">Panolar <v-icon size="16">mdi-chevron-down</v-icon></v-btn>

      <!-- Create Button -->
      <v-btn color="blue-darken-2" variant="flat" size="small" class="text-capitalize font-weight-bold px-4 mr-4" rounded="sm" @click="triggerGlobalCreate">
        Oluştur
      </v-btn>

      <!-- Search Bar -->
      <div style="width: 220px;" class="mr-auto d-none d-lg-block">
        <v-text-field
          placeholder="Ara..."
          variant="outlined"
          density="compact"
          hide-details
          prepend-inner-icon="mdi-magnify"
          style="max-height: 40px;"
        ></v-text-field>
      </div>

      <v-spacer class="d-lg-none"></v-spacer>

      <!-- Ask Rovo Button -->
      <v-btn variant="outlined" color="blue" size="small" class="text-capitalize font-weight-bold mr-3 d-none d-lg-flex" prepend-icon="mdi-robot-outline" rounded="sm">
        Ask Rovo
      </v-btn>

      <!-- Notification Badge & Menu -->
      <v-menu location="bottom end" :close-on-content-click="false">
        <template v-slot:activator="{ props }">
          <v-btn icon variant="text" color="grey-darken-2" class="mr-1" v-bind="props">
            <v-badge :content="unreadCount" color="error" :model-value="unreadCount > 0" dot>
              <v-icon size="22">mdi-bell-outline</v-icon>
            </v-badge>
          </v-btn>
        </template>
        <v-card width="300" max-height="400" class="overflow-y-auto rounded-lg" border>
          <v-list>
            <v-list-subheader>Bildirimler</v-list-subheader>
            <v-divider></v-divider>
            <v-list-item 
              v-for="notif in notifications" 
              :key="notif.id" 
              :title="notif.message" 
              @click="markRead(notif.id)"
              :class="{'bg-grey-lighten-4': notif.is_read}"
            >
              <template v-slot:append>
                <v-icon v-if="!notif.is_read" color="blue" size="small">mdi-circle-medium</v-icon>
              </template>
            </v-list-item>
            <v-list-item v-if="notifications.length === 0" title="Yeni bildirim yok"></v-list-item>
          </v-list>
        </v-card>
      </v-menu>

      <!-- Help Icon -->
      <v-btn icon variant="text" color="grey-darken-2" class="mr-1 d-none d-sm-flex">
        <v-icon size="22">mdi-help-circle-outline</v-icon>
      </v-btn>

      <!-- Settings Icon -->
      <v-btn icon variant="text" color="grey-darken-2" class="mr-1 d-none d-sm-flex">
        <v-icon size="22">mdi-cog-outline</v-icon>
      </v-btn>

      <!-- Theme Switcher -->
      <v-btn icon variant="text" color="grey-darken-2" class="mr-2" @click="toggleTheme">
        <v-icon size="22">{{ currentTheme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>

      <!-- Logout -->
      <v-btn icon variant="text" color="red-darken-1" class="mr-2" @click="logout" title="Çıkış Yap">
        <v-icon size="22">mdi-logout</v-icon>
      </v-btn>

      <!-- User Avatar / Initials -->
      <v-avatar color="indigo-darken-2" size="32" class="cursor-pointer font-weight-bold elevation-1 mr-2" @click="router.push('/profile')">
        {{ username.substring(0, 2).toUpperCase() }}
      </v-avatar>

      <!-- Sol Çekmeceyi Açıp Kapatma Butonu (Aesthetics) -->
      <v-btn icon variant="text" color="grey-darken-2" @click="drawer = !drawer">
        <v-icon size="22">mdi-menu</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import api from './api'

const route = useRoute()
const router = useRouter()
const theme = useTheme()

const drawer = ref(true)
const isLoggedIn = ref(false)
const isStaff = ref(false)
const username = ref('')
const notifications = ref([])

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)
const currentTheme = computed(() => theme.global.name.value)

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
  if (isLoggedIn.value) fetchNotifications()
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
  
  // Bildirimleri her 60 saniyede bir otomatik tazele (Canlılık katar)
  setInterval(fetchNotifications, 60000)
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
</script>
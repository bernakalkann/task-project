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
        <v-list-item v-if="isStaff" prepend-icon="mdi-account-group" title="Kullanıcılar" value="users" to="/users" color="cyan-accent-3"></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Top Bar -->
    <v-app-bar v-if="isLoggedIn" app color="surface" elevation="1">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title class="font-weight-medium">Panel</v-app-bar-title>
      <v-spacer></v-spacer>

      <!-- Bildirim Menüsü -->
      <v-menu location="bottom end" :close-on-content-click="false">
        <template v-slot:activator="{ props }">
          <v-btn icon class="mr-2" v-bind="props">
            <v-badge :content="unreadCount" color="error" :model-value="unreadCount > 0">
              <v-icon>mdi-bell</v-icon>
            </v-badge>
          </v-btn>
        </template>
        <v-card width="300" max-height="400" class="overflow-y-auto">
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

      <v-chip class="mr-4" color="indigo" variant="outlined" prepend-icon="mdi-account">
        {{ username }}
      </v-chip>

      <v-btn icon class="mr-2" color="indigo-darken-1" @click="toggleTheme">
        <v-icon>{{ currentTheme === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>

      <v-btn icon color="red-darken-1" class="mr-2" @click="logout">
        <v-icon>mdi-logout</v-icon>
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
</script>
<template>
  <v-app>
    <!-- Nav Drawer (Yan Menü) - Sadece Giriş Yapılmışsa Göster -->
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
        <!-- Home (Anasayfa) -->
        <v-list-item
          prepend-icon="mdi-home"
          title="Anasayfa"
          value="home"
          to="/"
          color="cyan-accent-3"
        ></v-list-item>

        <!-- Tasks (Görevler) -->
        <v-list-item
          prepend-icon="mdi-clipboard-text-multiple"
          title="Görevler"
          value="tasks"
          to="/tasks"
          color="cyan-accent-3"
        ></v-list-item>

        <!-- Users (Kullanıcılar) - Sadece Admin/Staff ise Göster -->
        <v-list-item
          v-if="isStaff"
          prepend-icon="mdi-account-group"
          title="Kullanıcılar"
          value="users"
          to="/users"
          color="cyan-accent-3"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Top Bar (Üst Menü) - Sadece Giriş Yapılmışsa Göster -->
    <v-app-bar v-if="isLoggedIn" app color="white" elevation="1">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      
      <v-app-bar-title class="font-weight-medium">Panel</v-app-bar-title>

      <v-spacer></v-spacer>

      <!-- Kullanıcı Bilgisi -->
      <v-chip class="mr-4" color="indigo" variant="outlined" prepend-icon="mdi-account">
        {{ username }}
        <span v-if="isStaff" class="ml-2 text-caption text-indigo-darken-2 font-weight-bold">
          (Admin)
        </span>
      </v-chip>

      <!-- Tema Değiştirme Butonu -->
      <v-btn icon class="mr-2" color="indigo-darken-1" @click="toggleTheme" title="Tema Değiştir">
        <v-icon>{{ theme.global.name.value === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>

      <!-- Çıkış Yap Butonu -->
      <v-btn icon color="red-darken-1" class="mr-2" @click="logout" title="Çıkış Yap">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- Ana İçerik Alanı -->
    <v-main class="bg-grey-lighten-4">
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTheme } from 'vuetify'

const route = useRoute()
const router = useRouter()
const theme = useTheme()

const drawer = ref(true)
const isLoggedIn = ref(false)
const isStaff = ref(false)
const username = ref('')

const updateLoginStatus = () => {
  isLoggedIn.value = !!localStorage.getItem('token')
  isStaff.value = localStorage.getItem('is_staff') === 'true'
  username.value = localStorage.getItem('username') || ''
}

const toggleTheme = () => {
  const currentTheme = theme.global.name.value
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark'
  theme.global.name.value = newTheme
  localStorage.setItem('theme', newTheme)
}

// Sayfa ilk yüklendiğinde durumu kontrol et
onMounted(() => {
  updateLoginStatus()
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    theme.global.name.value = savedTheme
  }
})

// Rota her değiştiğinde durum bilgisini güncelle
watch(() => route.path, () => {
  updateLoginStatus()
})

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('is_staff')
  localStorage.removeItem('username')
  isLoggedIn.value = false
  isStaff.value = false
  username.value = ''
  router.push('/login')
}
</script>

<style>
.v-navigation-drawer {
  transition: transform 0.2s ease-in-out !important;
}
</style>
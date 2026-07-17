<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const summary = ref({ todo: 0, in_progress: 0, done: 0 })

const fetchSummary = async () => {
  try {
    const response = await api.get('tasks/summary/')
    summary.value = response.data
    console.log("Özet verisi başarıyla çekildi:", summary.value)
  } catch (error) {
    console.error("Özet verisi çekilemedi:", error)
  }
}

onMounted(() => {
  fetchSummary()
})
</script>

<template>
  <v-container class="py-8">
    <h1 class="text-h4 font-weight-bold text-indigo-darken-4 mb-6">
      <v-icon icon="mdi-view-dashboard" class="mr-2" color="indigo"></v-icon>
      Dashboard (Özet Tablosu)
    </h1>
    <v-row>
      <!-- TODO Kartı -->
      <v-col cols="12" md="4">
        <v-card class="pa-6 rounded-lg text-center" border elevation="1">
          <div class="text-subtitle-1 font-weight-bold text-grey-darken-1 mb-2">TODO (Yapılacaklar)</div>
          <div class="text-h3 font-weight-bold text-grey-darken-3">{{ summary.todo }}</div>
        </v-card>
      </v-col>
      
      <!-- IN PROGRESS Kartı -->
      <v-col cols="12" md="4">
        <v-card class="pa-6 rounded-lg text-center" border elevation="1">
          <div class="text-subtitle-1 font-weight-bold text-blue mb-2">IN PROGRESS (İşlemde)</div>
          <div class="text-h3 font-weight-bold text-blue-darken-2">{{ summary.in_progress }}</div>
        </v-card>
      </v-col>
      
      <!-- DONE Kartı -->
      <v-col cols="12" md="4">
        <v-card class="pa-6 rounded-lg text-center" border elevation="1">
          <div class="text-subtitle-1 font-weight-bold text-green mb-2">DONE (Tamamlandı)</div>
          <div class="text-h3 font-weight-bold text-green-darken-2">{{ summary.done }}</div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
/* Vuetify bileşenleri kullanıldığı için özel stil tanımlarına gerek kalmadı */
</style>

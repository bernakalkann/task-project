<script setup>
import { ref, onMounted } from 'vue'
import api from '../api' // api.js dosyasını import ettik

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
  <div class="home">
    <h1>Dashboard</h1>
    <div style="display: flex; gap: 20px;">
      <div class="card">TODO: {{ summary.todo }}</div>
      <div class="card">IN PROGRESS: {{ summary.in_progress }}</div>
      <div class="card">DONE: {{ summary.done }}</div>
    </div>
  </div>
</template>

<style scoped>
.card {
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
}
</style>

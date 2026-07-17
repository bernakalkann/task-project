<template>
  <v-app>
    <v-main>
      <!-- Sayfaların yüklenmesi için bu şart! -->
      <router-view /> 
    </v-main>
  </v-app>
</template>
<script setup>
import Login from './Login.vue'
</script>
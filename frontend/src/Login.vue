<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Giriş Yap</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form>
              <v-text-field v-model="username" label="Kullanıcı Adı" prepend-icon="mdi-account" type="text" />
              <v-text-field v-model="password" label="Şifre" prepend-icon="mdi-lock" type="password" />
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" @click="login">Giriş Yap</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from './api' // api.js dosyanın bulunduğu yolu doğrula (../api veya ./api)

const username = ref('')
const password = ref('')
const router = useRouter()

const login = async () => {
  try {
    const response = await api.post('login/', { 
      username: username.value, 
      password: password.value 
    });
    
    // Token'ı localStorage'a kaydediyoruz
    const token = response.data.token;
    localStorage.setItem('token', token);
    
    console.log("Giriş başarılı, yönlendiriliyor...");
    
    // Başarılı giriş sonrası ana sayfaya yönlendir
    router.push('/');
    
  } catch (error) {
    console.error("Giriş başarısız:", error.response?.data);
    alert("Kullanıcı adı veya şifre hatalı!");
  }
}
</script>
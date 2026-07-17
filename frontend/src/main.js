import { createApp } from 'vue'
import App from './App.vue'
import router from './router' 
// Vuetify kurulumu için gerekli olanları içe aktarıyoruz
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css' // İkonlar için gerekli

// Vuetify'ı oluşturuyoruz
const vuetify = createVuetify({
  components,
  directives,
})

// Uygulamayı oluştururken .use(vuetify) ile ona tanıtıyoruz
const app = createApp(App)
app.use(router)
app.use(vuetify)
app.mount('#app')
<template>
  <v-container class="py-8" fluid>
    <v-row justify="center">
      <v-col cols="12" lg="11">
        
        <!-- BAŞLIK & YENİLEME BUTONLARI -->
        <div class="d-flex align-center justify-space-between mb-6 flex-wrap ga-4">
          <div>
            <h1 class="text-h4 font-weight-bold text-indigo-darken-4 d-flex align-center">
              <v-icon icon="mdi-shield-text-outline" class="mr-3" color="indigo"></v-icon>
              Sistem İstek Logları (Request Logs)
            </h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-1">
              Sayfalarda atılan *bütün* HTTP isteklerinin IP, kullanıcı, user-agent ve network detayları.
            </p>
          </div>

          <div class="d-flex align-center ga-3">
            <v-btn
              color="indigo-darken-3"
              variant="flat"
              prepend-icon="mdi-refresh"
              :loading="loading"
              @click="fetchLogs"
              class="text-capitalize font-weight-bold"
            >
              Yenile
            </v-btn>
          </div>
        </div>

        <!-- FİLTRELEME PANELSİ -->
        <v-card class="pa-4 mb-6 rounded-xl border elevation-2">
          <v-row density="comfortable" align="center">
            <!-- Arama Çubuğu -->
            <v-col cols="12" sm="6" md="4">
              <v-text-field
                v-model="searchQuery"
                placeholder="IP, Kullanıcı, Uç nokta ara..."
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                density="compact"
                hide-details
                clearable
              ></v-text-field>
            </v-col>

            <!-- Metod Filtresi -->
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="selectedMethod"
                :items="methodOptions"
                label="HTTP Metodu"
                variant="outlined"
                density="compact"
                hide-details
                clearable
              ></v-select>
            </v-col>

            <!-- Status Code Filtresi -->
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="selectedStatusGroup"
                :items="statusGroupOptions"
                label="Durum Kodu (Status)"
                variant="outlined"
                density="compact"
                hide-details
                clearable
              ></v-select>
            </v-col>

            <!-- Temizle Butonu -->
            <v-col cols="12" sm="6" md="2" class="text-right">
              <v-btn
                variant="outlined"
                color="grey-darken-2"
                size="small"
                block
                @click="resetFilters"
              >
                Filtreleri Sıfırla
              </v-btn>
            </v-col>
          </v-row>
        </v-card>

        <!-- LOG TABLOSU -->
        <v-card class="rounded-xl border elevation-3 overflow-hidden">
          <v-data-table
            :headers="headers"
            :items="filteredLogs"
            :loading="loading"
            loading-text="Loglar yükleniyor..."
            no-data-text="Kayıtlı log bulunamadı."
            class="elevation-0"
            density="comfortable"
            :items-per-page="15"
          >
            <!-- Zaman Damgası -->
            <template v-slot:item.timestamp="{ item }">
              <span class="text-caption font-weight-medium">
                {{ formatDate(item.timestamp) }}
              </span>
            </template>

            <!-- Kullanıcı -->
            <template v-slot:item.username="{ item }">
              <v-chip
                size="small"
                :color="item.username !== 'Anonymous' ? 'indigo' : 'grey'"
                variant="tonal"
                class="font-weight-bold"
              >
                <v-icon start size="14" :icon="item.username !== 'Anonymous' ? 'mdi-account' : 'mdi-incognito'"></v-icon>
                {{ item.username }}
              </v-chip>
            </template>

            <!-- HTTP Metodu -->
            <template v-slot:item.method="{ item }">
              <v-chip
                size="small"
                :color="getMethodColor(item.method)"
                variant="flat"
                class="font-weight-black text-caption"
              >
                {{ item.method }}
              </v-chip>
            </template>

            <!-- Durum Kodu -->
            <template v-slot:item.status_code="{ item }">
              <v-chip
                size="small"
                :color="getStatusColor(item.status_code)"
                variant="tonal"
                class="font-weight-bold"
              >
                {{ item.status_code }}
              </v-chip>
            </template>

            <!-- Endpoint -->
            <template v-slot:item.endpoint="{ item }">
              <code class="text-body-2 font-weight-bold text-indigo-darken-3">{{ item.endpoint }}</code>
            </template>

            <!-- IP Adresi -->
            <template v-slot:item.ip_address="{ item }">
              <span class="text-body-2 font-mono">{{ item.ip_address || '127.0.0.1' }}</span>
            </template>

            <!-- Detay Butonu -->
            <template v-slot:item.actions="{ item }">
              <v-btn
                icon="mdi-eye-outline"
                size="small"
                variant="text"
                color="indigo"
                title="Detayları Göster"
                @click="openDetailModal(item)"
              ></v-btn>
            </template>
          </v-data-table>
        </v-card>

        <!-- LOG DETAY MODALI -->
        <v-dialog v-model="detailDialog" max-width="600">
          <v-card v-if="selectedLog" class="rounded-xl">
            <v-card-title class="bg-indigo-darken-4 text-white py-3 px-4 font-weight-bold d-flex align-center">
              <v-icon icon="mdi-information-outline" class="mr-2"></v-icon>
              İstek Log Detayı #{{ selectedLog.id }}
            </v-card-title>
            <v-card-text class="pa-6">
              <v-list density="compact" border rounded class="mb-4">
                <v-list-item title="Zaman" :subtitle="formatDate(selectedLog.timestamp)"></v-list-item>
                <v-divider></v-divider>
                <v-list-item title="Kullanıcı" :subtitle="selectedLog.username"></v-list-item>
                <v-divider></v-divider>
                <v-list-item title="IP Adresi" :subtitle="selectedLog.ip_address || '127.0.0.1'"></v-list-item>
                <v-divider></v-divider>
                <v-list-item title="Metod / Endpoint" :subtitle="`${selectedLog.method} ${selectedLog.endpoint}`"></v-list-item>
                <v-divider></v-divider>
                <v-list-item title="Status Code" :subtitle="String(selectedLog.status_code)"></v-list-item>
              </v-list>

              <div class="text-subtitle-2 font-weight-bold mb-1">User Agent:</div>
              <v-card variant="tonal" class="pa-3 rounded-lg text-caption font-mono text-break">
                {{ selectedLog.user_agent || 'Belirtilmemiş' }}
              </v-card>
            </v-card-text>
            <v-card-actions class="pa-4 bg-grey-lighten-4">
              <v-spacer></v-spacer>
              <v-btn color="indigo-darken-3" variant="flat" @click="detailDialog = false">Kapat</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const logs = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedMethod = ref(null)
const selectedStatusGroup = ref(null)

const detailDialog = ref(false)
const selectedLog = ref(null)

const methodOptions = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
const statusGroupOptions = [
  { title: '2xx Başarılı', value: '2xx' },
  { title: '4xx İstemci Hatası', value: '4xx' },
  { title: '5xx Sunucu Hatası', value: '5xx' }
]

const headers = [
  { title: 'Tarih', key: 'timestamp', sortable: true },
  { title: 'Kullanıcı', key: 'username', sortable: true },
  { title: 'Metod', key: 'method', sortable: true },
  { title: 'Uç Nokta (Endpoint)', key: 'endpoint', sortable: true },
  { title: 'Status', key: 'status_code', sortable: true },
  { title: 'IP Adresi', key: 'ip_address', sortable: true },
  { title: 'Detay', key: 'actions', sortable: false }
]

const fetchLogs = async () => {
  loading.value = true
  try {
    const response = await api.get('logs/')
    // Decrypted response is handled automatically by api.js interceptor
    logs.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (error) {
    console.error("Loglar yüklenemedi:", error)
  } finally {
    loading.value = false
  }
}

const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    // 1. Search Query filter
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const matchesIp = (log.ip_address || '').toLowerCase().includes(q)
      const matchesUser = (log.username || '').toLowerCase().includes(q)
      const matchesEndpoint = (log.endpoint || '').toLowerCase().includes(q)
      const matchesUa = (log.user_agent || '').toLowerCase().includes(q)
      if (!matchesIp && !matchesUser && !matchesEndpoint && !matchesUa) return false
    }

    // 2. Method filter
    if (selectedMethod.value && log.method.toUpperCase() !== selectedMethod.value.toUpperCase()) {
      return false
    }

    // 3. Status Code Group filter
    if (selectedStatusGroup.value) {
      const code = log.status_code
      if (selectedStatusGroup.value === '2xx' && (code < 200 || code >= 300)) return false
      if (selectedStatusGroup.value === '4xx' && (code < 400 || code >= 500)) return false
      if (selectedStatusGroup.value === '5xx' && code < 500) return false
    }

    return true
  })
})

const resetFilters = () => {
  searchQuery.value = ''
  selectedMethod.value = null
  selectedStatusGroup.value = null
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('tr-TR', { dateStyle: 'short', timeStyle: 'medium' })
}

const getMethodColor = (method) => {
  switch ((method || '').toUpperCase()) {
    case 'GET': return 'blue-darken-2'
    case 'POST': return 'green-darken-2'
    case 'PUT': return 'orange-darken-2'
    case 'PATCH': return 'purple-darken-2'
    case 'DELETE': return 'red-darken-2'
    default: return 'grey-darken-1'
  }
}

const getStatusColor = (code) => {
  if (code >= 200 && code < 300) return 'green'
  if (code >= 300 && code < 400) return 'cyan'
  if (code >= 400 && code < 500) return 'amber-darken-3'
  if (code >= 500) return 'red'
  return 'grey'
}

const openDetailModal = (log) => {
  selectedLog.value = log
  detailDialog.value = true
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.font-mono {
  font-family: monospace;
}
</style>

<template>
  <v-container fluid class="pa-6">
    <!-- ÜST BAŞLIK VE ÖZET İSTATİSTİKLER -->
    <v-row class="mb-4" align="center">
      <v-col cols="12" md="6">
        <div class="d-flex align-center">
          <v-icon icon="mdi-format-list-bulleted-triangle" color="indigo" size="36" class="mr-3"></v-icon>
          <div>
            <h1 class="text-h4 font-weight-bold text-grey-darken-3">Backlog & Sprint Planlama</h1>
            <p class="text-subtitle-2 text-grey-darken-1 mb-0">
              Görevleri story point puanlarına göre eforlayın ve aktif sprint'e dahil edin.
            </p>
          </div>
        </div>
      </v-col>

      <v-col cols="12" md="6" class="text-md-right">
        <v-btn
          color="indigo-darken-2"
          prepend-icon="mdi-plus-circle"
          class="text-capitalize font-weight-bold mr-2 elevation-2"
          @click="openNewSprintDialog"
        >
          Yeni Sprint Oluştur
        </v-btn>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          class="text-capitalize font-weight-bold elevation-2"
          @click="openNewTaskDialog"
        >
          Görev / Story Ekle
        </v-btn>
      </v-col>
    </v-row>

    <!-- İSTATİSTİK KARTLARI -->
    <v-row class="mb-6">
      <v-col cols="12" sm="4">
        <v-card class="pa-4 rounded-xl border elevation-1" color="indigo-lighten-5">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-caption font-weight-bold text-indigo-darken-3 text-uppercase">Aktif Sprint Eforu</div>
              <div class="text-h4 font-weight-bold text-indigo-darken-4 mt-1">{{ activeSprintStoryPoints }} pts</div>
            </div>
            <v-avatar color="indigo" size="48">
              <v-icon icon="mdi-chart-timeline-variant" color="white"></v-icon>
            </v-avatar>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="4">
        <v-card class="pa-4 rounded-xl border elevation-1" color="amber-lighten-5">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-caption font-weight-bold text-amber-darken-4 text-uppercase">Backlog Havuzu Eforu</div>
              <div class="text-h4 font-weight-bold text-amber-darken-4 mt-1">{{ backlogStoryPoints }} pts</div>
            </div>
            <v-avatar color="amber-darken-3" size="48">
              <v-icon icon="mdi-tray-full" color="white"></v-icon>
            </v-avatar>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="4">
        <v-card class="pa-4 rounded-xl border elevation-1" color="teal-lighten-5">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-caption font-weight-bold text-teal-darken-3 text-uppercase">Toplam Görev Sayısı</div>
              <div class="text-h4 font-weight-bold text-teal-darken-4 mt-1">{{ allTasks.length }} Görev</div>
            </div>
            <v-avatar color="teal" size="48">
              <v-icon icon="mdi-checkbox-multiple-marked-outline" color="white"></v-icon>
            </v-avatar>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 1. AKTİF SPRINT KUTUSU -->
    <v-card class="rounded-xl border mb-6 elevation-2">
      <v-card-title class="bg-indigo-darken-3 text-white py-3 px-4 d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-icon icon="mdi-run-fast" class="mr-2"></v-icon>
          <span class="font-weight-bold">{{ activeSprint ? activeSprint.name : 'Aktif Sprint Bulunmuyor' }}</span>
          <v-chip v-if="activeSprint" size="x-small" color="emerald" class="ml-3 font-weight-bold" variant="flat">
            AKTİF SPRINT
          </v-chip>
        </div>
        <div v-if="activeSprint">
          <v-btn
            size="small"
            color="amber-darken-3"
            variant="flat"
            class="text-capitalize font-weight-bold"
            @click="completeSprint(activeSprint)"
          >
            <v-icon size="small" class="mr-1">mdi-check-all</v-icon> Sprinti Tamamla
          </v-btn>
        </div>
      </v-card-title>

      <v-card-text class="pa-4">
        <div v-if="activeSprint" class="mb-4 pa-3 bg-grey-lighten-4 rounded-lg d-flex align-center justify-space-between">
          <div class="text-body-2 text-grey-darken-2">
            <strong>Hedef:</strong> {{ activeSprint.goal || 'Belirtilmedi' }} | 
            <strong>Tarih:</strong> {{ activeSprint.start_date || 'N/A' }} - {{ activeSprint.end_date || 'N/A' }}
          </div>
          <v-chip size="small" color="indigo" variant="tonal" class="font-weight-bold">
            {{ activeSprintTasks.length }} Görev / {{ activeSprintStoryPoints }} Story Points
          </v-chip>
        </div>

        <div v-if="activeSprintTasks.length === 0" class="text-center py-6 text-grey-darken-1">
          <v-icon icon="mdi-tray-arrow-down" size="40" class="mb-2 text-grey-lighten-1"></v-icon>
          <div>Bu sprint'te henüz görev bulunmuyor. Aşağıdaki Backlog havuzundan görev ekleyebilirsiniz.</div>
        </div>

        <!-- SPRINT GÖREV LİSTESİ -->
        <v-list v-else density="compact" class="pa-0">
          <v-list-item
            v-for="task in activeSprintTasks"
            :key="task.id"
            class="border rounded-lg mb-2 pa-3 elevation-1"
          >
            <template v-slot:prepend>
              <v-chip size="small" :color="getTypeColor(task.task_type)" class="mr-3 font-weight-bold text-uppercase" variant="flat">
                {{ task.task_type }}
              </v-chip>
            </template>

            <v-list-item-title class="font-weight-bold text-grey-darken-3">
              {{ task.title }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption text-grey-darken-1">
              Atanan: <strong>{{ task.assignee_username || 'Atanmamış' }}</strong> | Epic: {{ task.epic || 'Genel' }}
            </v-list-item-subtitle>

            <template v-slot:append>
              <div class="d-flex align-center ga-2">
                <v-chip size="small" :color="getStateColor(task.state)" class="font-weight-bold text-uppercase" variant="tonal">
                  {{ task.state }}
                </v-chip>
                <v-chip size="small" color="indigo" class="font-weight-bold" variant="flat">
                  {{ task.story_points || 1 }} pts
                </v-chip>
                <v-btn
                  size="x-small"
                  color="grey-darken-2"
                  variant="outlined"
                  icon="mdi-tray-arrow-down"
                  title="Backlog'a Al"
                  @click="moveToBacklog(task)"
                ></v-btn>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- 2. BACKLOG HAVUZU -->
    <v-card class="rounded-xl border elevation-2">
      <v-card-title class="bg-grey-darken-3 text-white py-3 px-4 d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-icon icon="mdi-tray-full" class="mr-2"></v-icon>
          <span class="font-weight-bold">Backlog Havuzu (Planlanacak Görevler)</span>
        </div>
        <v-chip size="small" color="amber-darken-3" variant="flat" class="font-weight-bold">
          {{ backlogTasks.length }} Görev / {{ backlogStoryPoints }} Story Points
        </v-chip>
      </v-card-title>

      <v-card-text class="pa-4">
        <div v-if="backlogTasks.length === 0" class="text-center py-8 text-grey-darken-1">
          <v-icon icon="mdi-check-circle-outline" size="48" color="success" class="mb-2"></v-icon>
          <div class="text-subtitle-1 font-weight-bold">Backlog Havuzunuz Temiz!</div>
          <div class="text-caption">Tüm görevler sprint'lere planlandı veya yeni görev ekleyebilirsiniz.</div>
        </div>

        <v-list v-else density="compact" class="pa-0">
          <v-list-item
            v-for="task in backlogTasks"
            :key="task.id"
            class="border rounded-lg mb-2 pa-3 elevation-1"
          >
            <template v-slot:prepend>
              <v-chip size="small" :color="getTypeColor(task.task_type)" class="mr-3 font-weight-bold text-uppercase" variant="flat">
                {{ task.task_type }}
              </v-chip>
            </template>

            <v-list-item-title class="font-weight-bold text-grey-darken-3">
              {{ task.title }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption text-grey-darken-1">
              Atanan: <strong>{{ task.assignee_username || 'Atanmamış' }}</strong> | Öncelik: {{ task.priority }} | Epic: {{ task.epic || 'Genel' }}
            </v-list-item-subtitle>

            <template v-slot:append>
              <div class="d-flex align-center ga-2">
                <v-chip size="small" :color="getPriorityColor(task.priority)" class="font-weight-bold text-uppercase" variant="tonal">
                  {{ task.priority }}
                </v-chip>
                <v-chip size="small" color="amber-darken-3" class="font-weight-bold" variant="flat">
                  {{ task.story_points || 1 }} pts
                </v-chip>

                <v-btn
                  v-if="activeSprint"
                  size="small"
                  color="indigo"
                  variant="flat"
                  class="text-capitalize font-weight-bold ml-2"
                  @click="moveToActiveSprint(task)"
                >
                  <v-icon size="small" class="mr-1">mdi-plus</v-icon> Sprint'e Ekle
                </v-btn>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- YENİ SPRINT OLUŞTURMA DIALOG -->
    <v-dialog v-model="sprintDialog" max-width="500">
      <v-card class="rounded-xl pa-2">
        <v-card-title class="font-weight-bold text-indigo-darken-3">Yeni Sprint Oluştur</v-card-title>
        <v-card-text>
          <v-text-field v-model="newSprint.name" label="Sprint İsmi" variant="outlined" density="comfortable" class="mb-2" />
          <v-textarea v-model="newSprint.goal" label="Sprint Hedefi" rows="2" variant="outlined" density="comfortable" class="mb-2" />
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="newSprint.start_date" label="Başlangıç Tarihi" type="date" variant="outlined" density="comfortable" />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="newSprint.end_date" label="Bitiş Tarihi" type="date" variant="outlined" density="comfortable" />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="px-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="sprintDialog = false">İptal</v-btn>
          <v-btn color="indigo" variant="flat" :loading="sprintLoading" @click="saveSprint">Sprint Oluştur</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- YENİ GÖREV EKLENMESİ DIALOG -->
    <v-dialog v-model="taskDialog" max-width="550">
      <v-card class="rounded-xl pa-2">
        <v-card-title class="font-weight-bold text-primary">Yeni Görev / Story Ekle</v-card-title>
        <v-card-text>
          <v-text-field v-model="newTask.title" label="Görev Başlığı" variant="outlined" density="comfortable" class="mb-2" />
          <v-textarea v-model="newTask.definition" label="Açıklama" rows="3" variant="outlined" density="comfortable" class="mb-2" />
          <v-row>
            <v-col cols="6">
              <v-select v-model="newTask.task_type" label="Tipi" :items="['task', 'bug', 'story', 'epic']" variant="outlined" density="comfortable" />
            </v-col>
            <v-col cols="6">
              <v-select v-model="newTask.priority" label="Öncelik" :items="['low', 'medium', 'high', 'critical']" variant="outlined" density="comfortable" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-select v-model="newTask.story_points" label="Story Point (Efor Puanı)" :items="[1, 2, 3, 5, 8, 13]" variant="outlined" density="comfortable" />
            </v-col>
            <v-col cols="6">
              <v-select v-model="newTask.assignee" label="Atanan Kişi" :items="users" item-title="username" item-value="id" variant="outlined" density="comfortable" />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="px-4">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="taskDialog = false">İptal</v-btn>
          <v-btn color="primary" variant="flat" :loading="taskLoading" @click="saveTask">Kaydet</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const sprints = ref([])
const allTasks = ref([])
const users = ref([])

const sprintDialog = ref(false)
const sprintLoading = ref(false)
const newSprint = ref({ name: '', goal: '', start_date: '', end_date: '' })

const taskDialog = ref(false)
const taskLoading = ref(false)
const newTask = ref({
  title: '',
  definition: '',
  task_type: 'story',
  priority: 'medium',
  story_points: 3,
  assignee: null
})

const activeSprint = computed(() => {
  return sprints.value.find(s => s.status === 'active') || null
})

const activeSprintTasks = computed(() => {
  if (!activeSprint.value) return []
  return allTasks.value.filter(t => t.sprint === activeSprint.value.id)
})

const backlogTasks = computed(() => {
  return allTasks.value.filter(t => !t.sprint)
})

const activeSprintStoryPoints = computed(() => {
  return activeSprintTasks.value.reduce((acc, t) => acc + (t.story_points || 1), 0)
})

const backlogStoryPoints = computed(() => {
  return backlogTasks.value.reduce((acc, t) => acc + (t.story_points || 1), 0)
})

const fetchData = async () => {
  try {
    const [sprintRes, taskRes, userRes] = await Promise.all([
      api.get('sprints/'),
      api.get('tasks/'),
      api.get('users/')
    ])
    sprints.value = sprintRes.data.results || sprintRes.data || []
    allTasks.value = taskRes.data.results || taskRes.data || []
    users.value = userRes.data.results || userRes.data || []
  } catch (err) {
    console.error("Veri yükleme hatası:", err)
  }
}

onMounted(() => {
  fetchData()
})

const openNewSprintDialog = () => {
  newSprint.value = {
    name: `Sprint ${sprints.value.length + 15}`,
    goal: '',
    start_date: new Date().toISOString().substring(0, 10),
    end_date: new Date(Date.now() + 14 * 86400000).toISOString().substring(0, 10)
  }
  sprintDialog.value = true
}

const saveSprint = async () => {
  if (!newSprint.value.name) return
  sprintLoading.value = true
  try {
    await api.post('sprints/', newSprint.value)
    sprintDialog.value = false
    await fetchData()
  } catch (err) {
    console.error("Sprint kaydetme hatası:", err)
  } finally {
    sprintLoading.value = false
  }
}

const openNewTaskDialog = () => {
  const currentUserId = localStorage.getItem('user_id')
  newTask.value = {
    title: '',
    definition: '',
    task_type: 'story',
    priority: 'medium',
    story_points: 3,
    assignee: currentUserId ? Number(currentUserId) : (users.value[0]?.id || null)
  }
  taskDialog.value = true
}

const saveTask = async () => {
  if (!newTask.value.title) return
  taskLoading.value = true
  try {
    await api.post('tasks/', newTask.value)
    taskDialog.value = false
    await fetchData()
  } catch (err) {
    console.error("Görev kaydetme hatası:", err)
  } finally {
    taskLoading.value = false
  }
}

const moveToActiveSprint = async (task) => {
  if (!activeSprint.value) return
  try {
    await api.patch(`tasks/${task.id}/`, { sprint: activeSprint.value.id })
    await fetchData()
  } catch (err) {
    console.error("Sprint'e taşıma hatası:", err)
  }
}

const moveToBacklog = async (task) => {
  try {
    await api.patch(`tasks/${task.id}/`, { sprint: null })
    await fetchData()
  } catch (err) {
    console.error("Backlog'a alma hatası:", err)
  }
}

const completeSprint = async (sprint) => {
  try {
    await api.post(`sprints/${sprint.id}/complete_sprint/`)
    await fetchData()
  } catch (err) {
    console.error("Sprint tamamlama hatası:", err)
  }
}

const getTypeColor = (type) => {
  switch (type) {
    case 'bug': return 'error'
    case 'story': return 'success'
    case 'epic': return 'purple'
    default: return 'info'
  }
}

const getPriorityColor = (priority) => {
  switch (priority) {
    case 'critical': return 'red-darken-3'
    case 'high': return 'deep-orange'
    case 'low': return 'blue-grey'
    default: return 'amber-darken-2'
  }
}

const getStateColor = (state) => {
  switch (state) {
    case 'done': return 'success'
    case 'in progress': return 'indigo'
    case 'in code review': return 'purple'
    case 'blocked dev': return 'error'
    default: return 'grey-darken-1'
  }
}
</script>

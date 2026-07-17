<!-- eslint-disable vue/valid-v-slot -->
<template>
  <v-container class="py-8" fluid>
    <!-- Başlık ve Kontroller -->
    <v-row class="mb-6 mx-2" align="center">
      <v-col cols="12" sm="6">
        <h1 class="text-h4 font-weight-bold text-indigo-darken-4">
          <v-icon icon="mdi-clipboard-text-multiple" class="mr-2" color="indigo"></v-icon>
          Görev Panosu (Kanban)
        </h1>
        <p class="text-subtitle-1 text-grey-darken-1">Görevlerinizi sütunlar arasında sürükleyin, detayları inceleyin ve yorum yapın.</p>
      </v-col>
      
      <!-- Görev Ekle Butonu -->
      <v-col cols="12" sm="6" class="text-sm-right">
        <v-btn
          color="indigo-darken-2"
          prepend-icon="mdi-plus"
          size="large"
          elevation="2"
          @click="openAddDialog"
        >
          Yeni Görev Ekle
        </v-btn>
      </v-col>
    </v-row>

    <!-- KANBAN PANOSU -->
    <v-row class="px-2">
      <!-- TODO KOLONU -->
      <v-col cols="12" md="4">
        <v-card class="bg-grey-lighten-3 pa-3 column-card" elevation="0">
          <div class="d-flex justify-space-between align-center mb-4 px-2">
            <span class="font-weight-bold text-uppercase text-grey-darken-2 tracking-wider">
              TODO (Yapılacaklar)
            </span>
            <v-chip color="grey-darken-2" size="small" variant="flat" class="font-weight-bold">
              {{ todoTasks.length }}
            </v-chip>
          </div>
          
          <v-divider class="mb-3 border-opacity-25"></v-divider>

          <v-scroll-y-transition group>
            <v-card
              v-for="task in todoTasks"
              :key="task.id"
              class="mb-3 task-card cursor-pointer"
              elevation="1"
              @click="selectTask(task)"
            >
              <v-card-text class="pa-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-caption font-weight-bold text-indigo-darken-1">TASK-{{ task.id }}</span>
                  <v-chip color="grey" size="x-small" variant="tonal" class="font-weight-bold text-uppercase">
                    TODO
                  </v-chip>
                </div>
                <h3 class="text-subtitle-1 font-weight-bold mb-2 text-indigo-darken-4">{{ task.title }}</h3>
                <p class="text-body-2 text-grey-darken-1 text-truncate mb-3">{{ task.definition }}</p>
                
                <div class="d-flex align-center justify-space-between mt-2 pt-2 border-top">
                  <span class="text-caption text-grey-darken-1">
                    Atanan: <strong>{{ task.assignee_username || getAssigneeName(task.assignee) }}</strong>
                  </span>
                  <v-avatar color="indigo-lighten-4" size="24" class="text-caption font-weight-bold">
                    {{ (task.assignee_username || getAssigneeName(task.assignee)).substring(0,2).toUpperCase() }}
                  </v-avatar>
                </div>
              </v-card-text>
            </v-card>
          </v-scroll-y-transition>
        </v-card>
      </v-col>

      <!-- IN PROGRESS KOLONU -->
      <v-col cols="12" md="4">
        <v-card class="bg-blue-lighten-5 pa-3 column-card" elevation="0">
          <div class="d-flex justify-space-between align-center mb-4 px-2">
            <span class="font-weight-bold text-uppercase text-blue-darken-3 tracking-wider">
              IN PROGRESS (İşlemde)
            </span>
            <v-chip color="blue" size="small" variant="flat" class="font-weight-bold">
              {{ inProgressTasks.length }}
            </v-chip>
          </div>
          
          <v-divider class="mb-3 border-opacity-25"></v-divider>

          <v-scroll-y-transition group>
            <v-card
              v-for="task in inProgressTasks"
              :key="task.id"
              class="mb-3 task-card cursor-pointer border-blue-left"
              elevation="1"
              @click="selectTask(task)"
            >
              <v-card-text class="pa-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-caption font-weight-bold text-blue-darken-3">TASK-{{ task.id }}</span>
                  <v-chip color="blue" size="x-small" variant="tonal" class="font-weight-bold text-uppercase">
                    PROGRESS
                  </v-chip>
                </div>
                <h3 class="text-subtitle-1 font-weight-bold mb-2 text-indigo-darken-4">{{ task.title }}</h3>
                <p class="text-body-2 text-grey-darken-1 text-truncate mb-3">{{ task.definition }}</p>
                
                <div class="d-flex align-center justify-space-between mt-2 pt-2 border-top">
                  <span class="text-caption text-grey-darken-1">
                    Atanan: <strong>{{ task.assignee_username || getAssigneeName(task.assignee) }}</strong>
                  </span>
                  <v-avatar color="blue-lighten-4" size="24" class="text-caption font-weight-bold text-blue-darken-4">
                    {{ (task.assignee_username || getAssigneeName(task.assignee)).substring(0,2).toUpperCase() }}
                  </v-avatar>
                </div>
              </v-card-text>
            </v-card>
          </v-scroll-y-transition>
        </v-card>
      </v-col>

      <!-- DONE KOLONU -->
      <v-col cols="12" md="4">
        <v-card class="bg-green-lighten-5 pa-3 column-card" elevation="0">
          <div class="d-flex justify-space-between align-center mb-4 px-2">
            <span class="font-weight-bold text-uppercase text-green-darken-3 tracking-wider">
              DONE (Tamamlandı)
            </span>
            <v-chip color="green" size="small" variant="flat" class="font-weight-bold">
              {{ doneTasks.length }}
            </v-chip>
          </div>
          
          <v-divider class="mb-3 border-opacity-25"></v-divider>

          <v-scroll-y-transition group>
            <v-card
              v-for="task in doneTasks"
              :key="task.id"
              class="mb-3 task-card cursor-pointer border-green-left"
              elevation="1"
              @click="selectTask(task)"
            >
              <v-card-text class="pa-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-caption font-weight-bold text-green-darken-3">TASK-{{ task.id }}</span>
                  <v-chip color="green" size="x-small" variant="tonal" class="font-weight-bold text-uppercase">
                    DONE
                  </v-chip>
                </div>
                <h3 class="text-subtitle-1 font-weight-bold mb-2 text-indigo-darken-4">{{ task.title }}</h3>
                <p class="text-body-2 text-grey-darken-1 text-truncate mb-3">{{ task.definition }}</p>
                
                <div class="d-flex align-center justify-space-between mt-2 pt-2 border-top">
                  <span class="text-caption text-grey-darken-1 text-decoration-line-through">
                    Atanan: <strong>{{ task.assignee_username || getAssigneeName(task.assignee) }}</strong>
                  </span>
                  <v-avatar color="green-lighten-4" size="24" class="text-caption font-weight-bold text-green-darken-4">
                    {{ (task.assignee_username || getAssigneeName(task.assignee)).substring(0,2).toUpperCase() }}
                  </v-avatar>
                </div>
              </v-card-text>
            </v-card>
          </v-scroll-y-transition>
        </v-card>
      </v-col>
    </v-row>

    <!-- DETAY YAN PANELİ (RIGHT DRAWER) -->
    <v-navigation-drawer
      v-model="drawer"
      location="right"
      temporary
      width="600"
      class="task-detail-drawer"
    >
      <v-container v-if="selectedTask" class="py-6 px-6">
        <!-- Başlık -->
        <div class="d-flex justify-space-between align-center mb-4">
          <span class="text-h6 font-weight-bold text-indigo-darken-3">TASK-{{ selectedTask.id }}</span>
          <div class="d-flex gap-2">
            <!-- Düzenleme Butonu -->
            <v-btn
              icon="mdi-pencil"
              variant="text"
              color="indigo"
              size="small"
              @click="toggleEditTask"
              :title="isEditingTask ? 'Değişiklikleri İptal Et' : 'Görevi Düzenle'"
            ></v-btn>
            <!-- Silme Butonu -->
            <v-btn
              icon="mdi-delete"
              variant="text"
              color="red"
              size="small"
              @click="confirmDeleteTask"
              title="Görevi Sil"
            ></v-btn>
            <v-btn icon="mdi-close" variant="text" size="small" @click="drawer = false"></v-btn>
          </div>
        </div>

        <v-divider class="mb-4"></v-divider>

        <!-- BAŞLIK & AÇIKLAMA GÖSTERİM VEYA EDİTLEME -->
        <v-form v-if="isEditingTask" ref="editTaskFormRef" class="mb-4">
          <v-text-field
            v-model="editTaskForm.title"
            label="Görev Başlığı"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          ></v-text-field>
          <v-textarea
            v-model="editTaskForm.definition"
            label="Açıklama"
            variant="outlined"
            density="comfortable"
            rows="3"
            class="mb-2"
          ></v-textarea>
          <v-btn color="indigo" variant="flat" size="small" class="mr-2" @click="saveTaskDetails">Detayları Kaydet</v-btn>
          <v-btn color="grey" variant="text" size="small" @click="isEditingTask = false">İptal</v-btn>
        </v-form>

        <div v-else class="mb-6">
          <h2 class="text-h5 font-weight-bold mb-3 text-indigo-darken-4">{{ selectedTask.title }}</h2>
          <div class="bg-grey-lighten-4 pa-4 rounded-lg">
            <h4 class="text-caption font-weight-bold text-grey-darken-2 mb-1">Açıklama</h4>
            <p class="text-body-1 whitespace-pre-wrap">{{ selectedTask.definition }}</p>
          </div>
        </div>

        <!-- PARAMETRELER (METADATA) -->
        <v-row class="mb-6">
          <!-- Durum (State) Seçimi -->
          <v-col cols="12" sm="6">
            <v-select
              v-model="selectedTask.state"
              :items="stateItems"
              label="Durum (State)"
              variant="outlined"
              density="comfortable"
              @update:model-value="changeTaskState"
            ></v-select>
          </v-col>

          <!-- Atanan Kişi (Assignee) -->
          <v-col cols="12" sm="6">
            <v-select
              v-model="selectedTask.assignee"
              :items="usersList"
              item-title="username"
              item-value="id"
              label="Atanan Kişi"
              variant="outlined"
              density="comfortable"
              :disabled="!isStaff"
              @update:model-value="changeTaskAssignee"
            ></v-select>
          </v-col>

          <!-- Oluşturan ve Tarih Bilgisi -->
          <v-col cols="12">
            <div class="d-flex justify-space-between bg-indigo-lighten-5 pa-3 rounded-lg text-caption text-indigo-darken-4">
              <span>Oluşturan: <strong>{{ selectedTask.creator_username || getAssigneeName(selectedTask.creator) }}</strong></span>
              <span>Tarih: <strong>{{ formatDate(selectedTask.create_date) }}</strong></span>
            </div>
          </v-col>
        </v-row>

        <v-divider class="mb-4"></v-divider>

        <!-- YORUMLAR BÖLÜMÜ -->
        <div class="comments-section">
          <h3 class="text-subtitle-1 font-weight-bold mb-3 d-flex align-center">
            <v-icon icon="mdi-comment-multiple-outline" class="mr-2" size="small"></v-icon>
            Yorumlar ({{ selectedTask.comments ? selectedTask.comments.length : 0 }})
          </h3>

          <!-- Yorum Ekleme Input -->
          <v-form class="mb-4">
            <v-textarea
              v-model="newCommentText"
              placeholder="Yorum yazın..."
              variant="outlined"
              density="comfortable"
              rows="2"
              hide-details
              class="mb-2"
            ></v-textarea>
            <v-btn
              color="indigo"
              size="small"
              :loading="commentSaving"
              @click="addComment"
              :disabled="!newCommentText.trim()"
            >
              Yorum Ekle
            </v-btn>
          </v-form>

          <!-- Yorum Listesi -->
          <v-divider class="mb-4 border-opacity-25"></v-divider>
          
          <div v-if="selectedTask.comments && selectedTask.comments.length > 0">
            <div v-for="comment in selectedTask.comments" :key="comment.id" class="comment-item mb-4 pa-3 bg-grey-lighten-5 rounded-lg border-left-grey">
              <!-- Yorum Başlığı -->
              <div class="d-flex justify-space-between align-center mb-1">
                <span class="text-caption font-weight-bold text-indigo-darken-2">{{ comment.user }}</span>
                <span class="text-xsmall text-grey-darken-1">{{ formatDate(comment.create_date) }}</span>
              </div>

              <!-- Yorum İçeriği Düzenleme Modu -->
              <div v-if="editingCommentId === comment.id">
                <v-textarea
                  v-model="editCommentText"
                  variant="outlined"
                  density="comfortable"
                  rows="2"
                  hide-details
                  class="mb-2"
                ></v-textarea>
                <v-btn color="indigo" size="x-small" class="mr-1" @click="saveComment(comment)">Kaydet</v-btn>
                <v-btn color="grey" size="x-small" variant="text" @click="editingCommentId = null">İptal</v-btn>
              </div>
              
              <!-- Yorum İçeriği Gösterim Modu -->
              <div v-else>
                <p class="text-body-2 whitespace-pre-wrap text-grey-darken-3">{{ comment.description }}</p>
                <!-- İşlem Butonları (Yalnızca yorum sahibi ya da admin düzenleyebilir/silebilir) -->
                <div v-if="canManageComment(comment)" class="d-flex justify-end gap-1 mt-1">
                  <v-btn
                    icon="mdi-pencil"
                    variant="text"
                    size="x-small"
                    color="grey-darken-1"
                    @click="startEditComment(comment)"
                  ></v-btn>
                  <v-btn
                    icon="mdi-delete"
                    variant="text"
                    size="x-small"
                    color="red-darken-1"
                    @click="confirmDeleteComment(comment)"
                  ></v-btn>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-caption text-grey-darken-1 text-center py-4">Henüz yorum yapılmamış. İlk yorumu siz yazın!</div>
        </div>
      </v-container>
    </v-navigation-drawer>

    <!-- GÖREV EKLEME DİYALOGU (POP-UP) -->
    <v-dialog v-model="addDialog" max-width="600px" persistent>
      <v-card class="pa-4">
        <v-card-title class="text-h5 font-weight-bold text-indigo-darken-3">
          <v-icon icon="mdi-plus-circle" class="mr-2" color="indigo"></v-icon>
          Yeni Görev Ekle
        </v-card-title>
        
        <v-card-text class="pt-2">
          <v-form ref="addFormRef">
            <v-text-field
              v-model="addForm.title"
              label="Görev Başlığı *"
              variant="outlined"
              density="comfortable"
              :error-messages="addErrors.title"
              required
              class="mb-2"
            ></v-text-field>

            <v-textarea
              v-model="addForm.definition"
              label="Açıklama *"
              variant="outlined"
              density="comfortable"
              rows="4"
              :error-messages="addErrors.definition"
              required
              class="mb-2"
            ></v-textarea>

            <v-row>
              <!-- Durum (State) Seçimi -->
              <v-col cols="12" sm="6">
                <v-select
                  v-model="addForm.state"
                  :items="stateItems"
                  label="Durum (State)"
                  variant="outlined"
                  density="comfortable"
                ></v-select>
              </v-col>

              <!-- Atanan Kişi (Only editable for admin, pre-selected for regular user) -->
              <v-col cols="12" sm="6">
                <v-select
                  v-model="addForm.assignee"
                  :items="usersList"
                  item-title="username"
                  item-value="id"
                  label="Atanan Kişi *"
                  variant="outlined"
                  density="comfortable"
                  :disabled="!isStaff"
                  :error-messages="addErrors.assignee"
                ></v-select>
              </v-col>
            </v-row>
            <p class="text-caption text-grey-darken-1 mt-1">* işaretli alanlar zorunludur.</p>
          </v-form>
        </v-card-text>

        <v-card-actions class="px-6 py-4">
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="addDialog = false">İptal</v-btn>
          <v-btn color="indigo-darken-2" variant="flat" :loading="addSaving" @click="saveNewTask">Oluştur</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- GÖREV SİLME ONAY DİYALOGU -->
    <v-dialog v-model="deleteTaskDialog" max-width="400px">
      <v-card class="pa-2">
        <v-card-title class="text-h6 font-weight-bold text-red-darken-3">
          <v-icon icon="mdi-alert-circle" class="mr-2" color="red"></v-icon>
          Görevi Sil
        </v-card-title>
        <v-card-text class="pt-2">
          <strong>TASK-{{ selectedTask?.id }}</strong> numaralı görevi silmek istediğinize emin misiniz? Bu işlem geri alınamaz.
        </v-card-text>
        <v-card-actions class="px-4 py-3">
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="deleteTaskDialog = false">Vazgeç</v-btn>
          <v-btn color="red-darken-1" variant="flat" :loading="taskDeleting" @click="deleteTask">Evet, Sil</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- YORUM SİLME ONAY DİYALOGU -->
    <v-dialog v-model="deleteCommentDialog" max-width="400px">
      <v-card class="pa-2">
        <v-card-title class="text-h6 font-weight-bold text-red-darken-3">
          <v-icon icon="mdi-alert-circle" class="mr-2" color="red"></v-icon>
          Yorumu Sil
        </v-card-title>
        <v-card-text class="pt-2">
          Bu yorumu silmek istediğinize emin misiniz?
        </v-card-text>
        <v-card-actions class="px-4 py-3">
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="deleteCommentDialog = false">İptal</v-btn>
          <v-btn color="red-darken-1" variant="flat" :loading="commentDeleting" @click="deleteComment">Evet, Sil</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const tasks = ref([])
const usersList = ref([])
const loading = ref(false)

const drawer = ref(false)
const selectedTask = ref(null)

// Giriş yapan kullanıcının verileri
const currentUserId = ref(null)
const currentUsername = ref(localStorage.getItem('username') || '')
const isStaff = ref(localStorage.getItem('is_staff') === 'true')

// Görev Ekleme Kontrolleri
const addDialog = ref(false)
const addSaving = ref(false)
const addErrors = ref({})
const addForm = ref({
  title: '',
  definition: '',
  state: 'to do',
  assignee: null,
})

// Görev Silme Kontrolleri
const deleteTaskDialog = ref(false)
const taskDeleting = ref(false)

// Görev Düzenleme Kontrolleri (Drawer içi)
const isEditingTask = ref(false)
const editTaskForm = ref({
  title: '',
  definition: '',
})

// Yorum Kontrolleri
const newCommentText = ref('')
const commentSaving = ref(false)
const editingCommentId = ref(null)
const editCommentText = ref('')
const deleteCommentDialog = ref(false)
const commentToDelete = ref(null)
const commentDeleting = ref(false)

// Durum (State) Seçenekleri
const stateItems = [
  { value: 'to do', title: 'TODO' },
  { value: 'in progress', title: 'IN PROGRESS' },
  { value: 'done', title: 'DONE' },
]

// Sütun gruplarını hesapla
const todoTasks = computed(() => tasks.value.filter(t => t.state === 'to do'))
const inProgressTasks = computed(() => tasks.value.filter(t => t.state === 'in progress'))
const doneTasks = computed(() => tasks.value.filter(t => t.state === 'done'))

// Görevleri Yükle
const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await api.get('tasks/')
    tasks.value = response.value || response.data
  } catch (error) {
    console.error("Görevler yüklenirken hata oluştu:", error)
  } finally {
    loading.value = false
  }
}

// Kullanıcıları Yükle (Adminlerin atama yapabilmesi veya isimlerin çözülmesi için)
const fetchUsers = async () => {
  try {
    const response = await api.get('users/')
    usersList.value = response.value || response.data
    
    // Aktif kullanıcının ID'sini kullanıcı adına göre bul
    const me = usersList.value.find(u => u.username === currentUsername.value)
    if (me) {
      currentUserId.value = me.id
    }
  } catch (error) {
    console.error("Kullanıcılar yüklenirken hata oluştu:", error)
  }
}

// ID'ye göre kullanıcı adı çöz
const getAssigneeName = (id) => {
  const user = usersList.value.find(u => u.id === id)
  return user ? user.username : `ID: ${id}`
}

// Tarih Formatla
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('tr-TR')
}

// Bir kart tıklandığında görevi seç ve drawer'ı aç
const selectTask = (task) => {
  selectedTask.value = task
  isEditingTask.value = false
  newCommentText.value = ''
  drawer.value = true
}

// Görev Ekleme Pop-up'ını Aç
const openAddDialog = () => {
  addErrors.value = {}
  addForm.value = {
    title: '',
    definition: '',
    state: 'to do',
    assignee: isStaff.value ? null : currentUserId.value,
  }
  addDialog.value = true
}

// Yeni Görev Kaydet
const saveNewTask = async () => {
  addErrors.value = {}
  let hasClientError = false

  if (!addForm.value.title || addForm.value.title.trim() === '') {
    addErrors.value.title = ['Bu alan zorunludur.']
    hasClientError = true
  }
  if (!addForm.value.definition || addForm.value.definition.trim() === '') {
    addErrors.value.definition = ['Bu alan zorunludur.']
    hasClientError = true
  }
  if (!addForm.value.assignee) {
    addErrors.value.assignee = ['Lütfen bir çalışan seçin.']
    hasClientError = true
  }

  if (hasClientError) return

  addSaving.value = true
  try {
    await api.post('tasks/', addForm.value)
    addDialog.value = false
    fetchTasks()
  } catch (error) {
    console.error("Görev kaydedilirken hata oluştu:", error)
    if (error.response && error.response.status === 400) {
      addErrors.value = error.response.data
    } else {
      alert("Görev oluşturulurken bilinmeyen bir hata oluştu.")
    }
  } finally {
    addSaving.value = false
  }
}

// Görevin Durumunu (State) Güncelle
const changeTaskState = async (newState) => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    const response = await api.patch(`tasks/${id}/`, { state: newState })
    
    // Yerel veriyi güncelle
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].state = newState
    }
    console.log("Görev durumu güncellendi:", response.data)
  } catch (error) {
    console.error("Görev durumu güncellenemedi:", error)
    alert("Durum güncellenirken hata oluştu.")
  }
}

// Görevin Atanan Kişisini Güncelle (Sadece admin yapabilir)
const changeTaskAssignee = async (newAssigneeId) => {
  if (!selectedTask.value || !isStaff.value) return
  try {
    const id = selectedTask.value.id
    const response = await api.patch(`tasks/${id}/`, { assignee: newAssigneeId })
    
    // Yerel veriyi güncelle
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].assignee = newAssigneeId
      tasks.value[index].assignee_username = getAssigneeName(newAssigneeId)
    }
    console.log("Atanan kişi güncellendi:", response.data)
  } catch (error) {
    console.error("Atanan kişi güncellenemedi:", error)
    alert("Atanan kişi güncellenirken hata oluştu.")
  }
}

// Görevin Başlık & Açıklama Güncelleme Panelini Aç/Kapat
const toggleEditTask = () => {
  if (isEditingTask.value) {
    isEditingTask.value = false
  } else {
    editTaskForm.value = {
      title: selectedTask.value.title,
      definition: selectedTask.value.definition,
    }
    isEditingTask.value = true
  }
}

// Görev Başlık ve Açıklamasını Kaydet
const saveTaskDetails = async () => {
  if (!selectedTask.value) return
  if (!editTaskForm.value.title.trim() || !editTaskForm.value.definition.trim()) {
    alert("Başlık ve açıklama boş bırakılamaz.")
    return
  }

  try {
    const id = selectedTask.value.id
    const response = await api.patch(`tasks/${id}/`, {
      title: editTaskForm.value.title,
      definition: editTaskForm.value.definition,
    })

    // Yereldeki ve seçili görevdeki verileri güncelle
    selectedTask.value.title = response.data.title
    selectedTask.value.definition = response.data.definition
    
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].title = response.data.title
      tasks.value[index].definition = response.data.definition
    }

    isEditingTask.value = false
  } catch (error) {
    console.error("Görev detayları güncellenemedi:", error)
    alert("Görev detayları kaydedilemedi.")
  }
}

// Görevi Silme Onayı
const confirmDeleteTask = () => {
  deleteTaskDialog.value = true
}

// Görevi Sil
const deleteTask = async () => {
  if (!selectedTask.value) return
  taskDeleting.value = true
  try {
    const id = selectedTask.value.id
    await api.delete(`tasks/${id}/`)
    deleteTaskDialog.value = false
    drawer.value = false
    fetchTasks()
  } catch (error) {
    console.error("Görev silinirken hata oluştu:", error)
    alert("Görev silinemedi.")
  } finally {
    taskDeleting.value = false
  }
}

// Görevin Detaylarını Yenile (Yorumlar eklendiğinde/silindiğinde kullanmak için)
const refreshTaskDetails = async () => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    const response = await api.get(`tasks/${id}/`)
    selectedTask.value.comments = response.data.comments
  } catch (error) {
    console.error("Görev detayları yenilenirken hata oluştu:", error)
  }
}

// Yorum Ekle
const addComment = async () => {
  if (!selectedTask.value || !newCommentText.value.trim()) return
  commentSaving.value = true
  try {
    await api.post('comments/', {
      task: selectedTask.value.id,
      description: newCommentText.value.trim()
    })
    newCommentText.value = ''
    // Detayları yenileyerek yeni yorumu listeye ekle
    await refreshTaskDetails()
  } catch (error) {
    console.error("Yorum eklenirken hata oluştu:", error)
    alert("Yorum eklenemedi.")
  } finally {
    commentSaving.value = false
  }
}

// Yorum Yetki Kontrolü (Sahibi veya Admin silebilir/düzenleyebilir)
const canManageComment = (comment) => {
  return isStaff.value || comment.user === currentUsername.value
}

// Yorum Düzenleme Modunu Başlat
const startEditComment = (comment) => {
  editingCommentId.value = comment.id
  editCommentText.value = comment.description
}

// Yorum Düzenlemeyi Kaydet
const saveComment = async (comment) => {
  if (!editCommentText.value.trim()) return
  try {
    await api.put(`comments/${comment.id}/`, {
      task: selectedTask.value.id,
      description: editCommentText.value.trim()
    })
    editingCommentId.value = null
    await refreshTaskDetails()
  } catch (error) {
    console.error("Yorum güncellenirken hata oluştu:", error)
    alert("Yorum kaydedilemedi.")
  }
}

// Yorum Silme Onayı
const confirmDeleteComment = (comment) => {
  commentToDelete.value = comment
  deleteCommentDialog.value = true
}

// Yorum Sil
const deleteComment = async () => {
  if (!commentToDelete.value) return
  commentDeleting.value = true
  try {
    await api.delete(`comments/${commentToDelete.value.id}/`)
    deleteCommentDialog.value = false
    await refreshTaskDetails()
  } catch (error) {
    console.error("Yorum silinirken hata oluştu:", error)
    alert("Yorum silinemedi.")
  } finally {
    commentDeleting.value = false
    commentToDelete.value = null
  }
}

onMounted(() => {
  fetchUsers()
  fetchTasks()
})
</script>

<style scoped>
.column-card {
  min-height: 70vh;
  border-radius: 8px;
  max-height: 80vh;
  overflow-y: auto;
}
.task-card {
  transition: all 0.2s ease-in-out;
  border-left: 4px solid #9e9e9e;
}
.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}
.border-blue-left {
  border-left: 4px solid #2196f3 !important;
}
.border-green-left {
  border-left: 4px solid #4caf50 !important;
}
.border-top {
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}
.cursor-pointer {
  cursor: pointer;
}
.gap-1 {
  gap: 4px;
}
.gap-2 {
  gap: 8px;
}
.whitespace-pre-wrap {
  white-space: pre-wrap;
}
.text-xsmall {
  font-size: 0.75rem;
}
.border-left-grey {
  border-left: 3px solid #e0e0e0;
}
.italic {
  font-style: italic;
}
</style>

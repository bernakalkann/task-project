<!-- eslint-disable vue/valid-v-slot -->
<template>
  <v-container class="py-6 px-6" fluid>
    <!-- JIRA STYLE UST KONTROLLER (BREADCRUMBS, TITLE, SUB-NAV, FILTERS) -->
    
    <!-- Breadcrumbs -->
    <div class="text-caption text-grey-darken-1 mb-1 px-2" style="font-family: sans-serif;">
      Spaces / MSSP
    </div>

    <!-- Proje Başlığı ve Aksiyonlar -->
    <v-row class="mb-4 mx-2 align-center">
      <v-col cols="12" sm="6" class="d-flex align-center">
        <h1 class="text-h4 font-weight-bold text-grey-darken-4 mr-3" style="font-family: sans-serif;">
          MSP board
        </h1>
        <v-btn icon variant="text" size="small" color="grey-darken-1" class="rounded-lg mr-2" title="Takım Rolleri"><v-icon>mdi-account-group-outline</v-icon></v-btn>
        <v-btn icon variant="text" size="small" color="grey-darken-1" class="rounded-lg" title="Yıldızla"><v-icon>mdi-star-outline</v-icon></v-btn>
      </v-col>
      
      <!-- Aksiyon Butonları -->
      <v-col cols="12" sm="6" class="text-sm-right d-flex justify-sm-end gap-2 align-center">
        <v-btn icon variant="text" size="small" color="grey-darken-2" title="Paylaş"><v-icon>mdi-share-variant-outline</v-icon></v-btn>
        <v-btn icon variant="text" size="small" color="grey-darken-2" title="Genişlet"><v-icon>mdi-fullscreen</v-icon></v-btn>

        <v-btn
          color="success"
          prepend-icon="mdi-microsoft-excel"
          variant="outlined"
          size="small"
          class="text-capitalize font-weight-bold ml-2"
          :loading="exporting"
          @click="exportTasks"
        >
          Excel Dışa Aktar
        </v-btn>
        <v-btn
          color="blue-darken-2"
          prepend-icon="mdi-plus"
          variant="flat"
          size="small"
          class="text-capitalize font-weight-bold"
          @click="openAddDialog"
        >
          Yeni Görev Ekle
        </v-btn>
      </v-col>
    </v-row>

    <!-- Sub-navigation Tabs -->
    <div class="mx-2 mb-4 d-flex align-center border-bottom pb-1 overflow-x-auto" style="gap: 20px; font-family: sans-serif; cursor: pointer;">
      <span 
        v-for="tab in ['Testing Board', 'Active sprints', 'Backlog', 'Releases', 'Summary', 'Timeline', 'Calendar', 'Reports', 'List', 'Issues']"
        :key="tab"
        :class="['tab-item text-body-2 pb-2 transition-all', activeTab === tab ? 'active-tab font-weight-bold text-blue-darken-2 border-bottom-blue' : 'font-weight-medium text-grey-darken-1']"
        @click="activeTab = tab"
      >
        {{ tab }}
      </span>
    </div>

    <!-- Filtre Araç Çubuğu (Jira Tarzı Tek Sıra ve Kaydırılabilir) -->
    <div class="mx-2 mb-6 d-flex align-center overflow-x-auto pb-2 flex-nowrap" style="gap: 12px; scrollbar-width: none; -ms-overflow-style: none;">
      <!-- Arama Kutusu -->
      <div style="width: 180px; min-width: 180px;" class="flex-shrink-0">
        <v-text-field
          v-model="searchQuery"
          placeholder="Panoda ara..."
          variant="outlined"
          density="compact"
          hide-details
          prepend-inner-icon="mdi-magnify"
        ></v-text-field>
      </div>

      <!-- Atanan Kullanıcılar Avatar Listesi -->
      <div class="d-flex align-center mr-2 flex-shrink-0">
        <v-avatar 
          v-for="user in usersList.slice(0, 5)" 
          :key="user.id" 
          :color="selectedFilterUserId === user.id ? 'blue-darken-2' : 'indigo-lighten-4'" 
          :class="['cursor-pointer hover-avatar mr-n2 elevation-1', {'active-avatar-filter': selectedFilterUserId === user.id}]" 
          size="30"
          @click="toggleUserFilter(user.id)"
          :title="`${user.username} filtrele`"
        >
          <v-img v-if="user.avatar" :src="user.avatar"></v-img>
          <span v-else class="text-caption font-weight-bold">{{ user.username.substring(0,2).toUpperCase() }}</span>
        </v-avatar>
        
        <v-avatar 
          v-if="selectedFilterUserId !== null" 
          color="red-lighten-4" 
          class="cursor-pointer ml-3" 
          size="26"
          @click="clearUserFilter"
          title="Filtreyi Temizle"
        >
          <v-icon size="16" color="red">mdi-close</v-icon>
        </v-avatar>
      </div>

      <!-- Sürüm Filtresi (Interactive) -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="outlined"
            :color="selectedVersionFilter ? 'blue-darken-2' : 'grey-lighten-1'"
            size="small"
            class="text-capitalize text-grey-darken-3 font-weight-medium mr-1 flex-shrink-0"
            v-bind="props"
          >
            Sürüm: {{ selectedVersionFilter || 'Tümü' }}
            <v-icon size="14" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list density="compact">
          <v-list-item title="Tümü" @click="selectedVersionFilter = ''"></v-list-item>
          <v-list-item v-for="v in ['v1.0', 'v1.1', 'v2.0']" :key="v" :title="v" @click="selectedVersionFilter = v"></v-list-item>
        </v-list>
      </v-menu>

      <!-- Epic Filtresi (Interactive) -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="outlined"
            :color="selectedEpicFilter ? 'blue-darken-2' : 'grey-lighten-1'"
            size="small"
            class="text-capitalize text-grey-darken-3 font-weight-medium mr-1 flex-shrink-0"
            v-bind="props"
          >
            Epic: {{ selectedEpicFilter || 'Tümü' }}
            <v-icon size="14" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list density="compact">
          <v-list-item title="Tümü" @click="selectedEpicFilter = ''"></v-list-item>
          <v-list-item v-for="e in ['Kullanıcı Yönetimi', 'Kanban Panosu', 'Raporlama & CSV']" :key="e" :title="e" @click="selectedEpicFilter = e"></v-list-item>
        </v-list>
      </v-menu>

      <!-- Tip Filtresi (Interactive) -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="outlined"
            :color="selectedTypeFilter ? 'blue-darken-2' : 'grey-lighten-1'"
            size="small"
            class="text-capitalize text-grey-darken-3 font-weight-medium mr-1 flex-shrink-0"
            v-bind="props"
          >
            Tip: {{ getTypeLabel(selectedTypeFilter) }}
            <v-icon size="14" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list density="compact">
          <v-list-item title="Tümü" @click="selectedTypeFilter = ''"></v-list-item>
          <v-list-item v-for="t in typeOptions" :key="t.value" :title="t.title" @click="selectedTypeFilter = t.value"></v-list-item>
        </v-list>
      </v-menu>

      <!-- Öncelik Filtresi (Interactive) -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="outlined"
            :color="selectedPriorityFilter ? 'blue-darken-2' : 'grey-lighten-1'"
            size="small"
            class="text-capitalize text-grey-darken-3 font-weight-medium mr-1 flex-shrink-0"
            v-bind="props"
          >
            Öncelik: {{ getPriorityLabel(selectedPriorityFilter) }}
            <v-icon size="14" class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list density="compact">
          <v-list-item title="Tümü" @click="selectedPriorityFilter = ''"></v-list-item>
          <v-list-item v-for="p in priorityOptions" :key="p.value" :title="p.title" @click="selectedPriorityFilter = p.value"></v-list-item>
        </v-list>
      </v-menu>

      <!-- Benim Görevlerim Filtresi -->
      <v-btn
        :variant="onlyMyTasksFilter ? 'flat' : 'outlined'"
        :color="onlyMyTasksFilter ? 'blue-darken-2' : 'grey-lighten-1'"
        size="small"
        class="text-capitalize font-weight-bold flex-shrink-0"
        @click="onlyMyTasksFilter = !onlyMyTasksFilter"
      >
        Sadece Benim Görevlerim
      </v-btn>

      <v-spacer></v-spacer>

      <!-- Tasarım Görünümleri -->
      <div class="d-flex align-center gap-1 flex-shrink-0">
        <v-btn icon variant="text" size="small" color="grey-darken-2"><v-icon>mdi-chart-bar</v-icon></v-btn>
        <v-btn icon variant="text" size="small" color="grey-darken-2"><v-icon>mdi-tune-variant</v-icon></v-btn>
        <v-btn icon variant="text" size="small" color="grey-darken-2"><v-icon>mdi-dots-horizontal</v-icon></v-btn>
      </div>
    </div>

    <!-- TABS CORRESPONDING VIEWS -->
    
    <!-- 1. KANBAN PANOSU VIEW -->
    <v-row v-if="activeTab === 'Active sprints' || activeTab === 'Testing Board'" class="px-2 flex-nowrap" style="overflow-x: auto; min-height: 80vh; padding-bottom: 24px;">
      <!-- DINAMIK JIRA-STYLE KOLONLAR -->
      <v-col 
        v-for="col in columns" 
        :key="col.key" 
        cols="12" 
        sm="6" 
        md="3" 
        style="min-width: 320px;" 
        class="d-flex"
      >
        <v-card 
          :class="[currentTheme === 'dark' ? 'bg-grey-darken-4' : col.bgClass, {'drag-over-active': activeDragOverColumn === col.key}]" 
          class="pa-3 column-card w-100 d-flex flex-column" 
          elevation="0"
          @dragover.prevent="activeDragOverColumn = col.key"
          @dragleave="activeDragOverColumn = null"
          @drop="onDrop($event, col.key)"
        >
          <!-- Kolon Başlığı -->
          <div class="d-flex justify-space-between align-center mb-4 px-2">
            <span :class="`text-${col.color}`" class="font-weight-bold text-uppercase tracking-wider text-body-2">
              <v-icon :icon="col.icon" class="mr-1" size="small"></v-icon>
              {{ col.title }}
            </span>
            <v-chip :color="col.color" size="small" variant="flat" class="font-weight-bold">
              {{ getTasksByState(col.key).length }}
            </v-chip>
          </div>
          
          <v-divider class="mb-3 border-opacity-25"></v-divider>

          <!-- Kolon İçindeki Görevler Listesi (Kendi içinde kaydırılabilir) -->
          <div class="flex-grow-1 overflow-y-auto pr-1" style="max-height: 65vh;">
            <v-scroll-y-transition group>
              <v-card
                v-for="task in getTasksByState(col.key)"
                :key="task.id"
                :class="['mb-3 task-card cursor-pointer', getCardBorderClass(task.state)]"
                elevation="1"
                draggable="true"
                @dragstart="onDragStart($event, task)"
                @click="selectTask(task)"
              >
                <v-card-text class="pa-4">
                  <div class="d-flex justify-space-between align-center mb-2">
                    <div class="d-flex align-center gap-1">
                      <v-icon :icon="getTypeIcon(task.task_type)" :color="getTypeColor(task.task_type)" size="18" :title="getTypeLabel(task.task_type)"></v-icon>
                      <v-icon :icon="getPriorityIcon(task.priority)" :color="getPriorityColor(task.priority)" size="18" :title="getPriorityLabel(task.priority)"></v-icon>
                      <span class="text-caption font-weight-bold text-indigo-darken-1">TASK-{{ task.id }}</span>
                    </div>
                    <v-chip :color="col.color" size="x-small" variant="tonal" class="font-weight-bold text-uppercase">
                      {{ col.title }}
                    </v-chip>
                  </div>
                  <h3 class="text-subtitle-1 font-weight-bold mb-2 text-indigo-darken-4 text-truncate">{{ task.title }}</h3>
                  <p class="text-body-2 text-grey-darken-1 text-truncate mb-3">{{ task.definition }}</p>
                  
                  <div class="d-flex align-center justify-space-between mt-2 pt-2 border-top flex-wrap gap-2">
                    <span class="text-caption text-grey-darken-1">
                      Atanan: <strong>{{ task.assignee_username }}</strong>
                    </span>
                    <div class="d-flex align-center gap-1">
                      <v-chip v-if="task.duration" size="x-small" color="blue-grey" variant="flat" class="font-weight-bold">
                        {{ task.duration }}s
                      </v-chip>
                      <v-chip v-if="task.due_date" size="x-small" :color="isOverdue(task.due_date) && task.state !== 'done' ? 'red' : 'grey'" variant="outlined" class="font-weight-bold">
                        <v-icon size="10" class="mr-1">mdi-calendar</v-icon>
                        {{ formatShortDate(task.due_date) }}
                      </v-chip>
                      <v-avatar color="indigo-lighten-4" size="24" class="text-caption font-weight-bold">
                        <v-img v-if="task.assignee_avatar" :src="task.assignee_avatar"></v-img>
                        <span v-else>{{ (task.assignee_username || '').substring(0,2).toUpperCase() }}</span>
                      </v-avatar>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-scroll-y-transition>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 2. BACKLOG VIEW -->
    <div v-else-if="activeTab === 'Backlog'" class="mb-6">
      <v-card class="pa-4 rounded-lg border" elevation="0">
        <div class="d-flex justify-space-between align-center mb-4">
          <h3 class="text-h6 font-weight-bold text-grey-darken-3">Proje İş Listesi (Backlog)</h3>
          <v-chip color="blue" size="small" class="font-weight-bold">Toplam Görev: {{ tasks.length }}</v-chip>
        </div>
        <v-list class="pa-0 border rounded-lg">
          <v-list-item 
            v-for="task in tasks" 
            :key="task.id" 
            class="border-bottom py-3 cursor-pointer hover-backlog"
            @click="selectTask(task)"
          >
            <template v-slot:prepend>
              <v-icon :icon="getTypeIcon(task.task_type)" :color="getTypeColor(task.task_type)" class="mr-3"></v-icon>
            </template>
            <v-list-item-title class="font-weight-bold text-indigo-darken-4">
              TASK-{{ task.id }}: {{ task.title }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-grey-darken-1 text-truncate mt-1" style="max-width: 600px;">
              {{ task.definition }}
            </v-list-item-subtitle>
            <template v-slot:append>
              <div class="d-flex align-center gap-2">
                <v-chip size="x-small" :color="getPriorityColor(task.priority)" variant="tonal" class="font-weight-bold text-uppercase">
                  {{ getPriorityLabel(task.priority) }}
                </v-chip>
                <v-chip size="x-small" color="indigo" variant="flat" class="font-weight-bold text-uppercase">
                  {{ task.state.toUpperCase() }}
                </v-chip>
                <v-avatar color="indigo-lighten-4" size="26" class="text-caption font-weight-bold">
                  <v-img v-if="task.assignee_avatar" :src="task.assignee_avatar"></v-img>
                  <span v-else>{{ (task.assignee_username || 'US').substring(0,2).toUpperCase() }}</span>
                </v-avatar>
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-card>
    </div>

    <!-- 3. SUMMARY VIEW -->
    <div v-else-if="activeTab === 'Summary'" class="mb-6">
      <v-row>
        <!-- Durum Dağılım Kartları -->
        <v-col cols="12" md="6">
          <v-card class="pa-4 rounded-lg border h-100" elevation="0">
            <h3 class="text-h6 font-weight-bold text-indigo-darken-4 mb-4">Görev Durum Dağılımı</h3>
            <div class="d-flex flex-column gap-3">
              <div v-for="col in columns" :key="col.key">
                <div class="d-flex justify-space-between align-center text-body-2 font-weight-bold text-grey-darken-3 mb-1">
                  <span>{{ col.title }}</span>
                  <span>{{ tasks.filter(t => t.state === col.key).length }} Görev</span>
                </div>
                <v-progress-linear 
                  :model-value="(tasks.filter(t => t.state === col.key).length / (tasks.length || 1)) * 100"
                  :color="col.color"
                  height="8"
                  rounded
                ></v-progress-linear>
              </div>
            </div>
          </v-card>
        </v-col>
        <!-- Proje Bilgileri -->
        <v-col cols="12" md="6">
          <v-card class="pa-4 rounded-lg border h-100" elevation="0">
            <h3 class="text-h6 font-weight-bold text-indigo-darken-4 mb-4">Proje Genel Metrikleri</h3>
            <v-row>
              <v-col cols="6">
                <div class="bg-indigo-lighten-5 pa-4 rounded-lg text-center">
                  <div class="text-h4 font-weight-bold text-indigo-darken-4">{{ tasks.filter(t => t.state === 'done').length }}</div>
                  <div class="text-caption font-weight-bold text-grey-darken-2 mt-1">Tamamlanan</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="bg-red-lighten-5 pa-4 rounded-lg text-center">
                  <div class="text-h4 font-weight-bold text-red-darken-4">{{ tasks.filter(t => t.state.includes('blocked')).length }}</div>
                  <div class="text-caption font-weight-bold text-grey-darken-2 mt-1">Engellenen (Blocked)</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="bg-orange-lighten-5 pa-4 rounded-lg text-center">
                  <div class="text-h4 font-weight-bold text-orange-darken-4">{{ tasks.filter(t => t.state.includes('test')).length }}</div>
                  <div class="text-caption font-weight-bold text-grey-darken-2 mt-1">Test Aşamasında</div>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="bg-grey-lighten-4 pa-4 rounded-lg text-center">
                  <div class="text-h4 font-weight-bold text-grey-darken-4">{{ tasks.length }}</div>
                  <div class="text-caption font-weight-bold text-grey-darken-2 mt-1">Toplam Görev</div>
                </div>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- 4. LIST VIEW -->
    <div v-else-if="activeTab === 'List'" class="mb-6">
      <v-card class="pa-4 rounded-lg border" elevation="0">
        <v-table class="w-100">
          <thead>
            <tr>
              <th class="text-left font-weight-bold text-grey-darken-2">Anahtar (Key)</th>
              <th class="text-left font-weight-bold text-grey-darken-2">Başlık</th>
              <th class="text-left font-weight-bold text-grey-darken-2">Görev Tipi</th>
              <th class="text-left font-weight-bold text-grey-darken-2">Öncelik</th>
              <th class="text-left font-weight-bold text-grey-darken-2">Durum</th>
              <th class="text-left font-weight-bold text-grey-darken-2">Atanan Kişi</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="task in tasks" 
              :key="task.id" 
              class="cursor-pointer hover-table-row" 
              @click="selectTask(task)"
            >
              <td class="font-weight-bold text-indigo">TASK-{{ task.id }}</td>
              <td class="font-weight-bold text-indigo-darken-4">{{ task.title }}</td>
              <td>
                <div class="d-flex align-center gap-1">
                   <v-icon :icon="getTypeIcon(task.task_type)" :color="getTypeColor(task.task_type)" size="16"></v-icon>
                   <span class="text-caption font-weight-medium">{{ getTypeLabel(task.task_type) }}</span>
                </div>
              </td>
              <td>
                <div class="d-flex align-center gap-1">
                   <v-icon :icon="getPriorityIcon(task.priority)" :color="getPriorityColor(task.priority)" size="16"></v-icon>
                   <span class="text-caption font-weight-medium">{{ getPriorityLabel(task.priority) }}</span>
                </div>
              </td>
              <td>
                <v-chip size="x-small" color="blue" variant="flat" class="font-weight-bold">{{ task.state.toUpperCase() }}</v-chip>
              </td>
              <td>
                <div class="d-flex align-center gap-2">
                  <v-avatar color="indigo-lighten-4" size="24" class="text-caption font-weight-bold flex-shrink-0">
                    <v-img v-if="task.assignee_avatar" :src="task.assignee_avatar"></v-img>
                    <span v-else>{{ (task.assignee_username || '').substring(0,2).toUpperCase() }}</span>
                  </v-avatar>
                  <span class="font-weight-bold text-grey-darken-2">{{ task.assignee_username }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card>
    </div>

    <!-- 5. OTHERS PLACEHOLDER -->
    <div v-else class="mb-6">
      <v-card class="pa-10 text-center rounded-lg border" elevation="0">
        <v-icon size="64" color="blue-grey-lighten-2" class="mb-4">mdi-clock-outline</v-icon>
        <h3 class="text-h5 font-weight-bold text-grey-darken-3 mb-2">{{ activeTab }}</h3>
        <p class="text-body-1 text-grey">Bu görünüm çok yakında GoJira projenize dahil edilecektir.</p>
      </v-card>
    </div>

    <!-- DETAY YAN PANELİ (RIGHT DRAWER - JIRA CLOUD STYLE 2-COLUMN MODAL) -->
    <v-navigation-drawer
      v-model="drawer"
      location="right"
      temporary
      width="950"
      class="task-detail-drawer"
    >
      <v-container v-if="selectedTask" class="py-4 px-6">
        <!-- Path & Breadcrumbs Bar -->
        <div class="d-flex justify-space-between align-center mb-4 border-bottom pb-2">
          <div class="d-flex align-center gap-1 text-caption text-grey-darken-1">
            <v-icon size="14">mdi-plus</v-icon>
            <span>Add parent</span>
            <span class="mx-1">/</span>
            <v-icon size="14" color="blue">mdi-jira</v-icon>
            <span class="font-weight-bold">GoJira</span>
            <span class="mx-1">/</span>
            <v-icon size="14" color="green">mdi-checkbox-marked-circle-outline</v-icon>
            <span class="font-weight-bold text-grey-darken-3">TASK-{{ selectedTask.id }}</span>
          </div>
          <div class="d-flex align-center gap-1">
            <v-btn size="x-small" variant="flat" color="blue-lighten-5" class="text-capitalize text-blue-darken-3 font-weight-bold mr-1" prepend-icon="mdi-eye-outline">
              1 Watcher
            </v-btn>
            <v-btn icon variant="text" size="small" color="grey-darken-2"><v-icon size="18">mdi-share-variant-outline</v-icon></v-btn>
            <v-btn icon variant="text" size="small" color="grey-darken-2"><v-icon size="18">mdi-dots-horizontal</v-icon></v-btn>
            <v-btn icon variant="text" size="small" color="grey-darken-2"><v-icon size="18">mdi-fullscreen</v-icon></v-btn>
            <v-btn icon variant="text" size="small" color="grey-darken-2" @click="drawer = false"><v-icon size="18">mdi-close</v-icon></v-btn>
          </div>
        </div>

        <v-row>
          <!-- SOL KOLON (MAIN AREA) -->
          <v-col cols="12" md="7">
            <!-- Inline Görev Başlığı -->
            <div class="mb-4">
              <h2 
                v-if="!editingTitleInline" 
                class="text-h5 font-weight-bold cursor-pointer hover-bg-grey pa-1 rounded text-indigo-darken-4"
                @click="editingTitleInline = true; inlineTitleVal = selectedTask.title"
                title="Başlığı düzenlemek için tıklayın"
              >
                {{ selectedTask.title }}
              </h2>
              <div v-else class="d-flex align-center gap-2">
                <v-text-field
                  v-model="inlineTitleVal"
                  variant="outlined"
                  density="compact"
                  hide-details
                  autofocus
                  @keydown.enter="saveTitleInline"
                  @blur="saveTitleInline"
                  class="flex-grow-1"
                ></v-text-field>
              </div>
            </div>

            <!-- Description (Açıklama) -->
            <div class="mb-6">
              <div class="d-flex align-center gap-2 mb-2">
                <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3">Description</h3>
                <v-icon size="16" color="grey-darken-1">mdi-pencil-outline</v-icon>
              </div>
              <div 
                v-if="!editingDescInline" 
                class="bg-grey-lighten-4 pa-4 rounded-lg cursor-pointer hover-bg-grey-dark description-box" 
                @click="editingDescInline = true; inlineDescVal = selectedTask.definition"
                title="Açıklamayı düzenlemek için tıklayın"
              >
                <p v-if="selectedTask.definition" class="text-body-2 whitespace-pre-wrap text-grey-darken-3">{{ selectedTask.definition }}</p>
                <p v-else class="text-body-2 text-grey italic">Açıklama ekleyin...</p>
              </div>
              <div v-else>
                <v-textarea
                  v-model="inlineDescVal"
                  variant="outlined"
                  density="comfortable"
                  rows="3"
                  hide-details
                  class="mb-2"
                ></v-textarea>
                <v-btn color="indigo" size="x-small" class="mr-2" @click="saveDescInline">Kaydet</v-btn>
                <v-btn color="grey" variant="text" size="x-small" @click="editingDescInline = false">İptal</v-btn>
              </div>
            </div>

            <!-- Subtasks (Alt Görevler) -->
            <div class="mb-6">
              <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3 mb-2">Subtasks</h3>
              
              <!-- Add Subtask Button / Input -->
              <div v-if="!showAddSubtaskInput" class="d-flex align-center gap-2 text-caption text-blue-darken-2 font-weight-bold cursor-pointer hover-text-blue pb-2 border-bottom border-dashed mb-2" @click="showAddSubtaskInput = true">
                <v-icon size="16">mdi-plus</v-icon>
                <span>Add subtask</span>
              </div>
              <div v-else class="mb-3">
                <v-text-field
                  v-model="newSubtaskTitle"
                  placeholder="Alt görev başlığı girin..."
                  variant="outlined"
                  density="compact"
                  hide-details
                  autofocus
                  @keydown.enter="saveSubtask"
                  class="mb-2"
                ></v-text-field>
                <div class="d-flex gap-2">
                  <v-btn color="indigo" size="x-small" @click="saveSubtask" :loading="subtaskSaving">Kaydet</v-btn>
                  <v-btn color="grey" variant="text" size="x-small" @click="showAddSubtaskInput = false; newSubtaskTitle = ''">İptal</v-btn>
                </div>
              </div>

              <!-- Subtasks List -->
              <div v-if="selectedTask.subtasks && selectedTask.subtasks.length > 0">
                <div 
                  v-for="(subtask, idx) in selectedTask.subtasks" 
                  :key="subtask.id"
                  class="d-flex align-center gap-2 pa-2 bg-grey-lighten-4 rounded text-caption text-grey-darken-1 mb-1"
                >
                  <v-icon 
                    size="16" 
                    :color="subtask.state === 'done' ? 'green' : 'grey'"
                    @click="toggleSubtaskState(subtask)"
                    class="cursor-pointer"
                  >
                    {{ subtask.state === 'done' ? 'mdi-checkbox-marked-circle-outline' : 'mdi-checkbox-blank-circle-outline' }}
                  </v-icon>
                  <span class="text-indigo-darken-1 font-weight-bold">TASK-{{ selectedTask.id }}-{{ idx + 1 }}</span>
                  <span class="flex-grow-1 text-truncate" :style="subtask.state === 'done' ? 'text-decoration: line-through;' : ''">
                    {{ subtask.title }}
                  </span>
                  
                  <v-chip 
                    size="x-small" 
                    :color="subtask.state === 'done' ? 'green' : 'blue-darken-2'" 
                    variant="flat" 
                    class="text-uppercase font-weight-bold"
                  >
                    {{ subtask.state }}
                  </v-chip>
                  
                  <v-btn 
                    icon="mdi-delete" 
                    variant="text" 
                    size="x-small" 
                    color="red" 
                    @click="deleteSubtask(subtask.id)"
                    title="Alt görevi sil"
                  ></v-btn>
                </div>
              </div>
              <div v-else class="text-caption text-grey-darken-1 text-center py-2 bg-grey-lighten-5 rounded border border-dashed">
                Henüz alt görev eklenmemiş.
              </div>
            </div>

            <!-- Linked work items -->
            <div class="mb-6">
              <div class="d-flex justify-space-between align-center mb-2">
                <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3">Linked work items</h3>
                <v-icon size="16" class="cursor-pointer" color="grey-darken-1">mdi-plus</v-icon>
              </div>
              <span class="text-caption text-grey-darken-1 font-weight-bold d-block mb-2">relates to</span>
              <div class="d-flex align-center justify-space-between pa-2 bg-grey-lighten-4 rounded border mb-2">
                <div class="d-flex align-center gap-2 overflow-hidden">
                  <v-icon size="14" color="blue">mdi-checkbox-marked-circle-outline</v-icon>
                  <span class="text-caption text-indigo-darken-1 font-weight-bold">MSP-7979</span>
                  <span class="text-caption text-grey-darken-3 text-truncate font-weight-medium" style="max-width: 250px;">HR Özlük Verilerinin DB'den Silinmesi</span>
                </div>
                <div class="d-flex align-center gap-2">
                  <v-chip size="x-small" color="red-darken-4" variant="flat" class="font-weight-bold text-uppercase">Blocked (Test)</v-chip>
                  <v-avatar color="indigo-lighten-4" size="18">
                    <span class="text-xsmall font-weight-bold">SC</span>
                  </v-avatar>
                </div>
              </div>
            </div>

            <!-- Confluence content -->
            <div class="mb-6">
              <div class="d-flex justify-space-between align-center mb-2">
                <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3">Confluence content</h3>
                <v-icon size="16" class="cursor-pointer" color="grey-darken-1">mdi-dots-horizontal</v-icon>
              </div>
              <div class="d-flex align-center justify-space-between pa-2 bg-grey-lighten-4 rounded border">
                <div class="d-flex align-center gap-2">
                  <v-icon size="16" color="blue">mdi-page-layout-header</v-icon>
                  <span class="text-caption font-weight-bold text-blue-darken-3 cursor-pointer">Project plan</span>
                </div>
                <v-chip size="x-small" color="purple-lighten-5" text-color="purple-darken-4" class="font-weight-bold">REQUEST TO TRY</v-chip>
              </div>
            </div>

            <!-- Attachments (Dosyalar) -->
            <div class="attachments-section mb-6 border-top pt-4">
              <div class="d-flex justify-space-between align-center mb-3">
                <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3 d-flex align-center">
                  <v-icon icon="mdi-paperclip" class="mr-2" size="small"></v-icon>
                  Dosyalar ({{ selectedTask.attachments ? selectedTask.attachments.length : 0 }})
                </h3>
                <div>
                  <v-btn 
                    color="indigo" 
                    variant="outlined" 
                    size="small" 
                    prepend-icon="mdi-upload" 
                    @click="$refs.taskFileInput.click()"
                  >
                    Dosya Ekle
                  </v-btn>
                  <input 
                    ref="taskFileInput" 
                    type="file" 
                    style="display: none" 
                    @change="handleTaskFileUpload"
                  />
                </div>
              </div>
              <div v-if="selectedTask.attachments && selectedTask.attachments.length > 0" class="d-flex flex-column gap-2">
                <div 
                  v-for="file in selectedTask.attachments" 
                  :key="file.id" 
                  class="d-flex align-center justify-space-between pa-2 bg-grey-lighten-4 rounded border"
                >
                  <div class="d-flex align-center gap-2 overflow-hidden">
                    <v-icon :icon="getFileIcon(file.file_type)" color="grey-darken-1"></v-icon>
                    <span class="text-caption font-weight-medium text-truncate" style="max-width: 250px;">{{ file.name }}</span>
                  </div>
                  <div class="d-flex gap-1">
                    <v-btn icon="mdi-download" variant="text" size="x-small" color="indigo" @click="downloadAttachment(file)"></v-btn>
                    <v-btn icon="mdi-delete" variant="text" size="x-small" color="red" @click="deleteAttachment(file)"></v-btn>
                  </div>
                </div>
              </div>
              <div v-else class="text-caption text-grey-darken-1 text-center py-2 bg-grey-lighten-5 rounded border border-dashed">
                Henüz dosya eklenmemiş.
              </div>
            </div>

            <!-- Comments (Yorumlar) -->
            <div class="comments-section border-top pt-4">
              <h3 class="text-subtitle-1 font-weight-bold mb-3 text-grey-darken-3 d-flex align-center">
                <v-icon icon="mdi-comment-multiple-outline" class="mr-2" size="small"></v-icon>
                Yorumlar ({{ selectedTask.comments ? selectedTask.comments.length : 0 }})
              </h3>
              
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
                
                <div v-if="commentFile" class="d-flex align-center justify-space-between text-caption bg-indigo-lighten-5 pa-2 rounded mb-2">
                  <span class="text-truncate" style="max-width: 250px;">
                    <v-icon size="14" class="mr-1">mdi-paperclip</v-icon>
                    {{ commentFile.name }}
                  </span>
                  <v-btn icon="mdi-close" variant="text" size="x-small" color="red" @click="commentFile = null"></v-btn>
                </div>

                <div class="d-flex align-center gap-2">
                  <v-btn
                    color="indigo"
                    variant="flat"
                    size="small"
                    :loading="commentSaving"
                    @click="addComment"
                    :disabled="!newCommentText.trim() && !commentFile"
                  >
                    Yorum Yap
                  </v-btn>
                  <v-btn 
                    color="indigo" 
                    variant="outlined" 
                    size="small" 
                    icon="mdi-paperclip"
                    @click="$refs.commentFileInput.click()"
                  ></v-btn>
                  <input ref="commentFileInput" type="file" style="display: none" @change="handleCommentFileSelection" />
                </div>
              </v-form>

              <v-divider class="mb-4 border-opacity-25"></v-divider>

              <div v-if="selectedTask.comments && selectedTask.comments.length > 0">
                <div v-for="comment in selectedTask.comments" :key="comment.id" class="comment-item mb-4 pa-3 bg-grey-lighten-5 rounded-lg border-left-grey">
                  <div class="d-flex align-center justify-space-between mb-2">
                    <div class="d-flex align-center gap-2">
                      <v-avatar color="indigo-lighten-4" size="24" class="text-caption font-weight-bold flex-shrink-0">
                        <v-img v-if="comment.user_avatar" :src="comment.user_avatar"></v-img>
                        <span v-else>{{ (comment.user || 'US').substring(0,2).toUpperCase() }}</span>
                      </v-avatar>
                      <span class="text-caption font-weight-bold text-indigo-darken-2">{{ comment.user }}</span>
                    </div>
                    <span class="text-xsmall text-grey-darken-1">{{ formatDate(comment.create_date) }}</span>
                  </div>
                  <div v-if="editingCommentId === comment.id">
                    <v-textarea v-model="editCommentText" variant="outlined" density="comfortable" rows="2" hide-details class="mb-2"></v-textarea>
                    <v-btn color="indigo" size="x-small" class="mr-1" @click="saveComment(comment)">Kaydet</v-btn>
                    <v-btn color="grey" size="x-small" variant="text" @click="editingCommentId = null">İptal</v-btn>
                  </div>
                  <div v-else>
                    <p class="text-body-2 whitespace-pre-wrap text-grey-darken-3">{{ comment.description }}</p>
                    <div v-if="comment.attachments && comment.attachments.length > 0" class="mt-2 d-flex flex-wrap gap-1">
                      <v-chip 
                        v-for="file in comment.attachments" 
                        :key="file.id" 
                        size="x-small" 
                        color="indigo" 
                        variant="tonal" 
                        class="font-weight-bold"
                        @click="downloadAttachment(file)"
                      >
                        <v-icon size="12" class="mr-1">mdi-paperclip</v-icon>
                        {{ file.name }}
                      </v-chip>
                    </div>
                    <div v-if="canManageComment(comment)" class="d-flex justify-end gap-1 mt-1">
                      <v-btn icon="mdi-pencil" variant="text" size="x-small" color="grey-darken-1" @click="startEditComment(comment)"></v-btn>
                      <v-btn icon="mdi-delete" variant="text" size="x-small" color="red-darken-1" @click="confirmDeleteComment(comment)"></v-btn>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-caption text-grey-darken-1 text-center py-4">Henüz yorum yapılmamış. İlk yorumu siz yazın!</div>
            </div>
          </v-col>

          <!-- SAĞ KOLON (METADATA SIDEBAR) -->
          <v-col cols="12" md="5">
            <!-- Status Dropdown & General Actions -->
            <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
              <v-menu>
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    color="blue"
                    variant="flat"
                    size="small"
                    class="text-uppercase font-weight-bold text-white"
                    append-icon="mdi-chevron-down"
                  >
                    {{ selectedTask.state }}
                  </v-btn>
                </template>
                <v-list density="compact">
                  <v-list-item 
                    v-for="item in stateItems" 
                    :key="item.value" 
                    :title="item.title"
                    @click="selectedTask.state = item.value; changeTaskState(item.value)"
                  ></v-list-item>
                </v-list>
              </v-menu>

              <div class="d-flex align-center gap-1">
                <v-btn variant="outlined" size="small" prepend-icon="mdi-robot-outline" class="text-capitalize font-weight-bold">Agents</v-btn>
                <v-btn icon variant="text" size="small" color="grey-darken-2"><v-icon size="18">mdi-code-tags</v-icon></v-btn>
                <v-btn icon variant="text" size="small" color="grey-darken-2" @click="confirmDeleteTask" title="Sil"><v-icon size="18">mdi-delete-outline</v-icon></v-btn>
              </div>
            </div>

            <!-- Improve Task Button -->
            <v-btn block color="blue-lighten-5" variant="flat" size="small" class="text-capitalize text-blue-darken-3 font-weight-bold mb-4" prepend-icon="mdi-auto-fix">
              Improve Task
            </v-btn>

            <!-- DETAILS COLLAPSIBLE CARD -->
            <v-card variant="outlined" class="pa-4 border rounded-lg bg-grey-lighten-5">
              <div class="d-flex justify-space-between align-center mb-4">
                <span class="font-weight-bold text-subtitle-2 text-grey-darken-3">Details</span>
                <v-icon size="16">mdi-chevron-up</v-icon>
              </div>
              
              <v-divider class="mb-4"></v-divider>

              <!-- Assignee -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Assignee</label>
                <div class="d-flex align-center gap-2">
                  <v-select
                    v-if="isStaff"
                    v-model="selectedTask.assignee"
                    :items="usersList"
                    item-title="username"
                    item-value="id"
                    variant="outlined"
                    density="compact"
                    hide-details
                    @update:model-value="changeTaskAssignee"
                    class="flex-grow-1 bg-white"
                  >
                    <template v-slot:selection="{ item }">
                      <div v-if="item && item.raw" class="d-flex align-center gap-2">
                        <v-avatar size="24" color="indigo-lighten-4">
                          <v-img v-if="item.raw.avatar" :src="item.raw.avatar"></v-img>
                          <span v-else>{{ (item.raw.username || '').substring(0,2).toUpperCase() }}</span>
                        </v-avatar>
                        <span>{{ item.raw.username }}</span>
                      </div>
                    </template>
                  </v-select>
                  <div v-else class="d-flex align-center gap-2">
                    <v-avatar size="24" color="indigo-lighten-4">
                      <v-img v-if="selectedTask.assignee_avatar" :src="selectedTask.assignee_avatar"></v-img>
                      <span v-else>{{ (selectedTask.assignee_username || '').substring(0,2).toUpperCase() }}</span>
                    </v-avatar>
                    <span class="text-body-2 font-weight-bold">{{ selectedTask.assignee_username }}</span>
                  </div>
                </div>
                <a href="#" class="text-caption text-blue-darken-2 font-weight-bold d-inline-block mt-1 text-decoration-none" @click.prevent="assignToMe">Assign to me</a>
              </div>

              <!-- Reporter -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Reporter</label>
                <div class="d-flex align-center gap-2">
                  <v-avatar size="24" color="indigo-lighten-4">
                    <v-img v-if="selectedTask.creator_avatar" :src="selectedTask.creator_avatar"></v-img>
                    <span v-else>{{ (selectedTask.creator_username || 'US').substring(0,2).toUpperCase() }}</span>
                  </v-avatar>
                  <span class="text-body-2 font-weight-bold text-grey-darken-3">{{ selectedTask.creator_username || getAssigneeName(selectedTask.creator) }}</span>
                </div>
              </div>

              <!-- Labels -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Labels</label>
                <v-chip size="small" color="blue-grey" variant="tonal" class="font-weight-bold">GoJira</v-chip>
              </div>

              <!-- Due Date -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Due Date</label>
                <v-text-field
                  v-model="selectedTask.due_date"
                  type="date"
                  variant="outlined"
                  density="compact"
                  hide-details
                  @change="changeTaskDueDate(selectedTask.due_date)"
                  class="bg-white"
                ></v-text-field>
              </div>

              <!-- Original Estimate -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Original Estimate (Hours)</label>
                <v-text-field
                  v-model.number="selectedTask.duration"
                  type="number"
                  variant="outlined"
                  density="compact"
                  hide-details
                  @change="changeTaskDuration(selectedTask.duration)"
                  class="bg-white"
                ></v-text-field>
              </div>

              <!-- Department -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Department</label>
                <div class="text-body-2 font-weight-bold text-grey-darken-3 py-2 px-3 bg-white rounded border">
                  Yazılım
                </div>
              </div>

              <!-- Epic -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Epic</label>
                <v-select
                  v-model="selectedTask.epic"
                  :items="['Kullanıcı Yönetimi', 'Kanban Panosu', 'Raporlama & CSV']"
                  variant="outlined"
                  density="compact"
                  hide-details
                  @update:model-value="changeTaskEpic"
                  class="bg-white"
                ></v-select>
              </div>

              <!-- Version -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Version</label>
                <v-select
                  v-model="selectedTask.version"
                  :items="['v1.0', 'v1.1', 'v2.0']"
                  variant="outlined"
                  density="compact"
                  hide-details
                  @update:model-value="changeTaskVersion"
                  class="bg-white"
                ></v-select>
              </div>

              <!-- Priority -->
              <div class="mb-4">
                <label class="text-caption font-weight-bold text-grey-darken-1 d-block mb-1">Priority</label>
                <v-select
                  v-model="selectedTask.priority"
                  :items="priorityOptions"
                  item-title="title"
                  item-value="value"
                  variant="outlined"
                  density="compact"
                  hide-details
                  @update:model-value="changeTaskPriority"
                  class="bg-white"
                ></v-select>
              </div>
            </v-card>
          </v-col>
        </v-row>
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
              <!-- Görev Tipi -->
              <v-col cols="12" sm="6">
                <v-select
                  v-model="addForm.task_type"
                  :items="typeOptions"
                  item-title="title"
                  item-value="value"
                  label="Görev Tipi *"
                  variant="outlined"
                  density="comfortable"
                  required
                ></v-select>
              </v-col>

              <!-- Öncelik -->
              <v-col cols="12" sm="6">
                <v-select
                  v-model="addForm.priority"
                  :items="priorityOptions"
                  item-title="title"
                  item-value="value"
                  label="Öncelik *"
                  variant="outlined"
                  density="comfortable"
                  required
                ></v-select>
              </v-col>

              <!-- Tahmini Süre -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model.number="addForm.duration"
                  type="number"
                  label="Tahmini Süre (Saat)"
                  variant="outlined"
                  density="comfortable"
                  min="0"
                ></v-text-field>
              </v-col>

              <!-- Teslim Tarihi -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="addForm.due_date"
                  type="date"
                  label="Teslim Tarihi (Due Date)"
                  variant="outlined"
                  density="comfortable"
                ></v-text-field>
              </v-col>

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

              <!-- Atanan Kişi -->
              <v-col cols="12" sm="6">
                <v-select
                  v-if="isStaff"
                  v-model="addForm.assignee"
                  :items="usersList"
                  item-title="username"
                  item-value="id"
                  label="Atanan Kişi *"
                  variant="outlined"
                  density="comfortable"
                  :error-messages="addErrors.assignee"
                ></v-select>
                <v-text-field
                  v-else
                  :model-value="currentUsername"
                  label="Atanan Kişi"
                  variant="outlined"
                  density="comfortable"
                  disabled
                ></v-text-field>
              </v-col>

              <!-- Epic Seçimi -->
              <v-col cols="12" sm="6">
                <v-select
                  v-model="addForm.epic"
                  :items="['Kullanıcı Yönetimi', 'Kanban Panosu', 'Raporlama & CSV']"
                  label="Epic"
                  variant="outlined"
                  density="comfortable"
                ></v-select>
              </v-col>

              <!-- Sürüm Seçimi -->
              <v-col cols="12" sm="6">
                <v-select
                  v-model="addForm.version"
                  :items="['v1.0', 'v1.1', 'v2.0']"
                  label="Sürüm (Version)"
                  variant="outlined"
                  density="comfortable"
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
import { useTheme } from 'vuetify'
import api from '../api'

const theme = useTheme()
const currentTheme = computed(() => theme.global.name.value)

const tasks = ref([])
const usersList = ref([])
const loading = ref(false)

const drawer = ref(false)
const selectedTask = ref(null)

// Giriş yapan kullanıcının verileri
const currentUserId = ref(parseInt(localStorage.getItem('user_id')) || null)
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
const commentFile = ref(null)

// Alt Görev Kontrolleri
const showAddSubtaskInput = ref(false)
const newSubtaskTitle = ref('')
const subtaskSaving = ref(false)

const editingTitleInline = ref(false)
const inlineTitleVal = ref('')
const editingDescInline = ref(false)
const inlineDescVal = ref('')

// Durum (State) Seçenekleri
const stateItems = [
  { value: 'to do', title: 'TO DO' },
  { value: 'in progress', title: 'IN PROGRESS' },
  { value: 'in code review', title: 'IN CODE REVIEW' },
  { value: 'blocked dev', title: 'BLOCKED (DEV)' },
  { value: 'ready for test', title: 'READY FOR TEST' },
  { value: 'in test', title: 'IN TEST' },
  { value: 'blocked test', title: 'BLOCKED (TEST)' },
  { value: 'done', title: 'DONE' }
]

const columns = [
  { key: 'to do', title: 'TO DO', color: 'grey-darken-2', icon: 'mdi-clipboard-outline', bgClass: 'bg-grey-lighten-3' },
  { key: 'in progress', title: 'IN PROGRESS', color: 'blue-darken-3', icon: 'mdi-progress-clock', bgClass: 'bg-blue-lighten-5' },
  { key: 'in code review', title: 'IN CODE REVIEW', color: 'deep-purple-darken-3', icon: 'mdi-code-braces', bgClass: 'bg-deep-purple-lighten-5' },
  { key: 'blocked dev', title: 'BLOCKED (DEV)', color: 'red-darken-4', icon: 'mdi-alert-octagon', bgClass: 'bg-red-lighten-5' },
  { key: 'ready for test', title: 'READY FOR TEST', color: 'orange-darken-4', icon: 'mdi-flask-empty-outline', bgClass: 'bg-orange-lighten-5' },
  { key: 'in test', title: 'IN TEST', color: 'indigo-darken-4', icon: 'mdi-flask-outline', bgClass: 'bg-indigo-lighten-5' },
  { key: 'blocked test', title: 'BLOCKED (TEST)', color: 'red-darken-4', icon: 'mdi-alert-circle-outline', bgClass: 'bg-red-lighten-5' },
  { key: 'done', title: 'DONE', color: 'green-darken-3', icon: 'mdi-check-circle-outline', bgClass: 'bg-green-lighten-5' }
]

const searchQuery = ref('')
const selectedFilterUserId = ref(null)
const selectedPriorityFilter = ref('')
const selectedTypeFilter = ref('')
const onlyMyTasksFilter = ref(false)
const selectedVersionFilter = ref('')
const selectedEpicFilter = ref('')
const activeTab = ref('Active sprints')

const typeOptions = [
  { value: 'task', title: 'Görev' },
  { value: 'bug', title: 'Hata' },
  { value: 'story', title: 'Hikaye' },
  { value: 'epic', title: 'Epic' }
]

const priorityOptions = [
  { value: 'low', title: 'Düşük' },
  { value: 'medium', title: 'Orta' },
  { value: 'high', title: 'Yüksek' },
  { value: 'critical', title: 'Acil' }
]

const toggleUserFilter = (userId) => {
  if (selectedFilterUserId.value === userId) {
    selectedFilterUserId.value = null
  } else {
    selectedFilterUserId.value = userId
  }
}

const clearUserFilter = () => {
  selectedFilterUserId.value = null
}

const getTypeIcon = (type) => {
  if (type === 'bug') return 'mdi-bug'
  if (type === 'story') return 'mdi-bookmark'
  if (type === 'epic') return 'mdi-flash'
  return 'mdi-checkbox-marked-circle-outline'
}

const getTypeColor = (type) => {
  if (type === 'bug') return 'red'
  if (type === 'story') return 'green'
  if (type === 'epic') return 'purple'
  return 'blue'
}

const getTypeLabel = (type) => {
  if (!type) return 'Tümü'
  const found = typeOptions.find(t => t.value === type)
  return found ? found.title : type
}

const getPriorityIcon = (priority) => {
  if (priority === 'critical') return 'mdi-arrow-up-bold-circle'
  if (priority === 'high') return 'mdi-arrow-up-bold'
  if (priority === 'medium') return 'mdi-arrow-right-bold'
  return 'mdi-arrow-down-bold'
}

const getPriorityColor = (priority) => {
  if (priority === 'critical') return 'red'
  if (priority === 'high') return 'orange'
  if (priority === 'medium') return 'blue'
  return 'grey'
}

const getPriorityLabel = (priority) => {
  if (!priority) return 'Tümü'
  const found = priorityOptions.find(p => p.value === priority)
  return found ? found.title : priority
}

const isOverdue = (dateStr) => {
  if (!dateStr) return false
  return new Date(dateStr) < new Date()
}

const formatShortDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('tr-TR', { month: 'short', day: 'numeric' })
}

const getTasksByState = (stateKey) => {
  let filtered = tasks.value.filter(t => t.state === stateKey && !t.parent)
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(t => 
      t.title.toLowerCase().includes(q) || 
      t.definition.toLowerCase().includes(q) ||
      (t.assignee_username && t.assignee_username.toLowerCase().includes(q))
    )
  }

  if (selectedFilterUserId.value !== null) {
    filtered = filtered.filter(t => t.assignee === selectedFilterUserId.value)
  }

  if (onlyMyTasksFilter.value) {
    filtered = filtered.filter(t => t.assignee === currentUserId.value)
  }

  if (selectedTypeFilter.value) {
    filtered = filtered.filter(t => t.task_type === selectedTypeFilter.value)
  }

  if (selectedPriorityFilter.value) {
    filtered = filtered.filter(t => t.priority === selectedPriorityFilter.value)
  }

  if (selectedVersionFilter.value) {
    filtered = filtered.filter(t => t.version === selectedVersionFilter.value)
  }

  if (selectedEpicFilter.value) {
    filtered = filtered.filter(t => t.epic === selectedEpicFilter.value)
  }

  return filtered
}

const getCardBorderClass = (stateKey) => {
  if (stateKey === 'to do') return 'border-grey-left'
  if (stateKey === 'in progress') return 'border-blue-left'
  if (stateKey === 'in code review') return 'border-purple-left'
  if (stateKey === 'blocked dev' || stateKey === 'blocked test') return 'border-red-left'
  if (stateKey === 'ready for test') return 'border-orange-left'
  if (stateKey === 'in test') return 'border-indigo-left'
  if (stateKey === 'done') return 'border-green-left'
  return ''
}

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

const exporting = ref(false)
const activeDragOverColumn = ref(null)

const onDragStart = (event, task) => {
  event.dataTransfer.setData('text/plain', String(task.id))
  event.dataTransfer.effectAllowed = 'move'
}

const onDrop = async (event, newState) => {
  activeDragOverColumn.value = null
  const taskId = parseInt(event.dataTransfer.getData('text/plain'))
  if (isNaN(taskId)) return

  const task = tasks.value.find(t => t.id === taskId)
  if (!task) return

  if (task.state === newState) return

  // Arayüzde anında güncel görünmesi için (Optimistic UI update)
  const oldState = task.state
  task.state = newState

  try {
    await api.patch(`tasks/${taskId}/`, { state: newState })
    console.log("Görev sürüklenerek başarıyla taşındı.")
  } catch (error) {
    console.error("Görev taşınırken hata oluştu:", error)
    task.state = oldState // Hata halinde geri al
    alert("Görev taşınırken bir hata oluştu.")
  }
}

const exportTasks = async () => {
  exporting.value = true
  try {
    const response = await api.get('tasks/export_excel/', {
      responseType: 'blob'
    })
    
    // Blob dosyasını indir
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = window.URL.createObjectURL(blob)
    link.href = url
    link.setAttribute('download', 'gorevler.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error("Görevler dışa aktarılırken hata oluştu:", error)
    alert("Görevler dışa aktarılamadı.")
  } finally {
    exporting.value = false
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
  editingTitleInline.value = false
  editingDescInline.value = false
  newCommentText.value = ''
  commentFile.value = null
  showAddSubtaskInput.value = false
  newSubtaskTitle.value = ''
  drawer.value = true
  refreshTaskDetails()
}

const saveSubtask = async () => {
  if (!newSubtaskTitle.value.trim() || !selectedTask.value) return
  subtaskSaving.value = true
  try {
    await api.post('tasks/', {
      title: newSubtaskTitle.value.trim(),
      definition: 'Alt Görev',
      parent: selectedTask.value.id,
      assignee: selectedTask.value.assignee || currentUserId.value,
      state: 'to do'
    })
    newSubtaskTitle.value = ''
    showAddSubtaskInput.value = false
    await refreshTaskDetails()
    await fetchTasks()
  } catch (error) {
    console.error("Alt görev eklenirken hata oluştu:", error)
    alert("Alt görev eklenemedi.")
  } finally {
    subtaskSaving.value = false
  }
}

const toggleSubtaskState = async (subtask) => {
  const newState = subtask.state === 'done' ? 'to do' : 'done'
  try {
    await api.patch(`tasks/${subtask.id}/`, { state: newState })
    await refreshTaskDetails()
    await fetchTasks()
  } catch (error) {
    console.error("Alt görev durumu güncellenemedi:", error)
    alert("Alt görev durumu güncellenemedi.")
  }
}

const deleteSubtask = async (subtaskId) => {
  if (!confirm("Bu alt görevi silmek istediğinizden emin misiniz?")) return
  try {
    await api.delete(`tasks/${subtaskId}/`)
    await refreshTaskDetails()
    await fetchTasks()
  } catch (error) {
    console.error("Alt görev silinirken hata oluştu:", error)
    alert("Alt görev silinemedi.")
  }
}

const saveTitleInline = async () => {
  if (!selectedTask.value || !inlineTitleVal.value.trim()) {
    editingTitleInline.value = false
    return
  }
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { title: inlineTitleVal.value.trim() })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].title = inlineTitleVal.value.trim()
    }
    selectedTask.value.title = inlineTitleVal.value.trim()
    editingTitleInline.value = false
  } catch (error) {
    console.error("Başlık güncellenemedi:", error)
  }
}

const saveDescInline = async () => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { definition: inlineDescVal.value })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].definition = inlineDescVal.value
    }
    selectedTask.value.definition = inlineDescVal.value
    editingDescInline.value = false
  } catch (error) {
    console.error("Açıklama güncellenemedi:", error)
  }
}

const assignToMe = async () => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { assignee: currentUserId.value })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].assignee = currentUserId.value
      tasks.value[index].assignee_username = currentUsername.value
    }
    await refreshTaskDetails()
    fetchTasks()
  } catch (error) {
    console.error("Görev atanamadı:", error)
  }
}

// Görev Ekleme Pop-up'ını Aç
const openAddDialog = () => {
  addErrors.value = {}
  addForm.value = {
    title: '',
    definition: '',
    state: 'to do',
    assignee: isStaff.value ? null : currentUserId.value,
    priority: 'medium',
    task_type: 'task',
    duration: 0,
    due_date: null,
    epic: '',
    version: ''
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

const changeTaskPriority = async (val) => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { priority: val })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].priority = val
    }
  } catch (error) {
    console.error("Öncelik güncellenemedi:", error)
  }
}

const changeTaskType = async (val) => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { task_type: val })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].task_type = val
    }
  } catch (error) {
    console.error("Görev tipi güncellenemedi:", error)
  }
}

const changeTaskDuration = async (val) => {
  if (!selectedTask.value) return
  const numVal = parseInt(val) || 0
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { duration: numVal })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].duration = numVal
    }
  } catch (error) {
    console.error("Süre güncellenemedi:", error)
  }
}

const changeTaskDueDate = async (val) => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { due_date: val || null })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].due_date = val || null
    }
  } catch (error) {
    console.error("Teslim tarihi güncellenemedi:", error)
  }
}

const changeTaskEpic = async (val) => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { epic: val || '' })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].epic = val || ''
    }
  } catch (error) {
    console.error("Epic güncellenemedi:", error)
  }
}

const changeTaskVersion = async (val) => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    await api.patch(`tasks/${id}/`, { version: val || '' })
    const index = tasks.value.findIndex(t => t.id === id)
    if (index !== -1) {
      tasks.value[index].version = val || ''
    }
  } catch (error) {
    console.error("Sürüm güncellenemedi:", error)
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

// Görevin Detaylarını Yenile (Yorumlar/Dosyalar eklendiğinde/silindiğinde kullanmak için)
const refreshTaskDetails = async () => {
  if (!selectedTask.value) return
  try {
    const id = selectedTask.value.id
    const response = await api.get(`tasks/${id}/`)
    selectedTask.value = response.data
  } catch (error) {
    console.error("Görev detayları yenilenirken hata oluştu:", error)
  }
}

// Yorum Ekle
const addComment = async () => {
  if (!selectedTask.value) return
  if (!newCommentText.value.trim() && !commentFile.value) return
  commentSaving.value = true
  try {
    const commentRes = await api.post('comments/', {
      task: selectedTask.value.id,
      description: newCommentText.value.trim()
    })
    
    if (commentFile.value) {
      await api.post('attachments/', {
        comment: commentRes.data.id,
        name: commentFile.value.name,
        file_data: commentFile.value.data,
        file_type: commentFile.value.type
      })
      commentFile.value = null
    }

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

// Görev Dosyası Yükleme
const handleTaskFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async () => {
    try {
      await api.post('attachments/', {
        task: selectedTask.value.id,
        name: file.name,
        file_data: reader.result,
        file_type: file.type
      })
      await refreshTaskDetails()
      // Panodaki dosya/durum güncelliği için görevleri yeniden çek
      fetchTasks()
    } catch (error) {
      console.error("Dosya yüklenemedi:", error)
      alert("Dosya yüklenirken bir hata oluştu.")
    }
  }
  reader.readAsDataURL(file)
}

// Yorum Dosyası Seçme
const handleCommentFileSelection = (event) => {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    commentFile.value = {
      name: file.name,
      data: reader.result,
      type: file.type
    }
  }
  reader.readAsDataURL(file)
}

// Dosya İndirme
const downloadAttachment = (file) => {
  const link = document.createElement('a')
  link.href = file.file_data
  link.setAttribute('download', file.name)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Dosya Silme
const deleteAttachment = async (file) => {
  if (!confirm("Bu dosyayı silmek istediğinizden emin misiniz?")) return
  try {
    await api.delete(`attachments/${file.id}/`)
    await refreshTaskDetails()
    fetchTasks()
  } catch (error) {
    console.error("Dosya silinemedi:", error)
    alert("Dosya silinirken bir hata oluştu.")
  }
}

// Dosya İkonu Çöz
const getFileIcon = (fileType) => {
  if (!fileType) return 'mdi-file'
  if (fileType.includes('image')) return 'mdi-file-image'
  if (fileType.includes('pdf')) return 'mdi-file-pdf-box'
  if (fileType.includes('word') || fileType.includes('officedocument')) return 'mdi-file-word'
  if (fileType.includes('excel') || fileType.includes('sheet') || fileType.includes('csv')) return 'mdi-file-excel'
  return 'mdi-file-document'
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
  if (isStaff.value) {
    fetchUsers()
  }
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
.drag-over-active {
  background-color: rgba(63, 81, 181, 0.15) !important;
  outline: 2px dashed #3f51b5 !important;
  transition: all 0.2s ease;
}
.border-grey-left { border-left: 4px solid #9e9e9e !important; }
.border-blue-left { border-left: 4px solid #2196f3 !important; }
.border-purple-left { border-left: 4px solid #9c27b0 !important; }
.border-red-left { border-left: 4px solid #f44336 !important; }
.border-orange-left { border-left: 4px solid #ff9800 !important; }
.border-indigo-left { border-left: 4px solid #3f51b5 !important; }
.border-green-left { border-left: 4px solid #4caf50 !important; }
.tab-item {
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
}
.tab-item:hover {
  color: #1976d2 !important;
}
.active-tab {
  border-bottom: 2px solid #1976d2 !important;
}
.hover-avatar {
  border: 2px solid white;
  transition: transform 0.2s ease, z-index 0.2s ease;
}
.hover-avatar:hover {
  transform: translateY(-4px) scale(1.1);
  z-index: 10 !important;
}
.active-avatar-filter {
  border: 2.5px solid #1976d2 !important;
  transform: translateY(-2px) scale(1.05);
}
</style>

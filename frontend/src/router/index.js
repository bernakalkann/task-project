import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Login from '../Login.vue'
import TasksView from '../views/TasksView.vue'
import UsersView from '../views/UsersView.vue'
import ProfileView from '../views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/tasks',
      name: 'tasks',
      component: TasksView,
    },
    {
      path: '/users',
      name: 'users',
      component: UsersView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
    },
  ],
})

// Sayfa geçiş koruması (Navigation Guard)
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token');
  const isStaff = localStorage.getItem('is_staff') === 'true';

  // 1. Giriş yapmamış kullanıcıyı Giriş Yap sayfasına yönlendir
  if (to.name !== 'login' && !token) {
    return { name: 'login' };
  } 
  // 2. Giriş yapmış kullanıcıyı tekrar login sayfasına sokma
  else if (to.name === 'login' && token) {
    return { name: 'home' };
  } 
  // 3. Admin olmayan kullanıcıların Users menüsüne erişmesini engelle
  else if (to.name === 'users' && !isStaff) {
    return { name: 'home' };
  } 
})

export default router

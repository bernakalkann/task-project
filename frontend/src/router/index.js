import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Login from '../Login.vue'
import TasksView from '../views/TasksView.vue'
import UsersView from '../views/UsersView.vue'
import ProfileView from '../views/ProfileView.vue'
import ResetPassword from '../views/ResetPassword.vue'
import LogsView from '../views/LogsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: ResetPassword,
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
    {
      path: '/logs',
      name: 'logs',
      component: LogsView,
    },
  ],
})

// Sayfa geçiş koruması (Navigation Guard)
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token');
  const isStaff = localStorage.getItem('is_staff') === 'true';

  // 1. Giriş yapmamış kullanıcıyı (login ve reset-password harici) Giriş Yap sayfasına yönlendir
  if (to.name !== 'login' && to.name !== 'reset-password' && !token) {
    return { name: 'login' };
  } 
  // 2. Giriş yapmış kullanıcıyı tekrar login sayfasına sokma
  else if (to.name === 'login' && token) {
    return { name: 'home' };
  } 
  // 3. Admin olmayan kullanıcıların Users ve Logs ekranına erişmesini engelle
  else if ((to.name === 'users' || to.name === 'logs') && !isStaff) {
    return { name: 'home' };
  } 
})

export default router

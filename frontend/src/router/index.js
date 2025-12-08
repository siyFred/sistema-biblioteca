import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import MainLayout from '../layouts/MainLayout.vue'

const DashboardView = () => import('../views/DashboardView.vue')
const BooksView = () => import('../views/BooksView.vue')
const BookFormView = () => import('../views/BookFormView.vue')
const BookDetailView = () => import('../views/BookDetailView.vue')
const LoansView = () => import('../views/LoansView.vue')
const ProfileView = () => import('../views/ProfileView.vue')
const GestaoEmprestimosView = () => import('../views/GestaoEmprestimosView.vue')
const ManageUsersView = () => import('../views/ManageUsers.vue')
const PurchaseRequestView = () => import('../views/PurchaseRequestView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guest: true }
    },
    {
      path: '/',
      component: MainLayout,
      meta: { auth: true },
      children: [
        { path: 'dashboard', name: 'dashboard', component: DashboardView },
        { path: 'books', name: 'books', component: BooksView },
        { path: 'books/new', name: 'new-book', component: BookFormView },
        { path: 'books/:id', name: 'book-detail', component: BookDetailView },
        { 
            path: 'books/google/:googleId', 
            name: 'google-book-detail', 
            component: BookDetailView 
        },
        { path: 'books/:id/edit', name: 'edit-book', component: BookFormView },
        { path: 'loans', name: 'loans', component: LoansView },
        { path: 'profile', name: 'profile', component: ProfileView },
        
        { 
          path: 'admin/loans', 
          name: 'admin-loans', 
          component: GestaoEmprestimosView 
        },
        { 
          path: 'admin/users', 
          name: 'admin-users', 
          component: ManageUsersView 
        },
        { 
          path: 'admin/suggestions', 
          name: 'admin-suggestions', 
          component: PurchaseRequestView 
        }
      ]
    },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.auth && !token) next('/') 
  else if (to.meta.guest && token) next('/dashboard') 
  else next()
})

export default router

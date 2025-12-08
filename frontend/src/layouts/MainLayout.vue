<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const handleLogout = () => {
  auth.logout()
}
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="brand">📚 KotarLib</div>
      
      <div class="user-mini-profile">
        <div class="avatar-small">
            {{ auth.user?.username?.charAt(0).toUpperCase() || 'U' }}
        </div>
        <div class="user-details">
            <span class="name">{{ auth.user?.username }}</span>
            <span class="role">{{ auth.isLibrarian ? 'Bibliotecário' : 'Leitor' }}</span>
        </div>
      </div>

      <nav>
        <router-link to="/dashboard">📊 Dashboard</router-link>
        <router-link to="/books">📖 Acervo</router-link>
        <router-link to="/loans">🔄 Meus Livros</router-link>
        
        <div v-if="auth.isLibrarian" class="admin-section">
            <span class="menu-label">ADMINISTRAÇÃO</span>
            <router-link to="/admin/loans" class="admin-link">
                👮 Gestão Empréstimos
            </router-link>
            <router-link to="/admin/users" class="admin-link">
                👥 Gestão Usuários
            </router-link>
            <router-link to="/admin/suggestions" class="admin-link">
                💡 Sugestões de Compra
            </router-link>
        </div>

        <router-link to="/profile" style="margin-top: auto">👤 Meu Perfil</router-link>
      </nav>
      
      <button @click="handleLogout" class="btn-logout">Sair do Sistema</button>
    </aside>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-layout { display: flex; height: 100vh; font-family: 'Segoe UI', sans-serif; background: #f5f7fa; }
.sidebar { width: 260px; background: #2c3e50; color: white; display: flex; flex-direction: column; padding: 20px; box-sizing: border-box; }
.brand { color: #42b883; text-align: center; margin-bottom: 30px; font-size: 1.5rem; font-weight: bold; letter-spacing: 1px; }

.user-mini-profile { display: flex; align-items: center; gap: 10px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px; margin-bottom: 25px; }
.avatar-small { width: 40px; height: 40px; background: #42b883; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; }
.user-details { display: flex; flex-direction: column; overflow: hidden; }
.name { font-weight: bold; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.role { font-size: 0.75rem; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.5px; }

nav { display: flex; flex-direction: column; gap: 8px; flex: 1; }
nav a { color: #bdc3c7; text-decoration: none; padding: 12px 15px; border-radius: 8px; transition: 0.2s; display: flex; align-items: center; gap: 10px; font-size: 0.95rem; }
nav a:hover, nav a.router-link-active { background: #34495e; color: white; font-weight: bold; transform: translateX(5px); }

.admin-section { margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; gap: 5px; }
.menu-label { font-size: 0.7rem; color: #7f8c8d; font-weight: bold; padding-left: 10px; margin-bottom: 5px; }
.admin-link { color: #f39c12 !important; }
.admin-link:hover { background: rgba(243, 156, 18, 0.1); }

.btn-logout { width: 100%; padding: 12px; background: none; border: 1px solid #e74c3c; color: #e74c3c; border-radius: 6px; cursor: pointer; margin-top: 20px; transition: 0.2s; font-weight: bold; }
.btn-logout:hover { background: #e74c3c; color: white; }

.content { flex: 1; padding: 30px; overflow-y: auto; }
</style>
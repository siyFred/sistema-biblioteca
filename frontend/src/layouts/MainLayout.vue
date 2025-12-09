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
            <router-link to="/admin/books" class="admin-link">
                📚 Gestão Acervo
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
.app-layout { 
  display: flex; 
  height: 100vh; 
  width: 100vw;
  background: var(--background);
  overflow: hidden; /* Evita scrollbar na janela principal */
}

/* SIDEBAR */
.sidebar { 
  width: 280px; 
  background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%); 
  color: white; 
  display: flex; 
  flex-direction: column; 
  padding: 25px; 
  box-shadow: 4px 0 15px rgba(0,0,0,0.1);
  z-index: 10;
  overflow-y: auto; /* Permite scroll na sidebar se a tela for pequena */
}

.brand { 
  color: var(--accent); 
  text-align: center; 
  margin-bottom: 40px; 
  font-size: 1.6rem; 
  font-weight: 800; 
  letter-spacing: 1px; 
  text-transform: uppercase;
}

/* MINI PERFIL */
.user-mini-profile { 
  display: flex; 
  align-items: center; 
  gap: 15px; 
  padding: 15px; 
  background: rgba(255,255,255,0.08); 
  border-radius: var(--radius-md); 
  margin-bottom: 30px; 
  border: 1px solid rgba(255,255,255,0.05);
}

.avatar-small { 
  width: 42px; 
  height: 42px; 
  background: var(--accent); 
  border-radius: 50%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-weight: bold; 
  font-size: 1.2rem; 
  color: white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.user-details { display: flex; flex-direction: column; overflow: hidden; }
.name { font-weight: 600; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.role { font-size: 0.75rem; opacity: 0.8; letter-spacing: 0.5px; margin-top: 2px; }

/* NAVEGAÇÃO */
nav { display: flex; flex-direction: column; gap: 8px; flex: 1; }
nav a { 
  color: rgba(255,255,255,0.7); 
  text-decoration: none; 
  padding: 12px 18px; 
  border-radius: var(--radius-sm); 
  transition: all var(--transition-fast); 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  font-size: 0.95rem; 
  font-weight: 500;
}

nav a:hover { 
  background: rgba(255,255,255,0.1); 
  color: white; 
  transform: translateX(4px);
}

nav a.router-link-active { 
  background: var(--accent); 
  color: white; 
  font-weight: 600; 
  transform: translateX(4px);
  box-shadow: 0 4px 10px rgba(66, 184, 131, 0.3);
}

/* ADMIN */
.admin-section { 
  margin-top: 20px; 
  padding-top: 20px; 
  border-top: 1px solid rgba(255,255,255,0.1); 
  display: flex; 
  flex-direction: column; 
  gap: 5px; 
}

.menu-label { 
  font-size: 0.7rem; 
  color: rgba(255,255,255,0.4); 
  font-weight: 700; 
  padding-left: 10px; 
  margin-bottom: 8px; 
  letter-spacing: 1px;
}

.admin-link { color: var(--warning) !important; opacity: 0.9; }
.admin-link:hover { background: rgba(241, 196, 15, 0.15); color: #fff !important; }

/* LOGOUT */
.btn-logout { 
  width: 100%; 
  padding: 12px; 
  background: transparent; 
  border: 1px solid rgba(231, 76, 60, 0.5); 
  color: #ff6b6b; 
  border-radius: var(--radius-sm); 
  cursor: pointer; 
  margin-top: 20px; 
  transition: var(--transition-fast); 
  font-weight: 600; 
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-logout:hover { 
  background: var(--danger); 
  color: white; 
  border-color: var(--danger);
  transform: translateY(-2px);
}

/* CONTENT */
.content { 
  flex: 1; 
  padding: 40px; 
  overflow-y: auto; 
  scroll-behavior: smooth;
}
</style>
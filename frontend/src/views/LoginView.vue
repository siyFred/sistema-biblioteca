<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const errorMsg = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    await authStore.login(username.value, password.value)
    router.push('/dashboard')
  } catch (error) {
    errorMsg.value = "Usuário ou senha incorretos."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="card auth-card">
      <div class="header">
        <h1>📚 KotarLib</h1>
        <p class="subtitle">Bem-vindo de volta!</p>
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-3 text-left">
            <label for="username" class="label">Usuário</label>
            <input 
                id="username" 
                v-model="username" 
                class="input"
                placeholder="Seu login" 
                required 
                autocomplete="username" 
            />
        </div>

        <div class="mb-3 text-left">
            <label for="password" class="label">Senha</label>
            <input 
                id="password" 
                type="password" 
                v-model="password" 
                class="input"
                placeholder="Sua senha" 
                required 
                autocomplete="current-password" 
            />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button type="submit" :disabled="loading" class="btn btn-primary w-full mt-2">
            {{ loading ? 'Entrando...' : 'Acessar Conta' }}
        </button>
      </form>

      <div class="footer-links">
        <p class="link">Novo por aqui? <router-link to="/register">Crie uma conta</router-link></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-container { 
  min-height: 100vh; 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  padding: 20px; 
  background: var(--background);
  background-image: radial-gradient(#e0e0e0 1px, transparent 1px);
  background-size: 20px 20px;
}

.auth-card { width: 100%; max-width: 400px; text-align: center; }

.header h1 { font-size: 2rem; font-weight: 800; color: var(--primary); margin-bottom: 5px; }
.subtitle { color: var(--text-muted); font-size: 1rem; margin-bottom: 30px; }

.label { display: block; font-size: 0.85rem; font-weight: 600; color: var(--text-main); margin-bottom: 6px; }
.text-left { text-align: left; }
.mt-2 { margin-top: 10px; }

.error-msg { 
  color: var(--danger); 
  font-size: 0.9rem; 
  margin-bottom: 15px; 
  background: rgba(231, 76, 60, 0.1); 
  padding: 10px; 
  border-radius: var(--radius-sm);
  border: 1px solid rgba(231, 76, 60, 0.2);
}

.footer-links { margin-top: 25px; border-top: 1px solid var(--border-color); padding-top: 20px; }
.link { font-size: 0.9rem; color: var(--text-muted); }
</style>
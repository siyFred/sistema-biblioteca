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
    <div class="card">
      <div class="header">
        <h1>📚 KotarLib</h1>
        <p class="subtitle">Bem-vindo de volta!</p>
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="input-group">
            <label for="username">Usuário</label>
            <input 
                id="username" 
                v-model="username" 
                placeholder="Seu login" 
                required 
                autocomplete="username" 
            />
        </div>

        <div class="input-group">
            <label for="password">Senha</label>
            <input 
                id="password" 
                type="password" 
                v-model="password" 
                placeholder="Sua senha" 
                required 
                autocomplete="current-password" 
            />
        </div>

        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>

        <button type="submit" :disabled="loading" class="btn-primary">
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
/* Container Principal (Igual ao Register) */
.auth-container { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: #eef2f5; padding: 20px; }

/* Cartão (Igual ao Register) */
.card { background: white; padding: 40px 30px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); width: 100%; max-width: 400px; text-align: center; }

/* Tipografia */
.header h1 { font-size: 1.8rem; font-weight: bold; color: #2c3e50; margin-bottom: 5px; }
.subtitle { color: #7f8c8d; font-size: 1rem; margin-bottom: 30px; }

/* Inputs (Igual ao Register) */
.input-group { margin-bottom: 15px; display: flex; flex-direction: column; text-align: left; }
label { font-size: 0.85rem; font-weight: bold; color: #666; margin-bottom: 6px; }

input { 
    width: 100%; 
    padding: 12px; 
    border: 1px solid #ddd; 
    border-radius: 6px; 
    font-size: 1rem; 
    box-sizing: border-box; 
    transition: 0.2s;
}

input:focus { 
    border-color: #42b883; 
    outline: none; 
    box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1); 
}

/* Botão Principal */
button { 
    width: 100%; 
    padding: 14px; 
    background: #2c3e50; 
    color: white; 
    border: none; 
    border-radius: 6px; 
    font-size: 1rem; 
    font-weight: bold; 
    cursor: pointer; 
    transition: 0.2s; 
    margin-top: 10px;
}

button:hover:not(:disabled) { background: #34495e; transform: translateY(-1px); }
button:disabled { opacity: 0.7; cursor: not-allowed; }

/* Mensagens e Links */
.error { 
    color: #e74c3c; 
    font-size: 0.9rem; 
    margin-bottom: 15px; 
    background: #fadbd8; 
    padding: 10px; 
    border-radius: 6px; 
}

.footer-links { margin-top: 25px; border-top: 1px solid #eee; padding-top: 20px; }
.link { font-size: 0.9rem; color: #666; }
a { color: #42b883; font-weight: bold; text-decoration: none; transition: 0.2s; }
a:hover { color: #2ecc71; text-decoration: underline; }
</style>
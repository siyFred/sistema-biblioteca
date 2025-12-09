<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const auth = useAuthStore()
const stats = ref({}) // Começa vazio
const loading = ref(true)

const fetchStats = async () => {
    try {
        // Chama a rota específica que conta tudo no servidor
        const { data } = await api.get('dashboard/')
        stats.value = data
    } catch (e) {
        console.error("Erro ao carregar dashboard:", e)
    } finally {
        loading.value = false
    }
}

onMounted(fetchStats)
</script>

<template>
  <div class="dashboard-container">
    <div class="welcome-header">
        <h1>Olá, {{ auth.user?.username || 'Leitor' }}! 👋</h1>
        <p class="subtitle">Aqui está o resumo da sua biblioteca.</p>
    </div>

    <div v-if="loading" class="loading-state">
        <p>Carregando dados...</p>
    </div>

    <div v-else class="stats-grid">
        
        <template v-if="stats.is_admin">
            <div class="card blue">
                <h3>{{ stats.total_books }}</h3>
                <p>📚 Livros no Acervo</p>
            </div>
            <div class="card green">
                <h3>{{ stats.total_users }}</h3>
                <p>👥 Leitores Cadastrados</p>
            </div>
            <div class="card orange">
                <h3>{{ stats.active_loans }}</h3>
                <p>🔄 Empréstimos Ativos</p>
            </div>
            <div class="card red">
                <h3>{{ stats.overdue_loans }}</h3>
                <p>⚠️ Pendências Gerais</p>
            </div>
        </template>

        <template v-else>
            <div class="card blue">
                <h3>{{ stats.my_active_loans }}</h3>
                <p>📖 Estou Lendo</p>
            </div>
            <div class="card green">
                <h3>{{ stats.my_history }}</h3>
                <p>📜 Já Li (Histórico)</p>
            </div>
            <div class="card red" v-if="stats.my_overdue > 0">
                <h3>{{ stats.my_overdue }}</h3>
                <p>⚠️ Preciso Devolver!</p>
            </div>
            <div class="card gray" v-else>
                <h3>0</h3>
                <p>✅ Nenhuma Pendência</p>
            </div>
        </template>
    
    </div>

    <div class="shortcuts">
        <h3>Acesso Rápido</h3>
        <div class="buttons">
            <router-link to="/books" class="btn-shortcut">🔍 Ver Livros</router-link>
            
            <router-link v-if="!stats.is_admin" to="/loans" class="btn-shortcut">
                📅 Meus Prazos
            </router-link>

            <router-link v-if="stats.is_admin" to="/admin/loans" class="btn-shortcut admin">
                👮 Gestão de Empréstimos
            </router-link>
            
            <router-link v-if="stats.is_admin" to="/books/new" class="btn-shortcut admin">
                ➕ Cadastrar Livro
            </router-link>
        </div>
    </div>

  </div>
</template>

<style scoped>
.dashboard-container { max-width: 1000px; margin: 0 auto; padding-top: 20px; }

.welcome-header h1 { color: #2c3e50; margin-bottom: 5px; font-size: 1.8rem; }
.subtitle { color: #7f8c8d; margin-bottom: 30px; font-size: 1.1rem; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }

.card { padding: 30px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); transition: transform 0.2s; }
.card:hover { transform: translateY(-5px); }
.card h3 { font-size: 3rem; margin: 0; font-weight: bold; }
.card p { font-size: 1rem; opacity: 0.9; margin-top: 5px; font-weight: 500; }

/* Cores dos Cards */
.blue { background: linear-gradient(135deg, #3498db, #2980b9); }
.green { background: linear-gradient(135deg, #2ecc71, #27ae60); }
.orange { background: linear-gradient(135deg, #f39c12, #d35400); }
.red { background: linear-gradient(135deg, #e74c3c, #c0392b); }
.gray { background: linear-gradient(135deg, #95a5a6, #7f8c8d); }

/* Atalhos */
.shortcuts h3 { color: #2c3e50; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.buttons { display: flex; gap: 15px; flex-wrap: wrap; }

.btn-shortcut { 
    padding: 15px 25px; 
    background: white; 
    border: 1px solid #ddd; 
    border-radius: 8px; 
    text-decoration: none; 
    color: #2c3e50; 
    font-weight: bold; 
    transition: 0.2s; 
    display: flex; align-items: center; gap: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
}
.btn-shortcut:hover { border-color: #42b883; color: #42b883; transform: translateY(-2px); box-shadow: 0 5px 10px rgba(0,0,0,0.1); }

/* Botões exclusivos de Admin */
.btn-shortcut.admin { border-left: 4px solid #f39c12; }
.btn-shortcut.admin:hover { border-color: #f39c12; background: #fffcf5; color: #d35400; }

.loading-state { text-align: center; color: #7f8c8d; font-size: 1.2rem; margin: 40px 0; }
</style>
<template>
  <div class="admin-loans-container">
    <header class="view-header">
      <div>
        <h1>👮 Gestão de Empréstimos</h1>
        <p class="subtitle">Painel do Bibliotecário</p>
      </div>
      
      <div class="actions">
        <div class="search-box">
          <input 
            v-model="search" 
            placeholder="Buscar por usuário ou livro..." 
            @keyup.enter="fetchLoans"
          />
          <button @click="fetchLoans">🔍</button>
        </div>

        <select v-model="statusFilter" @change="fetchLoans" class="status-select">
          <option value="">Todos os Status</option>
          <option value="PENDING">⏳ Pendentes (Solicitações)</option>
          <option value="ACTIVE">📖 Em Andamento</option>
          <option value="OVERDUE">⚠️ Atrasados</option>
          <option value="RETURNED">✅ Devolvidos</option>
          <option value="REJECTED">🚫 Rejeitados</option>
        </select>
      </div>
    </header>

    <div v-if="loading" class="loading-state">
      Carregando dados...
    </div>

    <div v-else-if="Object.keys(groupedLoans).length === 0" class="empty-state">
      Nenhum empréstimo encontrado com esses filtros.
    </div>

    <div v-else class="loans-list">
      <div v-for="(group, user) in groupedLoans" :key="user" class="user-group-card">
        <div class="group-header">
          <h3>👤 {{ user }}</h3>
          <span class="count-badge">{{ group.length }} livro(s)</span>
        </div>
        
        <table>
          <thead>
            <tr>
              <th>Livro</th>
              <th>Solicitado em</th>
              <th>Vencimento</th>
              <th>Status</th>
              <th>Multa</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="loan in group" :key="loan.id">
              <td><strong>{{ loan.book_title }}</strong></td>
              <td>{{ formatDate(loan.loan_date) }}</td>
              
              <td>
                <span v-if="loan.due_date">{{ formatDate(loan.due_date) }}</span>
                <span v-else class="text-muted">-</span>
              </td>
              
              <td>
                <span :class="['status-badge', loan.status]">
                  {{ translateStatus(loan.status) }}
                </span>
              </td>

              <td>
                 <div v-if="loan.paid" class="text-green">
                    <span class="status-badge paid">PAGO</span>
                 </div>
                 <div v-else-if="loan.fine_amount && parseFloat(loan.fine_amount) > 0" class="text-red font-bold">
                    {{ formatCurrency(loan.fine_amount) }}
                 </div>
                 <span v-else class="text-muted">-</span>
              </td>
              
              <td class="actions-cell">
                <div v-if="loan.status === 'PENDING'" class="btn-group">
                  <button @click="approveLoan(loan.id)" class="btn-approve" title="Aprovar">
                    ✅ Aprovar
                  </button>
                  <button @click="rejectLoan(loan.id)" class="btn-reject" title="Rejeitar">
                    ❌ Rejeitar
                  </button>
                </div>

                <div v-if="['ACTIVE', 'OVERDUE'].includes(loan.status)" class="btn-group">
                  <button @click="markReturned(loan.id)" class="btn-return">
                    📥 Receber
                  </button>
                </div>

                <div v-if="loan.fine_amount > 0 && !loan.paid" class="btn-group">
                    <button @click="payLoan(loan.id)" class="btn-pay" title="Pagar Multa">
                        💰 Pagar
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import { useAlert } from '../utils/alert'

const swal = useAlert()
const loans = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('PENDING')

const fetchLoans = async () => {
  loading.value = true
  loans.value = []
  try {
    const params = {
      search: search.value,
      status: statusFilter.value
    }
    const res = await api.get('loans/', { params })
    loans.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
    swal.error('Erro', 'Erro ao buscar empréstimos.')
  } finally {
    loading.value = false
  }
}

const groupedLoans = computed(() => {
  const groups = {}
  if (!loans.value) return {}
  
  for (const loan of loans.value) {
    const user = loan.user || 'Usuário Desconhecido'
    if (!groups[user]) groups[user] = []
    groups[user].push(loan)
  }
  return groups
})

const approveLoan = async (id) => {
  if (!(await swal.confirm('Aprovar Empréstimo?', 'O prazo começará a contar agora.'))) return
  
  try {
    await api.post(`loans/${id}/approve/`)
    swal.success('Empréstimo Aprovado!')
    fetchLoans()
  } catch (e) {
    swal.error('Erro', 'Erro ao aprovar: ' + (e.response?.data?.detail || e.message))
  }
}

const rejectLoan = async (id) => {
  if (!(await swal.confirm('Rejeitar Solicitação?', 'O livro voltará ao estoque.'))) return
  
  try {
    await api.post(`loans/${id}/reject/`) 
    swal.success('Solicitação Rejeitada')
    fetchLoans()
  } catch (e) {
    swal.error('Erro', 'Erro ao rejeitar.')
  }
}

const markReturned = async (id) => {
  if (!(await swal.confirm('Confirmar Devolução?', 'O livro será marcado como devolvido.'))) return
  
  try {
    await api.post(`loans/${id}/return_book/`)
    swal.success('Livro Devolvido!')
    fetchLoans()
  } catch (e) {
    swal.error('Erro', 'Erro ao devolver.')
  }
}

const payLoan = async (id) => {
    if (!(await swal.confirm('Confirmar Pagamento?', 'A dívida será quitada.'))) return
    
    try {
        await api.post(`loans/${id}/pay/`)
        swal.success('Pagamento Confirmado', 'Multa quitada com sucesso.')
        fetchLoans()
    } catch (e) {
        swal.error('Erro', e.response?.data?.error || 'Erro ao processar pagamento.')
    }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

const formatCurrency = (value) => {
    if (!value) return '-'
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

const translateStatus = (status) => {
  const map = {
    'PENDING': 'Pendente',
    'ACTIVE': 'Ativo',
    'RETURNED': 'Devolvido',
    'OVERDUE': 'Atrasado',
    'REJECTED': 'Rejeitado'
  }
  return map[status] || status
}

onMounted(fetchLoans)
</script>

<style scoped>
.admin-loans-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.view-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 15px; }
.subtitle { color: #666; font-size: 0.9rem; margin-top: 5px; }

.actions { display: flex; gap: 10px; }
.search-box { display: flex; }
.search-box input { padding: 8px; border: 1px solid #ddd; border-radius: 4px 0 0 4px; outline: none; }
.search-box button { background: #2c3e50; color: white; border: none; padding: 0 15px; border-radius: 0 4px 4px 0; cursor: pointer; }
.status-select { padding: 8px; border: 1px solid #ddd; border-radius: 4px; background: white; }

.user-group-card { background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 25px; overflow: hidden; }
.group-header { background: #f8f9fa; padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.group-header h3 { margin: 0; color: #2c3e50; font-size: 1.1rem; }
.count-badge { background: #e9ecef; color: #495057; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; font-weight: bold; }

table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 12px 20px; background: #fff; color: #7f8c8d; font-size: 0.85rem; font-weight: 600; border-bottom: 1px solid #eee; }
td { padding: 12px 20px; border-bottom: 1px solid #f8f9fa; vertical-align: middle; color: #34495e; }

.status-badge { padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
.status-badge.PENDING { background: #fff3cd; color: #856404; }
.status-badge.ACTIVE { background: #d4edda; color: #155724; }
.status-badge.RETURNED { background: #d1ecf1; color: #0c5460; }
.status-badge.OVERDUE { background: #f8d7da; color: #721c24; }
.status-badge.REJECTED { background: #f2f2f2; color: #999; text-decoration: line-through; }
.status-badge.paid { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }

.btn-group { display: flex; gap: 5px; margin-top: 5px; }
button { border: none; cursor: pointer; padding: 6px 12px; border-radius: 4px; font-size: 0.85rem; transition: opacity 0.2s; color: white; }
button:hover { opacity: 0.9; }

.btn-approve { background: #27ae60; }
.btn-reject { background: #c0392b; }
.btn-return { background: #2980b9; }
.btn-pay { background: #8e44ad; }

.text-muted { color: #ccc; }
.text-red { color: #e74c3c; }
.text-green { color: #27ae60; }
.font-bold { font-weight: bold; }

.loading-state, .empty-state { padding: 40px; text-align: center; color: #7f8c8d; font-size: 1.1rem; }
</style>
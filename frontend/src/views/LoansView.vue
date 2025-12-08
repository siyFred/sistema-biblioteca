<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../services/api'
import { useAlert } from '../utils/alert'

const swal = useAlert()
const loans = ref([])
const loading = ref(true)
const currentFilter = ref('active')

const fetchLoans = async () => {
  loading.value = true
  loans.value = []
  try {
    const endpoint = currentFilter.value === 'active' ? 'lendo_agora' : 'historico';
    const res = await api.get(`loans/${endpoint}/`)
    loans.value = res.data
  } catch (e) { 
    console.error(e) 
  } finally {
    loading.value = false
  }
}

watch(currentFilter, () => {
    fetchLoans()
})

const isDateOverdue = (dateString) => {
    if (!dateString) return false
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const due = new Date(dateString)
    due.setHours(due.getHours() + 3) 
    return due < today
}

const getStatusLabel = (loan) => {
    if (loan.status === 'RETURNED' && loan.fine_amount > 0 && !loan.paid) {
      return { text: 'Multa Pendente', class: 'badge-fine-pending' }
    }
    if (loan.status === 'PENDING') return { text: 'Aguardando Aprovação', class: 'badge-pending' }
    if (loan.status === 'REJECTED') return { text: 'Rejeitado', class: 'badge-rejected' }
    if (loan.status === 'RETURNED') return { text: 'Devolvido', class: 'badge-returned' }
    if (loan.status === 'OVERDUE') return { text: 'Atrasado', class: 'badge-overdue' }
    if (loan.status === 'ACTIVE' && isDateOverdue(loan.due_date)) {
        return { text: 'Atrasado (Pendente)', class: 'badge-overdue' }
    }
    return { text: 'Em Dia', class: 'badge-active' }
}

const formatDate = (date) => date ? new Date(date).toLocaleDateString('pt-BR') : '-'

const returnBook = async (id) => {
  if(!(await swal.confirm("Confirmar devolução do livro?"))) return
  try {
    await api.post(`loans/${id}/return_book/`)
    swal.success('Livro Devolvido!')
    fetchLoans()
  } catch (e) { 
      swal.error('Erro', 'Erro na devolução') 
  }
}

const payFine = async (loanId) => {
    if (!(await swal.confirm("Confirmar pagamento da multa?"))) return
    try {
        await api.post(`loans/${loanId}/pay/`)
        swal.success('Multa paga com sucesso!')
        fetchLoans()
    } catch (e) {
        swal.error('Erro', 'Não foi possível processar o pagamento.')
    }
}

const renewBook = async (id) => {
  if(!(await swal.confirm("Renovar por mais 7 dias?"))) return
  try {
    await api.post(`loans/${id}/renew_book/`) 
    swal.success('Renovado!')
    fetchLoans()
  } catch (e) { 
      swal.error('Erro', 'Erro ao renovar') 
  }
}

onMounted(fetchLoans)
</script>

<template>
  <div class="loans-container">
    <h2>Meus Livros</h2>

    <div class="tabs">
        <button :class="['tab-btn', { active: currentFilter === 'active' }]" @click="currentFilter = 'active'">
            📚 Lendo Agora
        </button>
        <button :class="['tab-btn', { active: currentFilter === 'history' }]" @click="currentFilter = 'history'">
            📜 Histórico
        </button>
    </div>

    <div v-if="loading" class="loading-state">Carregando...</div>

    <div v-else class="card-list">
      <table v-if="loans.length">
        <thead>
          <tr>
            <th>Livro</th>
            <th>Retirada</th>
            <th>Vencimento</th>
            <th>Multa</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loan in loans" :key="loan.id">
            <td>{{ loan.book_title || 'Livro #' + loan.book }}</td>
            <td>{{ formatDate(loan.loan_date) }}</td>
            
            <td :class="{ 'text-red': getStatusLabel(loan).class === 'badge-overdue' }">
                {{ formatDate(loan.due_date) }}
            </td>
            
            <td>R$ {{ loan.fine_amount || '0.00' }}</td>

            <td>
                <span :class="['badge', getStatusLabel(loan).class]">
                    {{ getStatusLabel(loan).text }}
                </span>
            </td>

            <td class="actions-cell">
              <div v-if="loan.status === 'ACTIVE' || loan.status === 'OVERDUE'" class="btn-group">
                  <button @click="returnBook(loan.id)" class="btn-return" title="Devolver">Devolver</button>
              </div>

              <div v-if="loan.fine_amount > 0 && !loan.paid" class="btn-group">
                  <button @click="payFine(loan.id)" class="btn-pay-fine" title="Pagar Multa">Pagar Multa</button>
              </div>

              <span v-else-if="loan.status === 'PENDING'" class="text-muted">
                  Aguardando bibliotecário...
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-else class="empty-state">
          <p v-if="currentFilter === 'active'">Você não está lendo nenhum livro no momento.</p>
          <p v-else>Seu histórico de empréstimos está vazio.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.loans-container { max-width: 900px; margin: 0 auto; padding: 20px; }
.tabs { display: flex; gap: 15px; margin-bottom: 20px; border-bottom: 1px solid #ddd; }
.tab-btn { 
    background: none; border: none; padding: 10px 20px; 
    font-size: 1rem; cursor: pointer; color: #666; 
    border-bottom: 3px solid transparent; transition: all 0.3s;
}
.tab-btn:hover { background-color: #f9f9f9; }
.tab-btn.active { color: #2c3e50; border-bottom-color: #42b983; font-weight: bold; }

.card-list { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 12px; background: #f8f9fa; color: #666; font-weight: 600; }
td { padding: 12px; border-bottom: 1px solid #eee; vertical-align: middle; }

.badge { padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; }
.badge-active { background: #d4edda; color: #155724; }
.badge-overdue { background: #f8d7da; color: #721c24; }
.badge-returned { background: #e2e3e5; color: #383d41; }
.badge-pending { background: #fff3cd; color: #856404; }
.badge-fine-pending { background: #fca103; color: white; }


.badge-rejected { 
    background: rgba(255, 0, 0, 0.1);
    color: #d32f2f;
    border: 1px solid rgba(255, 0, 0, 0.15);
}

.btn-group { display: inline-block; margin-right: 5px; }

.btn-return { background: #3498db; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
.btn-return:hover { background: #2980b9; }
.btn-pay-fine { background: #27ae60; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
.btn-pay-fine:hover { background: #229954; }

.text-red { color: #dc3545; }
.text-muted { color: #999; font-style: italic; font-size: 0.9rem; }
.loading-state, .empty-state { text-align: center; padding: 40px; color: #666; }
</style>
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router' 
import api from '../services/api'
import { useAlert } from '../utils/alert'

const swal = useAlert()
const router = useRouter() 
const requests = ref([])
const loading = ref(true)
const activeTab = ref('PENDING') 

const fetchRequests = async () => {
    try {
        loading.value = true;
        const res = await api.get('books/requests/')
        requests.value = res.data
    } catch (e) {
        swal.error('Erro', 'Erro ao carregar sugestões.')
    } finally {
        loading.value = false
    }
}

// --- LÓGICA DE AGRUPAMENTO CENTRAL ---
const groupedRequests = computed(() => {
    const groups = {};
    for (const req of requests.value) {
        // Chave baseada em status + livro (Título, Autor e ISBN)
        const key = `${req.status}-${req.title}-${req.author}-${req.isbn}`;
        
        if (!groups[key]) {
            groups[key] = {
                ...req,
                request_count: 0,
                request_ids: [],
            };
        }
        groups[key].request_count += 1;
        groups[key].request_ids.push(req.id);
    }
    return Object.values(groups);
});


const groupedPendingRequests = computed(() => groupedRequests.value.filter(r => r.status === 'PENDING'));
const groupedApprovedRequests = computed(() => groupedRequests.value.filter(r => r.status === 'APPROVED'));
const groupedRejectedRequests = computed(() => groupedRequests.value.filter(r => r.status === 'REJECTED'));


// --- FUNÇÕES DE AÇÃO ---

const updateStatus = async (group, status) => {
    try {
        const totalRequests = group.request_ids.length;
        
        // Itera e envia PATCH para todos os pedidos no grupo
        for (const reqId of group.request_ids) {
            await api.patch(`books/requests/${reqId}/`, { status });
        }
        
        // Força o recarregamento, garantindo que o status mude de aba imediatamente
        await fetchRequests();
        
        // Opcional: Muda a aba para onde o item foi
        if (status === 'APPROVED' || status === 'REJECTED') {
             activeTab.value = status; 
        }
        
        swal.success('Sucesso', `${totalRequests} pedidos para '${group.title}' atualizados para ${status}.`);
    } catch (e) {
        swal.error('Erro', 'Falha ao atualizar o(s) pedido(s).');
    }
}

const cadastrarLivro = (req) => {
    router.push({
        name: 'new-book',
        query: {
            title: req.title,
            author: req.author,
            isbn: req.isbn
        }
    })
}

const formatDate = (d) => new Date(d).toLocaleDateString('pt-BR')

onMounted(fetchRequests)
</script>

<template>
  <div class="page">
    
    <div class="header-no-controls">
        <h1>💡 Gestão de Sugestões</h1>
    </div>
    
    <div class="tabs">
        <button 
            :class="{ active: activeTab === 'PENDING' }" 
            @click="activeTab = 'PENDING'"
        >Pendentes ({{ groupedPendingRequests.length }})</button>
        
        <button 
            :class="{ active: activeTab === 'APPROVED' }" 
            @click="activeTab = 'APPROVED'"
        >Aprovados ({{ groupedApprovedRequests.length }})</button>

        <button 
            :class="{ active: activeTab === 'REJECTED' }" 
            @click="activeTab = 'REJECTED'"
        >Rejeitados ({{ groupedRejectedRequests.length }})</button>
    </div>

    <div v-if="loading">Carregando...</div>

    <div v-else-if="activeTab === 'PENDING'">
        <table v-if="groupedPendingRequests.length > 0">
            <thead><tr><th>Livro</th><th>Total Pedidos</th><th>Ações</th></tr></thead>
            <tbody>
                <tr v-for="group in groupedPendingRequests" :key="group.title + group.author">
                    <td><strong>{{ group.title }}</strong><br><small>{{ group.author }}</small></td>
                    <td><span class="badge-count">{{ group.request_count }}</span> pessoa(s)</td>
                    <td>
                        <button @click="updateStatus(group, 'APPROVED')" class="btn-ok">Aprovar Todos</button>
                        <button @click="updateStatus(group, 'REJECTED')" class="btn-no">Rejeitar Todos</button>
                    </td>
                </tr>
            </tbody>
        </table>
        <p v-else class="empty">Nenhuma solicitação pendente.</p>
    </div>

    <div v-else-if="activeTab === 'APPROVED'">
        <table v-if="groupedApprovedRequests.length > 0">
            <thead><tr><th>Livro Aprovado</th><th>Pedidos</th><th>Ação</th></tr></thead>
            <tbody>
                <tr v-for="group in groupedApprovedRequests" :key="group.title + group.author">
                    <td>
                        <strong>{{ group.title }}</strong><br>
                        <small>{{ group.author }} - ISBN: {{ group.isbn || 'N/A' }}</small>
                    </td>
                    <td><span class="badge-count">{{ group.request_count }}</span></td>
                    <td>
                        <button @click="cadastrarLivro(group)" class="btn-register">
                            ➕ Cadastrar no Acervo
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
        <p v-else class="empty">Nenhum livro aprovado aguardando cadastro.</p>
    </div>

    <div v-else-if="activeTab === 'REJECTED'">
        <table v-if="groupedRejectedRequests.length > 0">
            <thead><tr><th>Livro Rejeitado</th><th>Motivo</th><th>Data da Última Ação</th></tr></thead>
            <tbody>
                <tr v-for="group in groupedRejectedRequests" :key="group.title + group.author">
                    <td>
                        <strong>{{ group.title }}</strong><br>
                        <small>{{ group.author }}</small>
                    </td>
                    <td>Rejeitado por Administrador</td>
                    <td>{{ formatDate(group.created_at) }}</td>
                </tr>
            </tbody>
        </table>
        <p v-else class="empty">Nenhum livro foi rejeitado.</p>
    </div>

  </div>
</template>

<style scoped>
.page { max-width: 1000px; margin: 0 auto; padding: 20px; }
.header-no-controls { display: flex; justify-content: flex-start; align-items: center; margin-bottom: 20px; }

.tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #eee; }
.tabs button { background: none; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; color: #7f8c8d; border-bottom: 3px solid transparent; }
.tabs button.active { color: #2c3e50; border-bottom-color: #3498db; }
.tabs button:hover { color: #3498db; }

table { width: 100%; border-collapse: collapse; background: white; margin-top: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
th, td { padding: 15px; border-bottom: 1px solid #eee; text-align: left; }
th { background: #f8f9fa; }

.badge-count { background: #e0f7fa; color: #00bcd4; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.9rem; margin-right: 5px; }

button { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; color: white; margin-right: 5px; }
.btn-ok { background: #27ae60; }
.btn-no { background: #c0392b; }
.btn-register { background: #2980b9; font-weight: bold; }
.btn-register:hover { background: #3498db; }
.empty { text-align: center; color: #999; margin-top: 30px; }
</style>
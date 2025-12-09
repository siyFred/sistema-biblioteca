<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '../services/api'
import { useAlert } from '../utils/alert'
import Swal from 'sweetalert2'

const swal = useAlert()
const books = ref([])
const loading = ref(true)
const search = ref('')

// Paginação e Filtros
const currentPage = ref(1)
const totalPages = ref(1)

const fetchBooks = async () => {
    loading.value = true
    try {
        const { data } = await api.get('books/', {
            params: {
                search: search.value,
                page: currentPage.value
            }
        })
        books.value = data.results || data
        // Assumindo paginação do DRF
        totalPages.value = Math.ceil((data.count || books.value.length) / 20)
    } catch (e) {
        swal.error('Erro', 'Falha ao carregar acervo.')
    } finally {
        loading.value = false
    }
}

const deleteBook = async (id, title) => {
    if(!(await swal.confirm('Excluir?', `Tem certeza que deseja apagar "${title}"?`))) return
    
    try {
        await api.delete(`books/${id}/`)
        swal.success('Apagado!', 'O livro foi removido do acervo.')
        fetchBooks()
    } catch (e) {
        swal.error('Erro', 'Não foi possível excluir este livro. Verifique se há empréstimos ativos.')
    }
}

// Debounce da busca
let timeout
watch(search, () => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
        currentPage.value = 1
        fetchBooks()
    }, 500)
})

onMounted(fetchBooks)
</script>

<template>
  <div class="manage-books-page">
    <div class="page-header">
        <div>
            <h2>📚 Gestão de Acervo</h2>
            <p>Controle total sobre o inventário da biblioteca.</p>
        </div>
        <router-link to="/books/new" class="btn btn-primary">
            + Novo Livro
        </router-link>
    </div>

    <div class="toolbar card">
        <input 
            v-model="search" 
            placeholder="🔍 Buscar por título, autor ou ISBN..." 
            class="input search-input"
        />
    </div>

    <div v-if="loading" class="loading">Carregando acervo...</div>

    <div v-else class="table-container card">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Capa</th>
                    <th>Título / Autor</th>
                    <th>ISBN</th>
                    <th>Estoque</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="book in books" :key="book.id">
                    <td>
                        <img 
                            :src="book.cover_url || book.cover_image || 'https://via.placeholder.com/40'" 
                            class="mini-cover" 
                        />
                    </td>
                    <td>
                        <div class="book-info">
                            <strong>{{ book.title }}</strong>
                            <span>{{ book.author }}</span>
                        </div>
                    </td>
                    <td><span class="isbn-tag">{{ book.isbn }}</span></td>
                    <td>
                        <div class="stock-badge" :class="book.available_copies > 0 ? 'instock' : 'outstock'">
                            {{ book.available_copies }} / {{ book.total_copies }}
                        </div>
                    </td>
                    <td class="actions-cell">
                        <router-link :to="`/books/${book.id}`" class="btn-icon" title="Ver Detalhes">👁️</router-link>
                        <router-link :to="`/books/${book.id}/edit`" class="btn-icon" title="Editar">✏️</router-link>
                        <button @click="deleteBook(book.id, book.title)" class="btn-icon delete" title="Excluir">🗑️</button>
                    </td>
                </tr>
                <tr v-if="books.length === 0">
                    <td colspan="5" class="empty-state">Nenhum livro encontrado.</td>
                </tr>
            </tbody>
        </table>
    </div>
  </div>
</template>

<style scoped>
.manage-books-page { padding: 30px; max-width: 1200px; margin: 0 auto; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.page-header h2 { margin: 0; color: var(--primary); font-size: 1.8rem; }
.page-header p { margin: 5px 0 0; color: var(--text-muted); }

.toolbar { padding: 15px; margin-bottom: 20px; display: flex; gap: 15px; }
.search-input { flex: 1; max-width: 400px; }

.table-container { overflow-x: auto; padding: 0; border-radius: 8px; box-shadow: var(--shadow-sm); }
.data-table { width: 100%; border-collapse: collapse; }

.data-table th { 
    background: #f8f9fa; color: var(--text-muted); 
    padding: 15px; text-align: left; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; 
    border-bottom: 2px solid #e9ecef;
}

.data-table td { padding: 12px 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: var(--text-main); }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover { background: #f8f9fa; }

.mini-cover { width: 40px; height: 55px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }

.book-info { display: flex; flex-direction: column; }
.book-info strong { font-size: 0.95rem; color: var(--primary); }
.book-info span { font-size: 0.85rem; color: var(--text-muted); }

.isbn-tag { background: #eef2f7; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 0.85rem; color: #555; }

.stock-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
.stock-badge.instock { background: rgba(39, 174, 96, 0.1); color: #27ae60; }
.stock-badge.outstock { background: rgba(231, 76, 60, 0.1); color: #c0392b; }

.actions-cell { display: flex; gap: 10px; }
.btn-icon { background: none; border: none; font-size: 1.2rem; cursor: pointer; padding: 5px; transition: 0.2s; text-decoration: none; border-radius: 4px; }
.btn-icon:hover { background: rgba(0,0,0,0.05); transform: scale(1.1); }
.btn-icon.delete:hover { background: rgba(231, 76, 60, 0.1); }

.empty-state { text-align: center; padding: 40px; color: var(--text-muted); font-style: italic; }
.loading { text-align: center; padding: 40px; font-size: 1.1rem; color: var(--text-muted); }

@media (max-width: 768px) {
    .page-header { flex-direction: column; align-items: flex-start; gap: 15px; }
    .data-table th:nth-child(3), .data-table td:nth-child(3) { display: none; } /* Hide ISBN on mobile */
}
</style>

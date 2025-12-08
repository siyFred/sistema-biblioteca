<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import api from '../services/api'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useAlert } from '../utils/alert'

const swal = useAlert()
const router = useRouter()
const auth = useAuthStore() 

const books = ref([])
const search = ref('')
const page = ref(1)
const loading = ref(false)
const hasMore = ref(true)
const sentinel = ref(null)
const BASE_URL = 'http://127.0.0.1:8000'

// --- FILTROS (AGORA NO MODAL) ---
const showFilterModal = ref(false)
const selectedGenre = ref('ALL') 
const minYear = ref('')
const maxYear = ref('')
const sortBy = ref('-created_at') // Padrão: Mais recentes

// --- FILTRO RÁPIDO ---
const onlyAvailable = ref(false)

// --- ESTADO DO MODAL (GOOGLE BOOKS) ---
const showModal = ref(false) // Google
const googleSearch = ref('')
const googleBooks = ref([])
const loadingGoogle = ref(false)

const GENRES = [
    { value: 'ALL', label: 'Todos os Gêneros' },
    { value: 'fiction', label: 'Ficção / Fantasia' },
    { value: 'romance', label: 'Romance' },
    { value: 'horror', label: 'Terror / Horror' },
    { value: 'history', label: 'História' },
    { value: 'computers', label: 'Tecnologia' },
    { value: 'science', label: 'Ciência' },
    { value: 'biography', label: 'Biografia' },
]

const SORT_OPTIONS = [
    { value: '-created_at', label: '🌟 Mais Recentes' },
    { value: 'title', label: '🔤 Título (A-Z)' },
    { value: '-publication_date', label: '📅 Ano (Mais novos)' },
    { value: 'publication_date', label: '📅 Ano (Mais antigos)' },
]

// --- BUSCA LOCAL (PADRÃO) ---
const fetchBooks = async (isLoadMore = false) => {
  if (loading.value) return
  if (isLoadMore && !hasMore.value) return 

  loading.value = true
  
  try {
    if (!isLoadMore) {
        page.value = 1
        books.value = []
        hasMore.value = true
    }

    const params = {
        q: search.value,
        page: page.value,
        genre: selectedGenre.value,
        source: 'local',
        available: onlyAvailable.value,
        min_year: minYear.value,
        max_year: maxYear.value,
        ordering: sortBy.value 
    }

    const res = await api.get('books/search-global/', { params })
    const newBooks = res.data

    if (newBooks.length === 0) {
        hasMore.value = false 
    } else {
        const existingIds = new Set(books.value.map(b => b.id))
        const filteredNewBooks = newBooks.filter(b => !existingIds.has(b.id))
        books.value = [...books.value, ...filteredNewBooks]
        
        if (newBooks.length < 40) hasMore.value = false
        else page.value++ 
    }

  } catch (e) { 
    console.error(e)
    swal.error("Erro", "Falha ao carregar acervo.")
  } finally { 
    loading.value = false 
  }
}

const applyFilters = () => {
    showFilterModal.value = false
    fetchBooks(false)
}

// --- BUSCA GOOGLE (MODAL) ---
const fetchGoogleBooks = async () => {
    if (!googleSearch.value) return
    loadingGoogle.value = true
    try {
        const { data } = await api.get('books/search-global/', {
            params: { q: googleSearch.value, source: 'google' }
        })
        googleBooks.value = data
    } catch (e) {
        console.error(e)
        swal.error("Erro", "Falha ao buscar no Google Books.")
    } finally {
        loadingGoogle.value = false
    }
}

// Watch apenas no filtro rápido
watch(onlyAvailable, () => { fetchBooks(false) })

let observer = null
const createObserver = () => {
    if (!('IntersectionObserver' in window)) return
    observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && hasMore.value && !loading.value) {
                fetchBooks(true)
            }
        })
    }, { root: null, rootMargin: '200px', threshold: 0.1 })
    if (sentinel.value) observer.observe(sentinel.value)
}

onMounted(() => {
    fetchBooks(false)
    createObserver()
})

onUnmounted(() => {
    if (observer) observer.disconnect()
})

const rentBook = async (book, event) => {
  event.stopPropagation() 
  if (book.available_copies <= 0) return swal.error('Esgotado', 'Sem estoque.')
  if (!(await swal.confirm(`Reservar '${book.title}'?`, 'Confirmar?'))) return
  try {
    await api.post('loans/', { book: book.id })
    book.status_usuario = 'solicitado'
    swal.success("Sucesso!", "Aguarde aprovação.")
  } catch (e) { swal.error("Erro", e.response?.data?.detail || "Erro.") }
}

const suggestPurchase = async (book) => {
    if (!(await swal.confirm(`Sugerir Compra?`, `Pedir '${book.title}' para a biblioteca?`))) return
    try {
        await api.post('books/request-purchase/', {
            title: book.title, author: book.author, isbn: book.isbn
        })
        swal.success("Enviado!", "O bibliotecário analisará seu pedido.")
        showModal.value = false
    } catch (e) { swal.error("Erro", "Falha ao enviar.") }
}

const getCover = (book) => {
  if (book.cover_url) return book.cover_url 
  if (book.cover_image) return book.cover_image.startsWith('http') ? book.cover_image : `${BASE_URL}${book.cover_image}`
  return 'https://via.placeholder.com/150x220?text=Sem+Capa'
}

const canRent = (book) => {
    return !['solicitado', 'alugado'].includes(book.status_usuario) && book.available_copies > 0
}

const goToDetail = (book) => {
    router.push({ name: 'book-detail', params: { id: book.id } })
}
</script>

<template>
  <div class="page-container">
    <div class="header">
      <h1>📖 Acervo da Biblioteca</h1>
      <router-link v-if="auth.isLibrarian" to="/books/new" class="btn-add">+ Novo Livro</router-link>
    </div>

    <div class="controls-section">
        <div class="search-bar">
            <input 
                v-model="search" 
                @keyup.enter="fetchBooks(false)" 
                placeholder="Pesquise no nosso acervo..." 
            />
            <button @click="fetchBooks(false)">🔍</button>
        </div>

        <button @click="showFilterModal = true" class="btn-filter">
            ⚡ Filtrar / Ordenar
        </button>

        <label class="checkbox-label">
            <input type="checkbox" v-model="onlyAvailable">
            Só Disponíveis
        </label>
    </div>

    <div class="grid">
      <div 
        v-for="(book, index) in books" 
        :key="book.id" 
        class="book-card"
        @click="goToDetail(book)" 
      >
        <div class="card-badges">
            <span v-if="book.status_usuario === 'solicitado'" class="badge badge-yellow">⏳ Aguardando</span>
            <span v-else-if="book.status_usuario === 'alugado'" class="badge badge-green">📖 Lendo</span>
        </div>

        <div class="image-wrapper">
            <img :src="getCover(book)" class="cover" :alt="book.title" />
        </div>

        <div class="info">
          <h3>{{ book.title }}</h3>
          <p class="author">{{ book.author }}</p>
          
          <div class="actions">
                <span class="stock" :class="{ 'red': book.available_copies === 0 }">{{ book.available_copies }} disp.</span>
                <div v-if="!auth.isLibrarian" @click.stop>
                    <button v-if="canRent(book)" @click="rentBook(book, $event)" class="btn-rent">Alugar</button>
                    <button v-else-if="book.available_copies === 0" disabled class="btn-rent disabled">Esgotado</button>
                    <span v-else class="status-text">Indisponível</span>
                </div>
                <button v-if="auth.isLibrarian" @click.stop="$router.push(`/books/${book.id}/edit`)" class="btn-edit-small">✏️</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-bar">Buscando...</div>
    <div v-if="!loading && books.length === 0" class="empty-state">
        Nenhum livro encontrado no acervo físico.
    </div>

    <div class="suggestion-banner" v-if="!loading">
        <p>Não encontrou o que queria?</p>
        <button @click="showModal = true" class="btn-external">
            🌎 Buscar em Outras Bibliotecas 
        </button>
    </div>

    <div ref="sentinel" class="infinite-sentinel"></div>

    <!-- MODAL DE FILTROS -->
    <div v-if="showFilterModal" class="modal-overlay" @click.self="showFilterModal = false">
        <div class="modal-content narrow">
            <div class="modal-header">
                <h2>⚡ Configurar Busca</h2>
                <button class="close-btn" @click="showFilterModal = false">&times;</button>
            </div>

            <div class="filter-section">
                <h3>Ordenação</h3>
                <div class="radio-group">
                    <label v-for="opt in SORT_OPTIONS" :key="opt.value" class="radio-label">
                        <input type="radio" v-model="sortBy" :value="opt.value">
                        {{ opt.label }}
                    </label>
                </div>
            </div>

            <div class="filter-section">
                <h3>Gênero</h3>
                <select v-model="selectedGenre" class="full-select">
                    <option v-for="g in GENRES" :key="g.value" :value="g.value">
                        {{ g.label }}
                    </option>
                </select>
            </div>

            <div class="filter-section">
                <h3>Ano de Publicação</h3>
                <div class="row">
                    <input v-model="minYear" type="number" placeholder="De (Ano)" class="year-input">
                    <input v-model="maxYear" type="number" placeholder="Até (Ano)" class="year-input">
                </div>
            </div>

            <button @click="applyFilters" class="btn-apply">Aplicar Filtros</button>
        </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
            <div class="modal-header">
                <h2>🌎 Buscar na Rede Externa</h2>
                <button class="close-btn" @click="showModal = false">&times;</button>
            </div>
            
            <div class="external-search-box">
                <input 
                    v-model="googleSearch" 
                    placeholder="Digite o nome do livro ou autor..." 
                    @keyup.enter="fetchGoogleBooks"
                />
                <button @click="fetchGoogleBooks">Buscar</button>
            </div>

            <div class="results-list">
                <div v-if="loadingGoogle" class="loading-google">Carregando sugestões...</div>
                
                <div v-else-if="googleBooks.length > 0" class="google-grid">
                    <div v-for="book in googleBooks" :key="book.google_id" class="google-item">
                        <img :src="book.cover_url || 'https://via.placeholder.com/80x120'" class="mini-cover" />
                        <div class="google-info">
                            <h4>{{ book.title }}</h4>
                            <p>{{ book.author }}</p>
                            <button @click="suggestPurchase(book)" class="btn-request">💡 Solicitar Compra</button>
                        </div>
                    </div>
                </div>

                <div v-else-if="googleSearch && !loadingGoogle" class="empty-google">
                    Nenhum resultado externo encontrado.
                </div>
            </div>
        </div>
    </div>
    
  </div>
</template>

<style scoped>
.page-container { padding-bottom: 50px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.btn-add { background: #2c3e50; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; }

.controls-section { display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; align-items: center; }
.search-bar { flex: 2; display: flex; gap: 5px; min-width: 300px; }
.search-bar input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; }
.search-bar button { padding: 0 20px; background: #3498db; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1.2rem; }

.btn-filter { background: #ecf0f1; border: 1px solid #bdc3c7; color: #2c3e50; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; white-space: nowrap; }
.btn-filter:hover { background: #dfe6e9; border-color: #95a5a6; }

.checkbox-label { display: flex; align-items: center; gap: 5px; font-weight: bold; font-size: 0.9rem; color: #2c3e50; cursor: pointer; user-select: none; }
.checkbox-label input { width: 18px; height: 18px; cursor: pointer; }

/* ESTILOS DO MODAL DE FILTROS */
.modal-content.narrow { max-width: 400px; }
.filter-section { margin-bottom: 25px; }
.filter-section h3 { font-size: 1rem; color: #7f8c8d; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
.radio-group { display: flex; flex-direction: column; gap: 10px; }
.radio-label { display: flex; gap: 10px; align-items: center; cursor: pointer; font-size: 0.95rem; color: #2c3e50; }
.full-select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
.row { display: flex; gap: 10px; }
.year-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }
.btn-apply { width: 100%; background: #2c3e50; color: white; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 1rem; }
.btn-apply:hover { background: #42b883; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 25px; margin-bottom: 40px; }

.book-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08); cursor: pointer; transition: transform 0.2s; position: relative; border: 1px solid transparent; }
.book-card:hover { transform: translateY(-5px); box-shadow: 0 6px 15px rgba(0,0,0,0.12); }

.card-badges { position: absolute; top: 10px; right: 10px; z-index: 10; display: flex; flex-direction: column; gap: 5px; align-items: flex-end; }
.badge { padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.badge-yellow { background: #f1c40f; color: #fff; }
.badge-green { background: #27ae60; color: #fff; }

.image-wrapper { height: 260px; overflow: hidden; background: #f0f0f0; display: flex; align-items: center; justify-content: center; }
.cover { width: 100%; height: 100%; object-fit: cover; }

.info { padding: 15px; }
.info h3 { margin: 0 0 5px 0; font-size: 1rem; color: #2c3e50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.author { font-size: 0.85rem; color: #7f8c8d; margin-bottom: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.actions { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
.stock { font-weight: bold; color: #27ae60; font-size: 0.8rem; }
.stock.red { color: #e74c3c; }

.btn-rent { background: #2c3e50; color: white; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; transition: background 0.2s; }
.btn-rent:hover { background: #42b883; }
.btn-rent.disabled { background: #ccc; cursor: not-allowed; }
.btn-edit-small { background: #f39c12; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }

.suggestion-banner {
    background: #eef2f5; border: 1px dashed #bdc3c7; border-radius: 8px; padding: 20px; text-align: center; margin-top: 20px; grid-column: 1 / -1;
}
.suggestion-banner p { font-size: 1.1rem; color: #2c3e50; font-weight: bold; margin-bottom: 10px; }
.btn-external { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; margin-bottom: 5px; font-size: 1rem; transition: 0.2s; }
.btn-external:hover { background: #2980b9; transform: scale(1.05); }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeIn 0.3s; }
.modal-content { background: white; padding: 25px; border-radius: 12px; width: 90%; max-width: 600px; max-height: 85vh; overflow-y: auto; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #7f8c8d; }

.external-search-box { display: flex; gap: 10px; margin-bottom: 20px; }
.external-search-box input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 6px; }
.external-search-box button { padding: 0 20px; background: #2c3e50; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }

.google-grid { display: flex; flex-direction: column; gap: 15px; }
.google-item { display: flex; gap: 15px; border-bottom: 1px solid #f0f0f0; padding-bottom: 15px; align-items: center; }
.mini-cover { width: 60px; height: 90px; object-fit: cover; border-radius: 4px; background: #eee; }
.google-info { flex: 1; }
.google-info h4 { margin: 0 0 5px 0; color: #2c3e50; font-size: 1rem; }
.google-info p { margin: 0 0 10px 0; color: #7f8c8d; font-size: 0.85rem; }
.btn-request { background: #e67e22; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.85rem; }
.btn-request:hover { background: #d35400; }

.loading-bar, .loading-google { text-align: center; padding: 20px; color: #999; }
.empty-state, .empty-google { text-align: center; padding: 20px; color: #999; }
.infinite-sentinel { height: 10px; }
</style>

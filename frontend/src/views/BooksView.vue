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
      <h1 class="page-title">📖 Acervo da Biblioteca</h1>
      <router-link v-if="auth.isLibrarian" to="/books/new" class="btn btn-primary">+ Novo Livro</router-link>
    </div>

    <div class="controls-section card">
        <div class="search-bar">
            <input 
                v-model="search" 
                @keyup.enter="fetchBooks(false)" 
                class="input search-input"
                placeholder="Pesquise no nosso acervo..." 
            />
            <button @click="fetchBooks(false)" class="btn btn-primary">🔍</button>
        </div>

        <button @click="showFilterModal = true" class="btn btn-outline">
            ⚡ Filtrar / Ordenar
        </button>

        <label class="checkbox-label">
            <input type="checkbox" v-model="onlyAvailable">
            <span class="ml-2">Só Disponíveis</span>
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
            <span v-if="book.status_usuario === 'solicitado'" class="badge badge-warning">⏳ Aguardando</span>
            <span v-else-if="book.status_usuario === 'alugado'" class="badge badge-success">📖 Lendo</span>
        </div>

        <div class="image-wrapper">
            <img :src="getCover(book)" class="cover" :alt="book.title" />
            <div class="overlay">
                <span class="view-details">Ver Detalhes</span>
            </div>
        </div>

        <div class="info">
          <h3 :title="book.title">{{ book.title }}</h3>
          <p class="author">{{ book.author }}</p>
          
          <div class="actions">
                <span class="stock" :class="{ 'text-danger': book.available_copies === 0 }">
                    {{ book.available_copies }} disp.
                </span>
                
                <div v-if="!auth.isLibrarian" @click.stop>
                    <button v-if="canRent(book)" @click="rentBook(book, $event)" class="btn btn-sm btn-primary">Alugar</button>
                    <button v-else-if="book.available_copies === 0" disabled class="btn btn-sm btn-disabled">Esgotado</button>
                    <span v-else class="status-text">Indisponível</span>
                </div>
                
                <button 
                    v-if="auth.isLibrarian" 
                    @click.stop="$router.push(`/books/${book.id}/edit`)" 
                    class="btn btn-sm btn-outline icon-btn"
                >
                    ✏️
                </button>
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
        <button @click="showModal = true" class="btn btn-accent">
            🌎 Buscar em Outras Bibliotecas 
        </button>
    </div>

    <div ref="sentinel" class="infinite-sentinel"></div>

    <!-- MODAL DE FILTROS -->
    <Transition name="modal">
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
                    <select v-model="selectedGenre" class="input full-select">
                        <option v-for="g in GENRES" :key="g.value" :value="g.value">
                            {{ g.label }}
                        </option>
                    </select>
                </div>

                <div class="filter-section">
                    <h3>Ano de Publicação</h3>
                    <div class="row">
                        <input v-model="minYear" type="number" placeholder="De (Ano)" class="input year-input">
                        <input v-model="maxYear" type="number" placeholder="Até (Ano)" class="input year-input">
                    </div>
                </div>

                <button @click="applyFilters" class="btn btn-primary w-full">Aplicar Filtros</button>
            </div>
        </div>
    </Transition>

    <Transition name="modal">
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
                        class="input"
                    />
                    <button @click="fetchGoogleBooks" class="btn btn-primary">Buscar</button>
                </div>

                <div class="results-list">
                    <div v-if="loadingGoogle" class="loading-google">Carregando sugestões...</div>
                    
                    <div v-else-if="googleBooks.length > 0" class="google-grid">
                        <div v-for="book in googleBooks" :key="book.google_id" class="google-item card">
                            <img :src="book.cover_url || 'https://via.placeholder.com/80x120'" class="mini-cover" />
                            <div class="google-info">
                                <h4>{{ book.title }}</h4>
                                <p>{{ book.author }}</p>
                                <button @click="suggestPurchase(book)" class="btn btn-sm btn-accent">💡 Solicitar Compra</button>
                            </div>
                        </div>
                    </div>

                    <div v-else-if="googleSearch && !loadingGoogle" class="empty-google">
                        Nenhum resultado externo encontrado.
                    </div>
                </div>
            </div>
        </div>
    </Transition>
    
  </div>
</template>

<style scoped>
.page-container { padding-bottom: 60px; }

.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
.page-title { font-size: 1.8rem; font-weight: 800; color: var(--primary); margin: 0; }

.controls-section { 
    display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; align-items: center; 
    background: white; padding: 20px; border-radius: var(--radius-md); box-shadow: var(--shadow-sm); 
}

.search-bar { flex: 2; display: flex; gap: 10px; min-width: 300px; }
.search-input { border-radius: 50px; padding-left: 20px; }

.checkbox-label { display: flex; align-items: center; font-weight: 600; font-size: 0.95rem; color: var(--text-main); cursor: pointer; user-select: none; }
.checkbox-label input { width: 18px; height: 18px; cursor: pointer; accent-color: var(--accent); }
.ml-2 { margin-left: 8px; }

/* GRID LIVROS */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 30px; margin-bottom: 50px; }

.book-card { 
    background: white; 
    border-radius: var(--radius-md); 
    overflow: hidden; 
    box-shadow: var(--shadow-sm); 
    cursor: pointer; 
    transition: all 0.3s ease; 
    border: 1px solid rgba(0,0,0,0.03); 
    position: relative;
    display: flex;
    flex-direction: column;
}

.book-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-lg); }

.card-badges { position: absolute; top: 12px; right: 12px; z-index: 10; display: flex; flex-direction: column; gap: 5px; align-items: flex-end; }
.badge { padding: 5px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-transform: uppercase; letter-spacing: 0.5px; }
.badge-warning { background: var(--warning); color: #fff; }
.badge-success { background: var(--accent); color: #fff; }

.image-wrapper { 
    height: 280px; 
    overflow: hidden; 
    background: #f8f9fa; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    position: relative;
}

.cover { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }
.book-card:hover .cover { transform: scale(1.05); }

/* Overlay no hover da imagem */
.overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(44, 62, 80, 0.4);
    opacity: 0;
    transition: opacity 0.3s;
    display: flex; align-items: center; justify-content: center;
}
.book-card:hover .overlay { opacity: 1; }
.view-details { color: white; font-weight: bold; border: 2px solid white; padding: 8px 16px; border-radius: 20px; backdrop-filter: blur(2px); }

.info { padding: 18px; display: flex; flex-direction: column; flex: 1; }
.info h3 { margin: 0 0 6px 0; font-size: 1.05rem; color: var(--text-main); font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.author { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.actions { margin-top: auto; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
.stock { font-weight: 700; color: var(--accent); font-size: 0.8rem; background: rgba(66, 184, 131, 0.1); padding: 4px 8px; border-radius: 4px; }
.stock.text-danger { color: var(--danger); background: rgba(231, 76, 60, 0.1); }

.btn-sm { padding: 6px 14px; font-size: 0.8rem; }
.btn-disabled { background: #e0e0e0; color: #999; cursor: not-allowed; border: none; }
.icon-btn { padding: 6px 10px; }

/* SUGGESTION BANNER */
.suggestion-banner {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
    border-radius: var(--radius-md); 
    padding: 30px; 
    text-align: center; 
    margin-top: 20px;
    border: 1px solid rgba(0,0,0,0.05);
}
.suggestion-banner p { font-size: 1.2rem; color: var(--text-main); font-weight: 600; margin-bottom: 15px; }

/* MODAL OVERRIDES */
.modal-content.narrow { max-width: 400px; }

</style>

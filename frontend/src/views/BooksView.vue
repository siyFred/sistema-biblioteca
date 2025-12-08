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
const selectedGenre = ref('ALL') 
const page = ref(1)
const loading = ref(false)
const hasMore = ref(true)
const sentinel = ref(null)
const BASE_URL = 'http://127.0.0.1:8000'

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
        genre: selectedGenre.value
    }

    const res = await api.get('books/search-global/', { params })
    const newBooks = res.data

    if (newBooks.length === 0) {
        hasMore.value = false 
    } else {
        const existingIds = new Set(books.value.map(b => b.id || b.google_id))
        const filteredNewBooks = newBooks.filter(b => !existingIds.has(b.id || b.google_id))
        
        books.value = [...books.value, ...filteredNewBooks]
        
        if (newBooks.length < 10) hasMore.value = false
        else page.value++ 
    }

  } catch (e) { 
    console.error(e)
    swal.error("Erro", "Falha ao carregar livros.")
  } finally { 
    loading.value = false 
  }
}

watch(selectedGenre, () => { fetchBooks(false) })

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

const suggestPurchase = async (book, event) => {
    event.stopPropagation()
    if (!(await swal.confirm(`Sugerir Compra?`, `Pedir '${book.title}'?`))) return
    try {
        await api.post('books/request-purchase/', {
            title: book.title, author: book.author, isbn: book.isbn
        })
        swal.success("Enviado!", "Pedido registrado.")
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
    if (book.is_google) {
        router.push({ 
            name: 'google-book-detail', 
            params: { googleId: book.google_id } 
        })
    } else {
        router.push({ 
            name: 'book-detail', 
            params: { id: book.id } 
        })
    }
}
</script>

<template>
  <div>
    <div class="header">
      <h1>📖 Acervo & Descoberta</h1>
      <router-link v-if="auth.isLibrarian" to="/books/new" class="btn-add">+ Novo Livro</router-link>
    </div>

    <div class="controls-section">
        <div class="search-bar">
            <input 
                v-model="search" 
                @keyup.enter="fetchBooks(false)" 
                placeholder="Pesquise por título, autor..." 
            />
            <button @click="fetchBooks(false)">🔍</button>
        </div>

        <div class="filter-box">
            <select v-model="selectedGenre">
                <option v-for="g in GENRES" :key="g.value" :value="g.value">
                    {{ g.label }}
                </option>
            </select>
        </div>
    </div>

    <div class="grid">
      <div 
        v-for="(book, index) in books" 
        :key="book.id || book.google_id || index" 
        class="book-card"
        :class="{ 'google-card': book.is_google }"
        @click="goToDetail(book)" 
      >
        <div class="card-badges">
            <span v-if="book.is_google" class="badge badge-gray">🌐 Sugestão</span>
            <span v-else-if="book.status_usuario === 'solicitado'" class="badge badge-yellow">⏳ Aguardando</span>
            <span v-else-if="book.status_usuario === 'alugado'" class="badge badge-green">📖 Lendo</span>
            <span v-else class="badge badge-blue">🏠 Acervo</span>
        </div>

        <div class="image-wrapper">
            <img :src="getCover(book)" class="cover" :alt="book.title" />
        </div>

        <div class="info">
          <h3>{{ book.title }}</h3>
          <p class="author">{{ book.author }}</p>
          
          <div class="actions">
            <template v-if="!book.is_google">
                <span class="stock" :class="{ 'red': book.available_copies === 0 }">{{ book.available_copies }} disp.</span>
                <div v-if="!auth.isLibrarian" @click.stop>
                    <button v-if="canRent(book)" @click="rentBook(book, $event)" class="btn-rent">Alugar</button>
                    <button v-else-if="book.available_copies === 0" disabled class="btn-rent disabled">Esgotado</button>
                    <span v-else class="status-text">Indisponível</span>
                </div>
                <button v-if="auth.isLibrarian" @click.stop="$router.push(`/books/${book.id}/edit`)" class="btn-edit-small">✏️</button>
            </template>

            <template v-else>
                <span class="stock red">Externo</span>
                <button @click="suggestPurchase(book, $event)" class="btn-suggest">💡 Pedir</button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- 🔥 OBRIGATÓRIO PARA FUNÇÃO DO INFINITE SCROLL -->
    <div ref="sentinel" class="infinite-sentinel"></div>
    
    <div v-if="loading" class="loading-bar">
        <span class="spinner"></span> Buscando...
    </div>
    
    <div v-if="!loading && books.length === 0" class="empty-state">
        Nenhum livro encontrado.
    </div>
    
  </div>
</template>

<style scoped>
.infinite-sentinel {
  height: 1px;
}
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.btn-add { background: #2c3e50; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; }

.controls-section { display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }
.search-bar { flex: 2; display: flex; gap: 5px; }
.search-bar input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; }
.search-bar button { padding: 0 20px; background: #3498db; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1.2rem; }
.filter-box { flex: 1; min-width: 200px; }
.filter-box select { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; background: white; cursor: pointer; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 25px; }

.book-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08); cursor: pointer; transition: transform 0.2s; position: relative; border: 1px solid transparent; }
.book-card:hover { transform: translateY(-5px); }
.google-card { border: 1px dashed #ccc; background: #fafafa; opacity: 0.95; }
.google-card:hover { border-color: #3498db; opacity: 1; background: white; }

.card-badges { position: absolute; top: 10px; right: 10px; z-index: 10; display: flex; flex-direction: column; gap: 5px; align-items: flex-end; }
.badge { padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.badge-yellow { background: #f1c40f; color: #fff; }
.badge-green { background: #27ae60; color: #fff; }
.badge-gray { background: #95a5a6; color: #fff; }
.badge-blue { background: #3498db; color: #fff; }

.image-wrapper { height: 260px; overflow: hidden; background: #f0f0f0; display: flex; align-items: center; justify-content: center; }
.cover { width: 100%; height: 100%; object-fit: cover; }

.info { padding: 15px; }
.info h3 { margin: 0 0 5px 0; font-size: 1rem; color: #2c3e50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.author { font-size: 0.85rem; color: #7f8c8d; margin-bottom: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.actions { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
.stock { font-weight: bold; color: #27ae60; font-size: 0.8rem; }
.stock.red { color: #e74c3c; }
.status-text { font-size: 0.8rem; color: #7f8c8d; font-style: italic; }

.btn-rent { background: #2c3e50; color: white; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; transition: background 0.2s; }
.btn-rent:hover { background: #42b883; }
.btn-rent.disabled { background: #ccc; cursor: not-allowed; }
.btn-suggest { background: #e67e22; color: white; border: none; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; width: 50%; font-weight: bold; }
.btn-suggest:hover { background: #d35400; }
.btn-edit-small { background: #f39c12; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }

.loading-bar { text-align: center; padding: 20px; font-weight: bold; color: #7f8c8d; width: 100%; grid-column: 1 / -1; }
.spinner { display: inline-block; width: 15px; height: 15px; border: 2px solid #ccc; border-top-color: #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state, .end-msg { text-align: center; padding: 40px; color: #7f8c8d; width: 100%; grid-column: 1 / -1; }
</style>

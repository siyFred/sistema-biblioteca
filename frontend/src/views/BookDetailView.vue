<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useAlert } from '../utils/alert'

const swal = useAlert()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const book = ref(null)
const loading = ref(true)

// Lógica para saber se é Google ou Local
const isGoogleBook = computed(() => !!route.params.googleId)

// URL base para imagens locais
const BASE_URL = 'http://127.0.0.1:8000'

const fetchBook = async () => {
  loading.value = true
  try {
    let res
    if (isGoogleBook.value) {
        // Busca na rota especial do Google
        res = await api.get(`books/google/${route.params.googleId}/`)
    } else {
        // Busca no banco de dados local
        res = await api.get(`books/${route.params.id}/`)
    }
    book.value = res.data
  } catch (error) {
    console.error(error)
    swal.error('Erro', 'Não foi possível carregar os detalhes do livro.')
    router.push('/books')
  } finally {
    loading.value = false
  }
}

const solicitarAluguel = async () => {
    if(!(await swal.confirm('Reservar?', `Confirmar pedido de empréstimo para: ${book.value.title}?`))) return
    
    try {
        await api.post('loans/', { book: book.value.id })
        // Atualiza status visualmente para bloquear o botão
        book.value.status_usuario = 'solicitado' 
        swal.success('Sucesso', 'Solicitação enviada! Aguarde a aprovação.')
    } catch (e) {
        const msg = e.response?.data?.detail || "Erro ao processar solicitação."
        swal.error('Erro', msg)
    }
}

const sugerirCompra = async () => {
    if(!(await swal.confirm('Sugerir Aquisição?', 'Você quer que a biblioteca compre este livro?'))) return
    
    try {
        await api.post('books/request-purchase/', {
            title: book.value.title,
            author: book.value.author,
            isbn: book.value.isbn
        })
        swal.success('Sugestão Enviada!', 'O bibliotecário foi notificado do seu interesse.')
    } catch (e) {
        swal.error('Atenção', e.response?.data?.detail || 'Erro ao enviar sugestão.')
    }
}

// Resolve a URL da capa (Google Link vs Local File)
const getCover = (url) => {
    if (!url) return 'https://via.placeholder.com/300x450?text=Sem+Capa'
    if (url.startsWith('http')) return url
    return `${BASE_URL}${url}`
}

onMounted(fetchBook)
</script>

<template>
  <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Carregando detalhes...</p>
  </div>
  
  <div v-else-if="book" class="detail-page">
    
    <div class="top-nav">
        <button @click="$router.back()" class="btn-back">← Voltar para o Acervo</button>
        
        <button v-if="auth.isLibrarian && !isGoogleBook" @click="$router.push(`/books/${book.id}/edit`)" class="btn-edit">
            ✏️ Editar Dados
        </button>
    </div>
    
    <div class="content-card">
        <div class="img-box">
            <img :src="getCover(book.cover_image || book.cover_url)" :alt="book.title" class="book-cover">
        </div>
        
        <div class="info-box">
            <div class="badges-row">
                <span v-if="isGoogleBook" class="tag tag-google">🌐 Google Books</span>
                <span v-else class="tag tag-local">🏠 Acervo Local</span>
                <span class="tag tag-genre">{{ book.genre || 'Geral' }}</span>
            </div>
            
            <h1 class="book-title">{{ book.title }}</h1>
            <h3 class="book-author">por {{ book.author }}</h3>
            
            <div class="meta-grid">
                <div class="meta-item">
                    <span class="label">Editora</span>
                    <span class="value">{{ book.publisher || '---' }}</span>
                </div>
                <div class="meta-item">
                    <span class="label">ISBN</span>
                    <span class="value">{{ book.isbn || '---' }}</span>
                </div>
                <div class="meta-item">
                    <span class="label">Idioma</span>
                    <span class="value">{{ book.language || '---' }}</span>
                </div>
                <div class="meta-item">
                    <span class="label">Publicação</span>
                    <span class="value">{{ book.publication_date || '---' }}</span>
                </div>
            </div>
            
            <div class="description">
                <h4>Sinopse</h4>
                <p v-html="book.description || 'Nenhuma descrição disponível para este livro.'"></p>
            </div>
            
            <div class="actions-footer">
                
                <template v-if="!isGoogleBook">
                    <div class="stock-indicator">
                        <span class="dot" :class="{ red: book.available_copies === 0 }"></span>
                        <strong>{{ book.available_copies }}</strong> exemplares disponíveis
                    </div>

                    <div class="buttons-row">
                        <button v-if="book.status_usuario === 'solicitado'" disabled class="btn-status yellow">
                            🕒 Solicitação Pendente
                        </button>
                        
                        <button v-else-if="book.status_usuario === 'alugado'" disabled class="btn-status green">
                            📖 Empréstimo Ativo
                        </button>
                        
                        <button v-else-if="book.available_copies > 0" @click="solicitarAluguel" class="btn-primary">
                            Solicitar Reserva
                        </button>
                        
                        <button v-else disabled class="btn-disabled">
                            Esgotado
                        </button>
                    </div>
                </template>
                
                <template v-else>
                    <div class="stock-indicator red-text">
                        ⚠️ Este item não pertence ao acervo físico da biblioteca.
                    </div>
                    <button @click="sugerirCompra" class="btn-warn">
                        💡 Sugerir Compra
                    </button>
                </template>

            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.detail-page { max-width: 1000px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', sans-serif; }

/* Navegação */
.top-nav { display: flex; justify-content: space-between; margin-bottom: 20px; }
.btn-back { background: none; border: none; font-size: 1rem; color: #7f8c8d; cursor: pointer; font-weight: 600; transition: 0.2s; }
.btn-back:hover { color: #2c3e50; transform: translateX(-5px); }
.btn-edit { background: #f39c12; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.btn-edit:hover { background: #e67e22; }

/* Layout Principal */
.content-card { display: grid; grid-template-columns: 320px 1fr; gap: 40px; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }

/* Imagem */
.img-box { text-align: center; }
.book-cover { width: 100%; border-radius: 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.15); object-fit: cover; }

/* Informações */
.info-box { display: flex; flex-direction: column; }

/* Tags/Badges */
.badges-row { display: flex; gap: 10px; margin-bottom: 15px; }
.tag { padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
.tag-google { background: #ecf0f1; color: #7f8c8d; border: 1px solid #bdc3c7; }
.tag-local { background: #e8f6f3; color: #16a085; border: 1px solid #a2d9ce; }
.tag-genre { background: #eaf2f8; color: #2980b9; }

.book-title { margin: 0 0 5px 0; font-size: 2.2rem; color: #2c3e50; line-height: 1.2; }
.book-author { margin: 0 0 25px 0; font-size: 1.1rem; color: #7f8c8d; font-weight: normal; }

/* Grid de Metadados */
.meta-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 25px; }
.meta-item { display: flex; flex-direction: column; }
.meta-item .label { font-size: 0.75rem; color: #95a5a6; font-weight: bold; text-transform: uppercase; }
.meta-item .value { font-size: 0.95rem; color: #34495e; font-weight: 600; }

.description h4 { margin-bottom: 10px; color: #2c3e50; }
.description p { line-height: 1.6; color: #555; font-size: 0.95rem; margin-bottom: 30px; }

/* Footer de Ações */
.actions-footer { margin-top: auto; padding-top: 20px; border-top: 1px solid #eee; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px; }

.stock-indicator { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: #2c3e50; }
.dot { width: 10px; height: 10px; background: #27ae60; border-radius: 50%; }
.dot.red { background: #c0392b; }
.red-text { color: #e74c3c; font-weight: bold; font-size: 0.85rem; }

/* Botões de Ação */
.btn-primary { background: #2c3e50; color: white; border: none; padding: 12px 25px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-primary:hover { background: #34495e; transform: translateY(-2px); }

.btn-warn { background: #e67e22; color: white; border: none; padding: 12px 25px; border-radius: 8px; font-size: 1rem; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-warn:hover { background: #d35400; transform: translateY(-2px); }

.btn-status { padding: 12px 25px; border-radius: 8px; font-weight: bold; border: none; cursor: default; }
.btn-status.yellow { background: #f1c40f; color: white; }
.btn-status.green { background: #27ae60; color: white; }

.btn-disabled { background: #bdc3c7; color: white; border: none; padding: 12px 25px; border-radius: 8px; font-weight: bold; cursor: not-allowed; }

/* Loading */
.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; color: #7f8c8d; }
.spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 15px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Responsivo */
@media (max-width: 768px) {
    .content-card { grid-template-columns: 1fr; padding: 20px; }
    .img-box img { max-width: 200px; }
    .actions-footer { flex-direction: column; text-align: center; }
    .btn-primary, .btn-warn, .btn-disabled, .btn-status { width: 100%; }
}
</style>
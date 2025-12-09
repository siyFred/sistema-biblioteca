<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api'
import { useAlert } from '../utils/alert' 

const swal = useAlert() 
const router = useRouter()
const route = useRoute() 

const isEditing = computed(() => !!route.params.id)
const isImporting = computed(() => !!route.query.googleId || !!route.query.title)

const form = ref({ 
    title: '', 
    author: '', 
    isbn: '', 
    publisher: '', 
    genre: '',       
    language: 'Português',
    publication_year: new Date().getFullYear(),
    total_copies: 1, 
    description: '',
    cover_url: ''
})
const file = ref(null)
const localPreview = ref('')
const importIsbn = ref('')
const loadingImport = ref(false)

const handleFile = (e) => { 
    const selected = e.target.files[0]
    if (selected) {
        file.value = selected
        localPreview.value = URL.createObjectURL(selected)
    }
}

const removeLocalFile = () => {
    file.value = null
    localPreview.value = ''
}

const fetchByIsbn = async () => {
    if (!importIsbn.value) return
    loadingImport.value = true
    try {
        // Usando a rota de busca global existente com filtro de source=google
        const { data } = await api.get('books/search-global/', {
            params: {
                source: 'google',
                q: `isbn:${importIsbn.value}`
            }
        })

        if (data && data.length > 0) {
            const bookData = data[0] // Pega o primeiro resultado
            
            form.value.title = bookData.title || ''
            form.value.author = bookData.author || ''
            form.value.isbn = bookData.isbn || importIsbn.value
            form.value.publisher = bookData.publisher || ''
            form.value.description = bookData.description || ''
            form.value.publication_year = bookData.publication_date ? bookData.publication_date.split('-')[0] : ''
            form.value.language = bookData.language || 'Português'
            form.value.cover_url = bookData.cover_url || bookData.cover_image || ''
            form.value.genre = bookData.genre || 'Geral'
            
            swal.success('Livro Encontrado!', `Dados de "${bookData.title}" carregados.`)
        } else {
            swal.warning('Atenção', 'Nenhum livro encontrado com este ISBN.')
        }

    } catch (e) {
        console.error(e)
        swal.error('Erro', 'Falha ao buscar livro.')
    } finally {
        loadingImport.value = false
    }
}

const loadBookData = async () => {
    try {
        const { data } = await api.get(`books/${route.params.id}/`)
        form.value = {
            title: data.title,
            author: data.author,
            isbn: data.isbn,
            publisher: data.publisher,
            genre: data.genre,
            language: data.language,
            total_copies: data.total_copies,
            description: data.description,
            publication_year: data.publication_date ? data.publication_date.split('-')[0] : '',
            cover_url: data.cover_url
        }
    } catch (error) {
        swal.error('Erro', 'Não foi possível carregar os dados do livro.')
        router.push('/books')
    }
}

const loadGoogleData = async () => {
    try {
        const { data } = await api.get(`books/google/${route.query.googleId}/`)
        
        form.value.title = data.title || ''
        form.value.author = data.author || ''
        form.value.isbn = data.isbn || ''
        form.value.publisher = data.publisher || ''
        form.value.description = data.description || ''
        form.value.publication_year = data.publication_date ? data.publication_date.split('-')[0] : ''
        form.value.language = data.language || 'Português'
        form.value.cover_url = data.cover_url || data.cover_image || ''
        form.value.genre = data.genre || 'Geral'
        
        swal.success('Dados Importados', 'Complete as informações e salve o livro.')
        
    } catch (error) {
        console.error(error)
        swal.error('Erro', 'Falha ao importar dados do Google.')
    }
}

const loadQueryData = () => {
    if (route.query.title) form.value.title = route.query.title
    if (route.query.author) form.value.author = route.query.author
    if (route.query.isbn) form.value.isbn = route.query.isbn
}

const submit = async () => {
  try {
    const data = new FormData()
    
    if (form.value.publication_year) {
        data.append('publication_date', `${form.value.publication_year}-01-01`)
    }

    data.append('total_copies', parseInt(form.value.total_copies))
    
    if (!isEditing.value) {
        data.append('available_copies', parseInt(form.value.total_copies))
    }

    data.append('title', form.value.title)
    data.append('author', form.value.author)
    data.append('isbn', form.value.isbn)
    data.append('publisher', form.value.publisher)
    data.append('genre', form.value.genre)
    data.append('language', form.value.language)
    data.append('description', form.value.description)
    
    if (form.value.cover_url) {
        data.append('cover_url', form.value.cover_url)
    }

    if (file.value) {
        data.append('cover_image', file.value)
    }

    if (isEditing.value) {
        await api.patch(`books/${route.params.id}/`, data, { 
            headers: { 'Content-Type': 'multipart/form-data' } 
        })
        swal.success('Livro atualizado com sucesso!')
    } else {
        await api.post('books/', data, { 
            headers: { 'Content-Type': 'multipart/form-data' } 
        })
        swal.success('Livro cadastrado com sucesso!')
    }
    
    router.push('/books')

  } catch (error) {
    console.error("Erro:", error.response?.data)
    swal.error('Erro ao Salvar', 'Verifique os dados preenchidos.')
  }
}

onMounted(() => {
    if (isEditing.value) {
        loadBookData()
    } else if (route.query.googleId) {
        loadGoogleData()
    } else {
        loadQueryData()
    }
})
</script>

<template>
  <div class="container">
    <h2>{{ isEditing ? 'Editar Livro' : (isImporting ? 'Importar Livro' : 'Novo Livro') }}</h2>
    
    <form @submit.prevent="submit" class="form-card">
      
      <!-- IMPORTAR POR ISBN -->
      <div v-if="!isEditing" class="import-section">
          <h3>📥 Importar do Google Books</h3>
          <div class="import-box">
              <input 
                  v-model="importIsbn" 
                  placeholder="Digite o ISBN (apenas números)..." 
                  @keyup.enter="fetchByIsbn"
                  class="isbn-input"
              />
              <button type="button" @click="fetchByIsbn" class="btn-import" :disabled="loadingImport">
                  {{ loadingImport ? 'Buscando...' : 'Buscar' }}
              </button>
          </div>
          <small>Preenche automaticamente título, autor, capa e mais.</small>
          <hr />
      </div>



      <div class="row">
        <div class="input-group">
            <label>Título *</label>
            <input v-model="form.title" required />
        </div>
        <div class="input-group">
            <label>Autor *</label>
            <input v-model="form.author" required />
        </div>
      </div>
      
      <div class="row">
        <div class="input-group">
            <label>ISBN *</label>
            <input v-model="form.isbn" required />
        </div>
        <div class="input-group">
            <label>Editora</label>
            <input v-model="form.publisher" />
        </div>
      </div>

      <div class="row">
        <div class="input-group">
            <label>Gênero</label>
            <input v-model="form.genre" required />
        </div>
        <div class="input-group">
             <label>Ano de Publicação</label>
             <input type="number" v-model="form.publication_year" />
        </div>
      </div>

      <div class="row">
         <div class="input-group">
             <label>Idioma</label>
             <input v-model="form.language" />
         </div>
         <div class="input-group">
             <label>Quantidade Total</label>
             <input type="number" v-model="form.total_copies" min="1" required />
             <small v-if="isEditing" style="color: #666">Cuidado ao reduzir se houver livros emprestados.</small>
         </div>
      </div>
      
      <div class="input-group">
          <label>Descrição</label>
          <textarea v-model="form.description" rows="3"></textarea>
      </div>
      
      <div class="row">
          <div class="input-group cover-section">
              <label>Capa do Livro</label>
              
              <div class="cover-selection-container">
                  <!-- Preview Area -->
                  <div class="cover-display" v-if="localPreview || form.cover_url">
                      <img :src="localPreview || form.cover_url" alt="Preview Capa" class="cover-img" />
                      <div class="source-badge" :class="localPreview ? 'badge-local' : 'badge-google'">
                          {{ localPreview ? '📁 Upload Local' : '🌎 Google Books' }}
                      </div>
                  </div>
                  <div v-else class="no-cover">
                      <span>Sem capa definida</span>
                  </div>

                  <!-- Controls -->
                  <div class="cover-controls">
                      <p v-if="!localPreview && form.cover_url" class="info-text">
                          ℹ️ Esta capa foi sugerida pelo Google. Você pode <strong>manter ela</strong> ou enviar uma nova abaixo.
                      </p>
                      
                      <div class="upload-actions">
                          <label for="cover-upload" class="btn-upload">
                              {{ localPreview ? 'Trocar Imagem' : (form.cover_url ? 'Substituir por Arquivo Local' : 'Escolher Capa') }}
                          </label>
                          <input id="cover-upload" type="file" @change="handleFile" accept="image/*" hidden />

                          <button v-if="localPreview" @click="removeLocalFile" type="button" class="btn-link-danger">
                              ⚠️ Cancelar upload (Usar capa do Google)
                          </button>
                      </div>
                  </div>
              </div>
          </div>
      </div>

      <button type="submit">{{ isEditing ? 'Atualizar Livro' : 'Salvar Livro' }}</button>
    </form>
  </div>
</template>

<style scoped>
.container { max-width: 700px; margin: 0 auto; }
.form-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.row { display: flex; gap: 15px; margin-bottom: 15px; }
.input-group { flex: 1; display: flex; flex-direction: column; text-align: left; }
.input-group label { font-size: 0.9rem; font-weight: bold; margin-bottom: 5px; color: #555; }
input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
button { width: 100%; padding: 12px; background: #2c3e50; color: white; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; font-weight: bold; transition: 0.2s; }
button:hover { background: #34495e; }
.cover-preview { text-align: center; margin-bottom: 15px; background: #f9f9f9; padding: 10px; border-radius: 5px; }
.cover-preview img { display: block; margin: 0 auto 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }

.import-section { margin-bottom: 25px; background: #f0f4f8; padding: 15px; border-radius: 8px; border: 1px dashed #cfd8dc; }
.import-section h3 { margin: 0 0 10px 0; font-size: 1rem; color: #2c3e50; }
.import-box { display: flex; gap: 10px; }
.isbn-input { flex: 1; padding: 10px; border: 1px solid #cfd8dc; border-radius: 4px; }
.btn-import { background: #42b883; color: white; padding: 0 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; height: 42px; margin-top: 0; width: auto; }
.btn-import:hover { background: #3aa876; }
.btn-import:disabled { background: #a5d6a7; cursor: wait; }
.btn-import:hover { background: #3aa876; }
.btn-import:disabled { background: #a5d6a7; cursor: wait; }

/* Cover Section Styles */
.cover-section { grid-column: span 2; }
.cover-selection-container { 
    display: flex; gap: 20px; align-items: flex-start; 
    background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;
}
.cover-display { position: relative; width: 100px; height: 145px; flex-shrink: 0; background: #ddd; border-radius: 6px; overflow: hidden; box-shadow: 0 3px 6px rgba(0,0,0,0.1); }
.cover-img { width: 100%; height: 100%; object-fit: cover; }
.no-cover { width: 100px; height: 145px; display: flex; align-items: center; justify-content: center; background: #e9ecef; color: #adb5bd; font-size: 0.8rem; text-align: center; border-radius: 6px; border: 2px dashed #ced4da; }

.source-badge { position: absolute; bottom: 0; left: 0; right: 0; font-size: 0.65rem; text-align: center; padding: 3px; font-weight: bold; color: white; }
.badge-google { background: rgba(66, 133, 244, 0.9); }
.badge-local { background: rgba(52, 73, 94, 0.9); }

.cover-controls { flex: 1; display: flex; flex-direction: column; gap: 10px; justify-content: center; min-height: 140px; }
.info-text { margin: 0; font-size: 0.9rem; color: #6c757d; line-height: 1.4; }
.btn-upload { display: inline-block; background: white; border: 1px solid #ced4da; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 0.9rem; color: #495057; font-weight: 600; text-align: center; transition: all 0.2s; width: fit-content; }
.btn-upload:hover { background: #e9ecef; border-color: #adb5bd; }
.btn-link-danger { background: none; border: none; color: #dc3545; font-size: 0.85rem; cursor: pointer; text-decoration: underline; padding: 0; text-align: left; width: fit-content; }
.btn-link-danger:hover { color: #bd2130; }

@media (max-width: 600px) {
    .cover-selection-container { flex-direction: column; align-items: center; text-align: center; }
    .cover-controls { align-items: center; }
}
</style>
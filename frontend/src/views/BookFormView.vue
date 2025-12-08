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

const handleFile = (e) => { file.value = e.target.files[0] }

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
      
      <div v-if="form.cover_url && !file" class="cover-preview">
          <img :src="form.cover_url" alt="Capa" height="100">
          <small>Capa importada do Google</small>
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
      
      <div class="input-group">
          <label>Capa do Livro (Arquivo Local)</label>
          <input type="file" @change="handleFile" accept="image/*" />
          <small v-if="form.cover_url">Se enviar um arquivo, a capa do Google será ignorada.</small>
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
</style>
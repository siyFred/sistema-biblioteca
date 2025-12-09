<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import { useAlert } from '../utils/alert'

const swal = useAlert()
const users = ref([])
const loading = ref(true)
const editingUser = ref(null)

const searchQuery = ref('')
const roleFilter = ref('ALL')

const form = ref({
  id: null,
  first_name: '',
  last_name: '',
  email: '',
  role: ''
})

const fetchUsers = async () => {
  try {
    const res = await api.get('users/')
    users.value = res.data
  } catch (e) {
    swal.error('Erro', 'Erro ao carregar usuários.')
  } finally {
    loading.value = false
  }
}

const filteredUsers = computed(() => {
    return users.value.filter(user => {
        const matchesRole = roleFilter.value === 'ALL' || user.role === roleFilter.value

        const term = searchQuery.value.toLowerCase()
        const fullName = `${user.first_name} ${user.last_name}`.toLowerCase()
        
        const matchesSearch = 
            fullName.includes(term) ||
            (user.email && user.email.toLowerCase().includes(term)) ||
            user.username.toLowerCase().includes(term)

        return matchesRole && matchesSearch
    })
})

const openEdit = (user) => {
  editingUser.value = user
  form.value = { 
    id: user.id,
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    email: user.email || '',
    role: user.role
  }
}

const saveUser = async () => {
  try {
    await api.patch(`users/${form.value.id}/`, form.value)
    
    swal.success('Usuário atualizado com sucesso!')
    editingUser.value = null
    fetchUsers()
  } catch (e) {
    console.error(e)
    swal.error('Erro', 'Erro ao salvar alterações.')
  }
}

onMounted(fetchUsers)
</script>

<template>
  <div class="manage-page">
    <div class="header-area">
        <h1>👥 Gestão de Usuários</h1>
        <span class="count-badge">{{ filteredUsers.length }} encontrados</span>
    </div>

    <div class="filters-bar">
        <div class="search-box">
            <span class="icon">🔍</span>
            <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="Buscar por nome, email ou user..." 
            />
        </div>

        <div class="filter-select">
            <label>Cargo:</label>
            <select v-model="roleFilter">
                <option value="ALL">Todos</option>
                <option value="READER">Leitores</option>
                <option value="LIBRARIAN">Bibliotecários</option>
            </select>
        </div>
    </div>

    <div v-if="loading" class="loading">Carregando leitores...</div>

    <table v-else class="user-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Nome</th>
          <th>E-mail</th>
          <th>Cargo</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in filteredUsers" :key="user.id">
          <td>{{ user.id }}</td>
          <td>
             <div class="user-info">
                <strong>{{ user.first_name }} {{ user.last_name }}</strong>
                <span>@{{ user.username }}</span>
             </div>
          </td>
          <td>{{ user.email || '---' }}</td>
          <td>
            <span :class="['badge', (user.role === 'LIBRARIAN' || user.is_superuser || user.is_staff) ? 'admin' : 'reader']">
                {{ (user.role === 'LIBRARIAN' || user.is_superuser || user.is_staff) ? 'Bibliotecário' : 'Leitor' }}
            </span>
          </td>
          <td class="actions">
            <button v-if="!user.is_superuser" @click="openEdit(user)" class="btn-edit">✏️ Editar</button>
            <span v-else class="superuser-tag">👑 Super Admin</span>
          </td>
        </tr>

        <tr v-if="filteredUsers.length === 0">
            <td colspan="5" class="empty-state">
                Nenhum usuário encontrado para essa busca.
            </td>
        </tr>
      </tbody>
    </table>

    <Transition name="modal">
        <div v-if="editingUser" class="modal-overlay" @click.self="editingUser = null">
          <div class="modal-content narrow">
            <div class="modal-header">
                <h2>✏️ Editando: {{ editingUser.username }}</h2>
                <button class="close-btn" @click="editingUser = null">&times;</button>
            </div>
            
            <form @submit.prevent="saveUser">
                <div class="form-group">
                    <label>E-mail</label>
                    <input v-model="form.email" type="email" class="input" />
                </div>

                <div class="form-group">
                    <label>Nome</label>
                    <input v-model="form.first_name" type="text" class="input" />
                </div>
                
                <div class="form-group">
                    <label>Sobrenome</label>
                    <input v-model="form.last_name" type="text" class="input" />
                </div>

                <div class="form-group">
                    <label>Cargo</label>
                    <select v-model="form.role" class="input">
                        <option value="READER">Leitor</option>
                        <option value="LIBRARIAN">Bibliotecário</option>
                    </select>
                </div>

                <div class="modal-actions">
                    <button type="button" @click="editingUser = null" class="btn btn-outline" style="margin-right: 10px;">Cancelar</button>
                    <button type="submit" class="btn btn-accent">Salvar</button>
                </div>
            </form>
          </div>
        </div>
    </Transition>

  </div>
</template>

<style scoped>
.manage-page { max-width: 1000px; margin: 0 auto; padding: 20px; font-family: sans-serif; }
.header-area { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
h1 { color: #2c3e50; margin: 0; }
.count-badge { background: #e0f2f1; color: #00695c; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; }

.filters-bar { 
    display: flex; gap: 20px; background: white; padding: 15px; 
    border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px;
    flex-wrap: wrap; align-items: center;
}
.search-box { 
    flex: 1; display: flex; align-items: center; gap: 10px; 
    background: #f8f9fa; padding: 0 15px; border-radius: 6px; border: 1px solid #ddd;
}
.search-box input { border: none; background: transparent; padding: 12px 0; width: 100%; font-size: 1rem; outline: none; }
.filter-select { display: flex; align-items: center; gap: 10px; font-weight: 600; color: #555; }
.filter-select select { padding: 10px; border-radius: 6px; border: 1px solid #ddd; background: white; cursor: pointer; }

.user-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
.user-table th, .user-table td { padding: 15px; text-align: left; border-bottom: 1px solid #eee; }
.user-table th { background: #f8f9fa; color: #7f8c8d; font-weight: 600; }
.user-info { display: flex; flex-direction: column; }
.user-info span { font-size: 0.85rem; color: #999; }
.empty-state { text-align: center; padding: 30px; color: #999; font-style: italic; }

.badge { padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; }
.badge.admin { background: #e3f2fd; color: #1565c0; }
.badge.reader { background: #f1f8e9; color: #33691e; }
.superuser-tag { font-size: 0.8rem; font-weight: bold; color: #f39c12; }

.btn-edit { background: #ffb74d; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; transition: 0.2s; }
.btn-edit:hover { background: #f57c00; }

/* MODAL OVERRIDES */
.modal-content.narrow { max-width: 400px; }
.form-group { margin-bottom: 15px; display: flex; flex-direction: column; }
.form-group label { margin-bottom: 5px; font-weight: bold; font-size: 0.9rem; }
.modal-actions { margin-top: 20px; text-align: right; }
</style>
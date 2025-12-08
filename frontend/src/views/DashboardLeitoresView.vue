<template>
  <div>
    <h1>Leitores Cadastrados</h1>
    <input v-model="search" placeholder="Buscar por nome ou email..." @input="fetchUsers" />
    <table>
      <thead>
        <tr>
          <th>Nome</th>
          <th>Email</th>
          <th>CPF</th>
          <th>Função</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.first_name }} {{ user.last_name }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.cpf }}</td>
          <td>{{ user.role === 'LIBRARIAN' ? 'Bibliotecário' : 'Leitor' }}</td>
          <td>
            <button v-if="user.role === 'READER'" @click="promote(user.id)">Promover a Bibliotecário</button>
            <button v-if="user.role === 'LIBRARIAN'" @click="demote(user.id)">Rebaixar para Leitor</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
const users = ref([])
const search = ref('')
const fetchUsers = async () => {
  const res = await api.get('users/')
  users.value = res.data.filter(u => {
    const term = search.value.toLowerCase()
    return (
      u.first_name?.toLowerCase().includes(term) ||
      u.last_name?.toLowerCase().includes(term) ||
      u.email?.toLowerCase().includes(term)
    )
  })
}
const promote = async (id) => {
  await api.post(`users/${id}/promover/`, { role: 'LIBRARIAN' })
  fetchUsers()
}
const demote = async (id) => {
  await api.post(`users/${id}/promover/`, { role: 'READER' })
  fetchUsers()
}
onMounted(fetchUsers)
</script>
<style scoped>
table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
th, td { padding: 10px; border-bottom: 1px solid #eee; }
th { background: #e0f7fa; }
</style>

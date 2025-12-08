<script setup>
import { ref } from 'vue';

// Dados de exemplo
const users = ref([
  { id: 1, name: 'João Silva', email: 'joao.silva@email.com', cpf: '111.222.333-44' },
  { id: 2, name: 'Maria Souza', email: 'maria.souza@email.com', cpf: '222.333.444-55' },
  { id: 3, name: 'Pedro Santos', email: 'pedro.santos@email.com', cpf: '333.444.555-66' },
]);

const searchQuery = ref('');
</script>

<template>
  <div>
    <header class="view-header">
      <h1>Gerenciamento de Usuários</h1>
      <div class="actions">
        <input type="search" v-model="searchQuery" placeholder="Buscar por nome, email, CPF..." />
        <button class="primary-btn">Adicionar Usuário</button>
      </div>
    </header>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>CPF</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.cpf }}</td>
            <td class="actions-cell">
              <button class="btn-action">Editar</button>
              <button class="btn-action">Ver Histórico</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
/* Reutilizando estilos. Idealmente, mova para um arquivo CSS global */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.actions {
  display: flex;
  gap: 1rem;
}
.actions input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  width: 250px;
}
.primary-btn {
  background-color: #42b883;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
.table-container {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}
th {
  background-color: #f8f9fa;
  font-weight: 600;
}
.actions-cell {
  display: flex;
  gap: 8px;
}
.btn-action {
  padding: 5px 10px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}
</style>
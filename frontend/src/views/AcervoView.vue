<script setup>
import { ref } from 'vue';

// Dados de exemplo. No futuro, virão da sua API.
const books = ref([
  { id: 1, title: 'Clean Code', author: 'Robert C. Martin', isbn: '978-0132350884', available: 5 },
  { id: 2, title: 'Dom Casmurro', author: 'Machado de Assis', isbn: '978-8535914849', available: 2 },
  { id: 3, title: 'O Hobbit', author: 'J.R.R. Tolkien', isbn: '978-8595084742', available: 8 },
  { id: 4, title: 'A Revolução dos Bichos', author: 'George Orwell', isbn: '978-8535909555', available: 0 },
]);

const searchQuery = ref('');

// Lógica para abrir modal, editar, excluir, etc. viria aqui.

</script>

<template>
  <div>
    <header class="view-header">
      <h1>Gerenciamento de Acervo</h1>
      <div class="actions">
        <input type="search" v-model="searchQuery" placeholder="Buscar por título, autor, ISBN..." />
        <button class="primary-btn">Adicionar Livro</button>
      </div>
    </header>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Título</th>
            <th>Autor</th>
            <th>ISBN</th>
            <th>Qtd. Disponível</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="book in books" :key="book.id">
            <td>{{ book.title }}</td>
            <td>{{ book.author }}</td>
            <td>{{ book.isbn }}</td>
            <td>
              <span :class="{'low-stock': book.available < 3, 'no-stock': book.available === 0}">
                {{ book.available }}
              </span>
            </td>
            <td class="actions-cell">
              <button class="btn-action">Editar</button>
              <button class="btn-action btn-danger">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
/* Estilos compartilhados que podem ser movidos para um CSS global */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.view-header h1 {
  margin: 0;
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
}
.btn-danger {
  color: #e74c3c;
  border-color: #e74c3c;
}

.low-stock { color: #f39c12; font-weight: bold; }
.no-stock { color: #e74c3c; font-weight: bold; }
</style>
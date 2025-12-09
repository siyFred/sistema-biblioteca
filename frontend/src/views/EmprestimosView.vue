<script setup>
import { ref } from 'vue';

// Dados de exemplo
const loans = ref([
  { id: 1, user: 'João Silva', book: 'Clean Code', loanDate: '2025-11-20', returnDate: '2025-12-04', status: 'Ativo' },
  { id: 2, user: 'Maria Souza', book: 'Dom Casmurro', loanDate: '2025-11-15', returnDate: '2025-11-29', status: 'Atrasado' },
  { id: 3, user: 'Pedro Santos', book: 'Harry Potter 1', loanDate: '2025-11-10', returnDate: '2025-11-24', status: 'Devolvido' },
  { id: 4, user: 'Ana Costa', book: 'O Hobbit', loanDate: '2025-11-25', returnDate: '2025-12-09', status: 'Ativo' },
]);

const getStatusClass = (status) => {
  return `status-badge ${status.toLowerCase()}`;
};
</script>

<template>
  <div>
    <header class="view-header">
      <h1>Gerenciamento de Empréstimos</h1>
      <div class="actions">
        <!-- Filtros podem ser adicionados aqui -->
        <button class="primary-btn">Registrar Empréstimo</button>
      </div>
    </header>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Usuário</th>
            <th>Livro</th>
            <th>Data do Empréstimo</th>
            <th>Data de Devolução</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loan in loans" :key="loan.id">
            <td>{{ loan.user }}</td>
            <td>{{ loan.book }}</td>
            <td>{{ loan.loanDate }}</td>
            <td>{{ loan.returnDate }}</td>
            <td>
              <span :class="getStatusClass(loan.status)">
                {{ loan.status }}
              </span>
            </td>
            <td class="actions-cell">
              <button v-if="loan.status !== 'Devolvido'" class="btn-action">Marcar como Devolvido</button>
              <button class="btn-action">Ver Detalhes</button>
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
.actions { display: flex; gap: 1rem; }
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
.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: capitalize;
}
.status-badge.ativo { background-color: #e8f8f5; color: #2ecc71; }
.status-badge.atrasado { background-color: #fdedec; color: #e74c3c; }
.status-badge.devolvido { background-color: #ebf5fb; color: #3498db; }
</style>
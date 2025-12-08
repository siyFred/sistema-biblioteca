<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import { useAlert } from '../utils/alert'
import Swal from 'sweetalert2'

const swal = useAlert()
const auth = useAuthStore()
const loading = ref(true)

const form = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  cpf: '',
  phone: '',
  cep: '',
  street: '',
  number: '',
  complement: '',
  district: '',
  city: '',
  state: ''
})

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await api.get('users/me/')
    console.log("📥 Dados recebidos do Django:", res.data)
    Object.assign(form, res.data)
  } catch (e) {
    console.error("Erro ao buscar perfil:", e)
  } finally {
    loading.value = false
  }
}

const saveProfile = async () => {
  try {
    console.log("📤 Enviando atualização:", form)
    
    await api.patch('users/me/', form)
    
    swal.success('Perfil atualizado com sucesso!')
    
    if (form.username) auth.user.username = form.username
    if (form.first_name) auth.user.first_name = form.first_name
    
  } catch (e) {
    console.error("Erro ao salvar:", e)
    swal.error('Erro', 'Erro ao salvar perfil.')
  }
}

const upgradeAccount = async () => {
    const { value: code } = await Swal.fire({
        title: 'Área Restrita',
        text: 'Digite a chave de administrador para se tornar Bibliotecário.',
        input: 'password',
        inputPlaceholder: 'Chave Mestra...',
        showCancelButton: true,
        confirmButtonText: 'Validar',
        confirmButtonColor: '#2c3e50',
        cancelButtonText: 'Cancelar'
    })

    if (code) {
        try {
            await api.post('users/upgrade_role/', { admin_code: code })
            await Swal.fire('Sucesso!', 'Perfil atualizado. Bem-vindo, Bibliotecário!', 'success')
            window.location.reload()
        } catch (e) {
            Swal.fire('Erro', 'Chave inválida.', 'error')
        }
    }
}

onMounted(fetchProfile)
</script>

<template>
  <div class="profile-page">
    
    <div class="profile-header">
      <div class="avatar-circle">
        {{ form.first_name ? form.first_name.charAt(0).toUpperCase() : auth.user?.username?.charAt(0).toUpperCase() }}
      </div>
      <div class="header-info">
        <h2>{{ form.first_name }} {{ form.last_name }}</h2>
        <p class="subtitle">@{{ form.username || auth.user?.username }}</p>
        <span class="role-badge">
            {{ auth.isLibrarian ? '🛡️ Bibliotecário' : '📖 Leitor' }}
        </span>
      </div>
    </div>

    <div v-if="loading" class="loading">Carregando informações...</div>

    <div v-else class="form-container">
      <form @submit.prevent="saveProfile">
        
        <section class="form-section">
          <h3>👤 Dados Pessoais</h3>
          <div class="grid-layout">
            
            <div class="form-group">
              <label>Nome</label>
              <input v-model="form.first_name" type="text" placeholder="Seu nome" />
            </div>

            <div class="form-group">
              <label>Sobrenome</label>
              <input v-model="form.last_name" type="text" placeholder="Seu sobrenome" />
            </div>

            <div class="form-group">
              <label>E-mail (Não editável)</label>
              <input v-model="form.email" type="email" disabled class="disabled-input" />
            </div>

            <div class="form-group">
              <label>CPF</label>
              <input v-model="form.cpf" type="text" placeholder="000.000.000-00" />
            </div>

            <div class="form-group">
              <label>Telefone</label>
              <input v-model="form.phone" type="text" placeholder="(00) 00000-0000" />
            </div>
          </div>
        </section>

        <hr />

        <section class="form-section">
          <h3>📍 Endereço</h3>
          <div class="grid-layout">
            
            <div class="form-group">
              <label>CEP</label>
              <input v-model="form.cep" type="text" placeholder="00000-000" />
            </div>

            <div class="form-group span-2">
              <label>Rua / Avenida</label>
              <input v-model="form.street" type="text" />
            </div>

            <div class="form-group">
              <label>Número</label>
              <input v-model="form.number" type="text" />
            </div>

            <div class="form-group">
              <label>Complemento</label>
              <input v-model="form.complement" type="text" />
            </div>

            <div class="form-group">
              <label>Bairro</label>
              <input v-model="form.district" type="text" />
            </div>

            <div class="form-group">
              <label>Cidade</label>
              <input v-model="form.city" type="text" />
            </div>

            <div class="form-group">
              <label>Estado (UF)</label>
              <input v-model="form.state" type="text" maxlength="2" placeholder="UF" />
            </div>
          </div>
        </section>

        <hr v-if="!auth.isLibrarian" />

        <section v-if="!auth.isLibrarian" class="form-section">
            <h3>🛡️ Área Administrativa</h3>
             <div class="admin-box">
                <p>Possui uma chave de administrador?</p>
                <button type="button" @click="upgradeAccount" class="btn-admin">
                    🔑 Tornar-se Bibliotecário
                </button>
            </div>
        </section>

        <div class="actions">
          <button type="submit" class="btn-save">Salvar Alterações</button>
        </div>

      </form>
    </div>
  </div>
</template>

<style scoped>
.profile-page { max-width: 800px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', sans-serif; }

.profile-header { 
    display: flex; align-items: center; gap: 20px; 
    background: white; padding: 30px; border-radius: 12px; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 30px;
}

.avatar-circle {
    width: 80px; height: 80px; background: #2c3e50; color: white;
    font-size: 2.5rem; font-weight: bold; display: flex; 
    align-items: center; justify-content: center; border-radius: 50%;
}

.header-info h2 { margin: 0; color: #2c3e50; font-size: 1.5rem; }
.subtitle { color: #7f8c8d; margin: 5px 0 10px; }
.role-badge { 
    background: #e0f2f1; color: #00695c; padding: 5px 12px; 
    border-radius: 20px; font-size: 0.85rem; font-weight: bold; 
    display: inline-block;
}

.form-container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }

.form-section h3 { margin-bottom: 20px; color: #2c3e50; border-left: 4px solid #42b883; padding-left: 10px; }

.grid-layout { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
    gap: 20px; 
}

.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 0.9rem; font-weight: 600; color: #555; }
.form-group input { 
    padding: 10px; border: 1px solid #ddd; border-radius: 6px; 
    font-size: 1rem; transition: border 0.2s; 
}
.form-group input:focus { border-color: #42b883; outline: none; box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1); }
.disabled-input { background: #f9f9f9; color: #999; cursor: not-allowed; }

.span-2 { grid-column: span 2; }
@media (max-width: 600px) { .span-2 { grid-column: span 1; } }

hr { margin: 30px 0; border: none; border-top: 1px solid #eee; }

.actions { text-align: right; margin-top: 20px; }
.btn-save { 
    background: #42b883; color: white; border: none; 
    padding: 12px 25px; border-radius: 6px; font-size: 1rem; 
    font-weight: bold; cursor: pointer; transition: background 0.2s; 
}
.btn-save:hover { background: #3aa876; transform: translateY(-1px); }

.loading { text-align: center; padding: 50px; color: #7f8c8d; font-size: 1.2rem; }

.admin-box { 
    background: #f8f9fa; padding: 20px; border-radius: 8px; 
    border: 1px dashed #bdc3c7; display: flex; 
    justify-content: space-between; align-items: center; 
    flex-wrap: wrap; gap: 10px;
}
.admin-box p { margin: 0; color: #555; }
.btn-admin { 
    background: #2c3e50; color: white; padding: 10px 15px; border-radius: 6px; 
    cursor: pointer; border: none; font-weight: bold; transition: 0.2s;
}
.btn-admin:hover { background: #34495e; }
</style>
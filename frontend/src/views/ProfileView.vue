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
    
    <div class="profile-header card">
      <div class="avatar-circle">
        {{ form.first_name ? form.first_name.charAt(0).toUpperCase() : auth.user?.username?.charAt(0).toUpperCase() }}
      </div>
      <div class="header-info">
        <h2>{{ form.first_name }} {{ form.last_name }}</h2>
        <p class="subtitle">@{{ form.username || auth.user?.username }}</p>
        <span class="role-badge" :class="auth.isLibrarian ? 'badge-admin' : 'badge-user'">
            {{ auth.isLibrarian ? '🛡️ Bibliotecário' : '📖 Leitor' }}
        </span>
      </div>
    </div>

    <div v-if="loading" class="loading">Carregando informações...</div>

    <div v-else class="form-container card">
      <form @submit.prevent="saveProfile">
        
        <section class="form-section">
          <h3>👤 Dados Pessoais</h3>
          <div class="grid-layout">
            
            <div class="form-group">
              <label class="label">Nome</label>
              <input v-model="form.first_name" type="text" class="input" placeholder="Seu nome" />
            </div>

            <div class="form-group">
              <label class="label">Sobrenome</label>
              <input v-model="form.last_name" type="text" class="input" placeholder="Seu sobrenome" />
            </div>

            <div class="form-group">
              <label class="label">E-mail (Não editável)</label>
              <input v-model="form.email" type="email" disabled class="input disabled-input" />
            </div>

            <div class="form-group">
              <label class="label">CPF</label>
              <input v-model="form.cpf" type="text" class="input" placeholder="000.000.000-00" />
            </div>

            <div class="form-group">
              <label class="label">Telefone</label>
              <input v-model="form.phone" type="text" class="input" placeholder="(00) 00000-0000" />
            </div>
          </div>
        </section>

        <hr />

        <section class="form-section">
          <h3>📍 Endereço</h3>
          <div class="grid-layout">
            
            <div class="form-group">
              <label class="label">CEP</label>
              <input v-model="form.cep" type="text" class="input" placeholder="00000-000" />
            </div>

            <div class="form-group span-2">
              <label class="label">Rua / Avenida</label>
              <input v-model="form.street" type="text" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Número</label>
              <input v-model="form.number" type="text" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Complemento</label>
              <input v-model="form.complement" type="text" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Bairro</label>
              <input v-model="form.district" type="text" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Cidade</label>
              <input v-model="form.city" type="text" class="input" />
            </div>

            <div class="form-group">
              <label class="label">Estado (UF)</label>
              <input v-model="form.state" type="text" maxlength="2" class="input" placeholder="UF" />
            </div>
          </div>
        </section>

        <hr v-if="!auth.isLibrarian" />

        <section v-if="!auth.isLibrarian" class="form-section">
            <h3>🛡️ Área Administrativa</h3>
             <div class="admin-box">
                <p>Possui uma chave de administrador?</p>
                <button type="button" @click="upgradeAccount" class="btn btn-primary">
                    🔑 Tornar-se Bibliotecário
                </button>
            </div>
        </section>

        <div class="actions">
          <button type="submit" class="btn btn-accent">Salvar Alterações</button>
        </div>

      </form>
    </div>
  </div>
</template>

<style scoped>
.profile-page { max-width: 900px; margin: 0 auto; padding: 30px 20px; }

.profile-header { 
    display: flex; align-items: center; gap: 25px; 
    margin-bottom: 30px;
}

.avatar-circle {
    width: 90px; height: 90px; background: var(--primary); color: white;
    font-size: 2.5rem; font-weight: 800; display: flex; 
    align-items: center; justify-content: center; border-radius: 50%;
    box-shadow: var(--shadow-sm);
}

.header-info h2 { margin: 0; color: var(--primary); font-size: 1.8rem; font-weight: 700; }
.subtitle { color: var(--text-muted); margin: 5px 0 12px; font-size: 1rem; }
.role-badge { 
    padding: 6px 14px; 
    border-radius: 20px; font-size: 0.85rem; font-weight: 700; 
    display: inline-block;
    text-transform: uppercase; letter-spacing: 0.5px;
}
.badge-admin { background: rgba(52, 73, 94, 0.1); color: var(--primary); }
.badge-user { background: rgba(66, 184, 131, 0.1); color: var(--accent); }

.form-container { background: white; border-radius: 12px; }

.form-section h3 { 
    margin-bottom: 25px; color: var(--text-main); 
    border-left: 5px solid var(--accent); padding-left: 15px; 
    font-size: 1.2rem; font-weight: 700;
}

.grid-layout { 
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
    gap: 25px; 
}

.form-group { display: flex; flex-direction: column; gap: 6px; }
.label { font-size: 0.9rem; font-weight: 600; color: var(--text-main); }

.disabled-input { background: #f9f9f9; color: #999; cursor: not-allowed; border-color: #eee; }

.span-2 { grid-column: span 2; }
@media (max-width: 600px) { .span-2 { grid-column: span 1; } }

hr { margin: 40px 0; border: none; border-top: 1px solid var(--border-color); }

.actions { text-align: right; margin-top: 30px; }

.loading { text-align: center; padding: 50px; color: var(--text-muted); font-size: 1.1rem; }

.admin-box { 
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
    padding: 25px; border-radius: var(--radius-md); 
    border: 1px dashed var(--border-color); display: flex; 
    justify-content: space-between; align-items: center; 
    flex-wrap: wrap; gap: 15px;
}
.admin-box p { margin: 0; color: var(--text-main); font-weight: 600; }
</style>
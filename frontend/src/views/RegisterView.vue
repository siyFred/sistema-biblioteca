<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import axios from 'axios'
import { useAlert } from '../utils/alert'

const swal = useAlert()
const router = useRouter()
const step = ref(1) 
const loadingCep = ref(false)
const errorMsg = ref('')

const usernameError = ref('') 
const emailError = ref('') 
let usernameTimeout = null
let emailTimeout = null 

const form = ref({ 
    username: '', email: '', password: '', admin_code: '',
    first_name: '', last_name: '', cpf: '', phone: '',
    cep: '', street: '', number: '', complement: '', district: '', city: '', state: ''
})

const nextStep = () => { 
    if (step.value === 1 && (usernameError.value || emailError.value)) return
    
    if (step.value === 1 && (!form.value.username || !form.value.email || !form.value.password)) {
        swal.error('Atenção', 'Preencha todos os campos antes de continuar.')
        return
    }
    
    if (step.value < 3) step.value++ 
}

const prevStep = () => { if (step.value > 1) step.value-- }

const validateUsername = () => {
    usernameError.value = ''
    clearTimeout(usernameTimeout)
    if (!form.value.username) return

    usernameTimeout = setTimeout(async () => {
        try {
            const { data } = await api.get(`check-username/?username=${form.value.username}`)
            if (data.exists) usernameError.value = "⚠️ Este usuário já está em uso."
        } catch (error) { console.error(error) }
    }, 500)
}

const validateEmail = () => {
    emailError.value = ''
    clearTimeout(emailTimeout)
    
    if (!form.value.email) return

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailPattern.test(form.value.email)) {
        emailError.value = "Formato de e-mail inválido."
        return
    }

    emailTimeout = setTimeout(async () => {
        try {
            const { data } = await api.get(`check-email/?email=${form.value.email}`)
            if (data.exists) emailError.value = "⚠️ Este e-mail já possui cadastro."
        } catch (error) { console.error(error) }
    }, 500)
}

const formatCPF = () => {
    let v = form.value.cpf.replace(/\D/g, '') 
    if (v.length > 11) v = v.substring(0, 11) 
    v = v.replace(/(\d{3})(\d)/, '$1.$2')
    v = v.replace(/(\d{3})(\d)/, '$1.$2')
    v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2')
    form.value.cpf = v
}

const formatPhone = () => {
    let v = form.value.phone.replace(/\D/g, '')
    if (v.length > 11) v = v.substring(0, 11)
    v = v.replace(/^(\d{2})(\d)/g, '($1) $2')
    v = v.replace(/(\d)(\d{4})$/, '$1-$2')
    form.value.phone = v
}

const formatCEP = () => {
    let v = form.value.cep.replace(/\D/g, '')
    if (v.length > 8) v = v.substring(0, 8)
    v = v.replace(/(\d{5})(\d)/, '$1-$2')
    form.value.cep = v
}

const fetchCep = async () => {
    const cepLimpo = form.value.cep.replace(/\D/g, '')
    if (cepLimpo.length !== 8) return

    loadingCep.value = true
    try {
        const { data } = await axios.get(`https://viacep.com.br/ws/${cepLimpo}/json/`)
        
        if (!data.erro) {
            form.value.street = data.logradouro
            form.value.district = data.bairro
            form.value.city = data.localidade
            form.value.state = data.uf
            document.getElementById('number')?.focus()
        } else {
            swal.error('Erro', 'CEP não encontrado!')
        }
    } catch (e) { console.error(e) } 
    finally { loadingCep.value = false }
}

const handleRegister = async () => {
  if (usernameError.value || emailError.value) {
      swal.error('Atenção', 'Corrija os erros antes de continuar.')
      step.value = 1
      return
  }

  try {
    const payload = { ...form.value }
    payload.cpf = payload.cpf.replace(/\D/g, '')   
    payload.phone = payload.phone.replace(/\D/g, '') 
    payload.cep = payload.cep.replace(/\D/g, '')     

    await api.post('register/', payload)
    swal.success('Cadastro realizado!', 'Bem-vindo(a) ao KotarLib.')
    router.push('/')
  } catch (error) {
    const data = error.response?.data
    if (data?.username) errorMsg.value = "Usuário já existe."
    else if (data?.email) errorMsg.value = "Email já existe."
    else if (data?.cpf) errorMsg.value = "CPF já cadastrado."
    else {
        errorMsg.value = "Erro no cadastro."
        swal.error('Erro', 'Erro no cadastro. Verifique os campos.')
    }
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="card auth-card">
      <div class="progress-bar">
        <div :class="['step-dot', { active: step >= 1 }]">1</div>
        <div class="line"></div>
        <div :class="['step-dot', { active: step >= 2 }]">2</div>
        <div class="line"></div>
        <div :class="['step-dot', { active: step >= 3 }]">3</div>
      </div>

      <h2 v-if="step === 1">Criar Conta</h2>
      <h2 v-if="step === 2">Quem é você?</h2>
      <h2 v-if="step === 3">Onde você mora?</h2>

      <form @submit.prevent="handleRegister">
        
        <div v-show="step === 1" class="step-content">
            <div class="mb-3 text-left">
                <label class="label">Usuário</label>
                <input 
                    v-model="form.username" 
                    @input="validateUsername"
                    class="input"
                    placeholder="Login para entrar" 
                    required 
                    :class="{ 'input-error': usernameError }"
                />
                <small v-if="usernameError" class="live-error">{{ usernameError }}</small>
            </div>

            <div class="mb-3 text-left">
                <label class="label">Email</label>
                <input 
                    v-model="form.email" 
                    type="email" 
                    class="input"
                    @input="validateEmail"
                    placeholder="seu@email.com" 
                    required
                    :class="{ 'input-error': emailError }"
                />
                <small v-if="emailError" class="live-error">{{ emailError }}</small>
            </div>

            <div class="mb-3 text-left">
                <label class="label">Senha</label>
                <input v-model="form.password" type="password" class="input" placeholder="******" required />
            </div>
        </div>

        <div v-show="step === 2" class="step-content">
            <div class="row">
                <div class="mb-3 text-left w-full">
                    <label class="label">Nome</label>
                    <input v-model="form.first_name" class="input" required />
                </div>
                <div class="mb-3 text-left w-full">
                    <label class="label">Sobrenome</label>
                    <input v-model="form.last_name" class="input" required />
                </div>
            </div>
            <div class="mb-3 text-left">
                <label class="label">CPF</label>
                <input v-model="form.cpf" @input="formatCPF" class="input" placeholder="000.000.000-00" required maxlength="14" />
            </div>
            <div class="mb-3 text-left">
                <label class="label">Celular</label>
                <input v-model="form.phone" @input="formatPhone" class="input" placeholder="(00) 00000-0000" required maxlength="15" />
            </div>

            <div class="mb-3 text-left">
                <label class="label">Código de Bibliotecário (Opcional)</label>
                <input v-model="form.admin_code" class="input" placeholder="Chave Mestra..." type="password" />
            </div>
        </div>

        <div v-show="step === 3" class="step-content">
            <div class="row">
                <div class="mb-3 text-left" style="flex: 1">
                    <label class="label">CEP</label>
                    <input v-model="form.cep" @input="formatCEP" @blur="fetchCep" class="input" placeholder="00000-000" maxlength="9" />
                    <small v-if="loadingCep" class="loading-text">Buscando...</small>
                </div>
                <div class="mb-3 text-left" style="flex: 2">
                    <label class="label">Cidade/UF</label>
                    <input :value="form.city + (form.state ? ' - ' + form.state : '')" readonly disabled class="input read-only" />
                </div>
            </div>
            <div class="mb-3 text-left">
                <label class="label">Rua</label>
                <input v-model="form.street" class="input" placeholder="Logradouro..." />
            </div>
            <div class="row">
                <div class="mb-3 text-left" style="flex: 1">
                    <label class="label">Número</label>
                    <input id="number" v-model="form.number" class="input" placeholder="Nº" required />
                </div>
                <div class="mb-3 text-left" style="flex: 2">
                    <label class="label">Bairro</label>
                    <input v-model="form.district" class="input" />
                </div>
            </div>
            <div class="mb-3 text-left">
                <label class="label">Complemento</label>
                <input v-model="form.complement" class="input" placeholder="Apto, Bloco..." />
            </div>
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <div class="actions">
            <button v-if="step > 1" type="button" class="btn btn-outline" @click="prevStep">Voltar</button>
            
            <button 
                v-if="step < 3" 
                type="button" 
                class="btn btn-primary" 
                @click="nextStep" 
                :disabled="(step === 1 && (!!usernameError || !!emailError))"
            >
                Próximo
            </button>
            
            <button v-if="step === 3" type="submit" class="btn btn-accent">Finalizar Cadastro</button>
        </div>

      </form>
      <p class="link">Já tem conta? <router-link to="/">Faça Login</router-link></p>
    </div>
  </div>
</template>

<style scoped>
.auth-container { 
  min-height: 100vh; 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  padding: 20px; 
  background: var(--background);
  background-image: radial-gradient(#e0e0e0 1px, transparent 1px);
  background-size: 20px 20px;
}

.auth-card { width: 100%; max-width: 500px; text-align: center; }

/* STEPS */
.progress-bar { display: flex; align-items: center; justify-content: center; margin-bottom: 25px; }
.step-dot { width: 32px; height: 32px; background: #e0e0e0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #777; transition: 0.3s; z-index: 2; font-size: 0.9rem; }
.step-dot.active { background: var(--primary); color: white; transform: scale(1.1); box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
.line { width: 40px; height: 3px; background: #e0e0e0; margin: 0 -5px; z-index: 1; }

h2 { text-align: center; color: var(--primary); margin-bottom: 25px; font-size: 1.5rem; font-weight: 700; }

.step-content { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateX(10px); } to { opacity: 1; transform: translateX(0); } }

/* UTILS */
.row { display: flex; gap: 15px; }
.label { display: block; font-size: 0.85rem; font-weight: 600; color: var(--text-main); margin-bottom: 6px; }
.text-left { text-align: left; }

.read-only { background: #f9f9f9; color: #777; cursor: not-allowed; border-color: #eee; }
.input-error { border-color: var(--danger) !important; background-color: #fff5f5; }
.live-error { color: var(--danger); font-size: 0.8rem; font-weight: bold; margin-top: 4px; display: block; animation: fadeIn 0.3s; }
.loading-text { color: var(--info); font-weight: bold; font-size: 0.8rem; margin-top: 2px; }

.error-msg { 
  color: var(--danger); 
  font-size: 0.9rem; 
  margin-top: 15px; 
  background: rgba(231, 76, 60, 0.1); 
  padding: 10px; 
  border-radius: var(--radius-sm); 
  border: 1px solid rgba(231, 76, 60, 0.2);
}

.actions { display: flex; justify-content: space-between; margin-top: 30px; gap: 15px; }
.actions button { flex: 1; }

.link { text-align: center; margin-top: 20px; font-size: 0.9rem; color: var(--text-muted); }
</style>
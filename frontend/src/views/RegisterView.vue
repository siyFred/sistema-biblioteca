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
    <div class="card">
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
            <div class="input-group">
                <label>Usuário</label>
                <input 
                    v-model="form.username" 
                    @input="validateUsername"
                    placeholder="Login para entrar" 
                    required 
                    :class="{ 'input-error': usernameError }"
                />
                <small v-if="usernameError" class="live-error">{{ usernameError }}</small>
            </div>

            <div class="input-group">
                <label>Email</label>
                <input 
                    v-model="form.email" 
                    type="email" 
                    @input="validateEmail"
                    placeholder="seu@email.com" 
                    required
                    :class="{ 'input-error': emailError }"
                />
                <small v-if="emailError" class="live-error">{{ emailError }}</small>
            </div>

            <div class="input-group">
                <label>Senha</label>
                <input v-model="form.password" type="password" placeholder="******" required />
            </div>
        </div>

        <div v-show="step === 2" class="step-content">
            <div class="row">
                <div class="input-group">
                    <label>Nome</label>
                    <input v-model="form.first_name" required />
                </div>
                <div class="input-group">
                    <label>Sobrenome</label>
                    <input v-model="form.last_name" required />
                </div>
            </div>
            <div class="input-group">
                <label>CPF</label>
                <input v-model="form.cpf" @input="formatCPF" placeholder="000.000.000-00" required maxlength="14" />
            </div>
            <div class="input-group">
                <label>Celular</label>
                <input v-model="form.phone" @input="formatPhone" placeholder="(00) 00000-0000" required maxlength="15" />
            </div>

            <div class="input-group">
                <label>Código de Bibliotecário (Opcional)</label>
                <input v-model="form.admin_code" placeholder="Chave Mestra..." type="password" />
            </div>
        </div>

        <div v-show="step === 3" class="step-content">
            <div class="row">
                <div class="input-group" style="flex: 1">
                    <label>CEP</label>
                    <input v-model="form.cep" @input="formatCEP" @blur="fetchCep" placeholder="00000-000" maxlength="9" />
                    <small v-if="loadingCep" class="loading-text">Buscando...</small>
                </div>
                <div class="input-group" style="flex: 2">
                    <label>Cidade/UF</label>
                    <input :value="form.city + (form.state ? ' - ' + form.state : '')" readonly disabled class="read-only" />
                </div>
            </div>
            <div class="input-group">
                <label>Rua</label>
                <input v-model="form.street" placeholder="Logradouro..." />
            </div>
            <div class="row">
                <div class="input-group" style="flex: 1">
                    <label>Número</label>
                    <input id="number" v-model="form.number" placeholder="Nº" required />
                </div>
                <div class="input-group" style="flex: 2">
                    <label>Bairro</label>
                    <input v-model="form.district" />
                </div>
            </div>
            <div class="input-group">
                <label>Complemento</label>
                <input v-model="form.complement" placeholder="Apto, Bloco..." />
            </div>
        </div>

        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>

        <div class="actions">
            <button v-if="step > 1" type="button" class="btn-secondary" @click="prevStep">Voltar</button>
            
            <button 
                v-if="step < 3" 
                type="button" 
                class="btn-primary" 
                @click="nextStep" 
                :disabled="(step === 1 && (!!usernameError || !!emailError))"
            >
                Próximo
            </button>
            
            <button v-if="step === 3" type="submit" class="btn-success">Finalizar Cadastro</button>
        </div>

      </form>
      <p class="link">Já tem conta? <router-link to="/">Faça Login</router-link></p>
    </div>
  </div>
</template>

<style scoped>
.auth-container { min-height: 100vh; display: flex; justify-content: center; align-items: center; background: #eef2f5; padding: 20px; }
.card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); width: 100%; max-width: 450px; }

.progress-bar { display: flex; align-items: center; justify-content: center; margin-bottom: 25px; }
.step-dot { width: 32px; height: 32px; background: #e0e0e0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #777; transition: 0.3s; z-index: 2; }
.step-dot.active { background: #2c3e50; color: white; transform: scale(1.1); }
.line { width: 40px; height: 3px; background: #e0e0e0; margin: 0 -5px; z-index: 1; }

h2 { text-align: center; color: #2c3e50; margin-bottom: 20px; font-size: 1.4rem; }

.step-content { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateX(10px); } to { opacity: 1; transform: translateX(0); } }

.row { display: flex; gap: 10px; }
.input-group { margin-bottom: 12px; display: flex; flex-direction: column; text-align: left; }
label { font-size: 0.85rem; font-weight: bold; color: #666; margin-bottom: 4px; }
input { padding: 10px; border: 1px solid #ddd; border-radius: 6px; width: 100%; box-sizing: border-box; font-size: 0.95rem; transition: 0.2s; }

input:focus { border-color: #42b883; outline: none; box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1); }
input.read-only { background: #f9f9f9; color: #777; cursor: not-allowed; border-color: #eee; }

.input-error { border-color: #e74c3c !important; background-color: #fdf2f2; }
.live-error { color: #e74c3c; font-size: 0.8rem; font-weight: bold; margin-top: 4px; display: block; animation: fadeIn 0.3s; }
.loading-text { color: #3498db; font-weight: bold; font-size: 0.8rem; margin-top: 2px; }

.actions { display: flex; justify-content: space-between; margin-top: 25px; gap: 10px; }
button { flex: 1; padding: 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; font-size: 1rem; }

.btn-primary { background: #2c3e50; color: white; }
.btn-primary:hover { background: #34495e; }
button:disabled { background: #bdc3c7; cursor: not-allowed; opacity: 0.7; }

.btn-secondary { background: #ecf0f1; color: #2c3e50; }
.btn-secondary:hover { background: #bdc3c7; }
.btn-success { background: #42b883; color: white; }
.btn-success:hover { background: #2ecc71; }

.error { color: #e74c3c; font-size: 0.9rem; text-align: center; margin-top: 15px; background: #fadbd8; padding: 10px; border-radius: 6px; }
.link { text-align: center; margin-top: 20px; font-size: 0.9rem; color: #666; }
a { color: #42b883; font-weight: bold; text-decoration: none; }
</style>
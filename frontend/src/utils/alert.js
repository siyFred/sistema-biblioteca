import Swal from 'sweetalert2'

// Configuração padrão das cores do seu tema
const colors = {
    confirm: '#42b883', // Verde do Vue
    cancel: '#e74c3c'   // Vermelho
}

export const useAlert = () => {
    
    // 1. Alerta de Sucesso (Canto superior direito, some sozinho)
    const success = (title) => {
        Swal.fire({
            icon: 'success',
            title: title,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            background: '#fff',
            iconColor: colors.confirm
        })
    }

    // 2. Alerta de Erro (Modal central)
    const error = (title, text = '') => {
        Swal.fire({
            icon: 'error',
            title: title,
            text: text,
            confirmButtonColor: colors.confirm
        })
    }

    // 3. Confirmação (Sim/Não) - Retorna uma Promise
    const confirm = async (title, text = 'Essa ação não pode ser desfeita.') => {
        const result = await Swal.fire({
            title: title,
            text: text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: colors.confirm,
            cancelButtonColor: colors.cancel,
            confirmButtonText: 'Sim, confirmar!',
            cancelButtonText: 'Cancelar'
        })
        return result.isConfirmed
    }

    return { success, error, confirm }
}
# sistema-biblioteca

Este projeto é um sistema robusto de gerenciamento de biblioteca desenvolvido com foco em boas práticas de backend e frontend. O sistema permite o gerenciamento completo de livros, usuários e empréstimos, com controle de estoque, multas e notificações.

## Tecnologias Utilizadas

### Backend
*   **Django 5 & Django Rest Framework (DRF):** Framework principal.
*   **PostgreSQL 17:** Banco de dados relacional.
*   **Redis:** Cache e Message Broker.
*   **Celery:** Processamento assíncrono (background tasks).
*   **JWT (Simple JWT):** Autenticação segura.
*   **Drf-spectacular:** Documentação OpenAPI/Swagger.

### Frontend
*   **Vue.js 3:** Framework reativo (Composition API).
*   **Vite:** Build tool ultra-rápido.
*   **Axios:** Cliente HTTP.

### Infraestrutura
*   **Docker & Docker Compose:** Containerização completa do ambiente.

---

## Como Rodar

Você pode rodar o projeto de duas formas: usando **Docker** (recomendado para simplicidade) ou **Localmente** (para desenvolvimento).

### Opção 1: Com Docker (Recomendado)

Certifique-se de ter o Docker e Docker Compose instalados.

1.  **Configure o ambiente:**
    Crie um arquivo `.env` na raiz do projeto (baseado nas variáveis listadas abaixo).

2.  **Execute o comando:**
    ```bash
    docker-compose up --build
    ```

3.  **Acesse:**
    *   **Frontend:** http://localhost:5173
    *   **Backend API:** http://localhost:8000/api/
    *   **Swagger Docs:** http://localhost:8000/api/schema/swagger-ui/

### Opção 2: Rodar Localmente

#### Pré-requisitos
*   Python 3.12+
*   Node.js 18+
*   PostgreSQL rodando localmente (ou via Docker)
*   Redis rodando localmente (ou via Docker)

#### 1. Configurar Backend

```bash
cd backend
# Crie e ative o ambiente virtual
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure o .env na raiz (veja a seção Variáveis de Ambiente abaixo)
# IMPORTANTE: Para rodar localmente, ajuste os hosts do DB e Redis:
# POSTGRES_HOST=localhost
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Execute as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# Rode o servidor
python manage.py runserver
```

**Para rodar o Celery (em outro terminal):**
```bash
cd backend
.\venv\Scripts\activate
celery -A sistema_biblioteca worker -l info
```

#### 2. Configurar Frontend

```bash
cd frontend
# Instale as dependências
npm install

# Rode o servidor de dev
npm run dev
```

---

## Variáveis de Ambiente (.env)

Crie um arquivo `.env` na RAIZ do projeto com as seguintes chaves. Ajuste os valores conforme seu ambiente.

```ini
# Django
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Banco de Dados (PostgreSQL)
POSTGRES_DB=biblioteca_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
# Se rodar com Docker: "db". Se rodar local: "localhost"
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis / Celery
# Se rodar com Docker: "redis://redis:6379/0". Se rodar local: "redis://localhost:6379/0"
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Regras de Negócio
# Valor da multa diária por atraso
FINE_DAILY_AMOUNT=1.50
```
# sistema-biblioteca

Este projeto é um sistema de gerenciamento de biblioteca desenvolvido como requisito para as disciplinas de Backend e Frontend Frameworks.

* **Backend:** Django 5 (Django Rest Framework)
* **Frontend:** Vue.js 3 (Composition API + Vite)
* **Banco de Dados:** PostgreSQL 17
* **Infraestrutura:** Docker & Docker Compose
* **Documentação:** Swagger/OpenAPI (drf-spectacular)

---

# Tasks

## MVP (Fase 1)

### Infraestrutura e Configuração (Docker)

- [x] **Docker Containers:** Orquestração dos serviços (App, DB, Broker, Worker) com Healthchecks e dependências de inicialização (`depends_on`).
- [x] **Persistência de Dados:** Configuração de volumes para persistência de dados do Postgres e Redis.
- [x] **Segurança:** Segregação de variáveis sensíveis via `.env`.

### Backend e Segurança

- [x] **Autenticação:** Implementação de JWT (Access + Refresh Tokens) com rotação de chaves.
- [x] **Controle de Acesso (RBAC):** Definição de permissões granulares para Bibliotecários vs Usuários Comuns.
- [x] **Documentação:** Geração automática de documentação OpenAPI 3.0 (Swagger) para consumo do Frontend.

### Lógica de Negócio e Integrações Externas

- [x] **Padrão/Pattern Service Layer:** Desacoplamento da lógica de negócio das Views/Controllers.
- [x] **Adapter Externo (Google Books):** Serviço robusto de importação de metadados via ISBN, tratando timeouts e falhas de API externa.
- [x] **Data Normalization:** Estratégia de armazenamento de capas (URLs vs Blobs) e categorização.
- [x] **Advanced Filtering:** Implementação de busca textual (Full-Text Search) e filtros dinâmicos no endpoint de acervo.

### Performance e Concorrência

- [x] **ACID Transactions:** Controle de integridade na criação de empréstimos.
- [x] **Concurrency Control:** Implementação de `select_for_update` (Row locking) para evitar Race Conditions no estoque de livros.
- [x] **Async Pipelines (Celery):** Processamento em background para notificações e relatórios pesados, evitando bloqueio da thread principal.
- [ ] **Caching:** Cacheamento de endpoints de leitura frequente (ex: Listagem de Livros) com invalidação inteligente.

### Frontend e UX

- [ ] **Gerenciamento de Estado (Pinia):** Stores modulares para Auth e Carrinho de Empréstimos.
- [ ] **Abstração API Client:** Configuração do Axios com Interceptors para injeção automática de Token e tratamento global de erros (401/403).
- [ ] **Reutilização de Componentes:** Criação de componentes atômicos (Cards, Inputs, Modais) para padronização visual.
- [ ] **Interface otimizada:** Interface otimizada para o fluxo de "Scan & Import" de livros via ISBN.
---
title: "Sistema de Biblioteca Full-Stack com Automação de Empréstimos e Multas"
description: "Plataforma de gestão de biblioteca com controle transacional de acervo, autenticação JWT e processamento assíncrono de regras de negócio."
stack: ["Python", "Django", "Django REST Framework", "PostgreSQL", "Redis", "Celery", "Vue 3", "Vite", "Docker", "JWT"]
images: ["assets/capa.png"]
featured-skills: ["Arquitetura de APIs REST", "Mensageria Assíncrona", "Modelagem de Domínio"]
---

> `assets/capa.png` é um placeholder intencional para integração com o pipeline de imagens do portfólio.

## Visão do Projeto

Sistema de gestão de biblioteca com foco em **operações reais de acervo**: cadastro e descoberta de livros, solicitações de empréstimo, aprovação por bibliotecário, devolução, cálculo de multas e governança de usuários por perfil.

A solução foi desenhada para separar responsabilidades entre:
- **Core transacional** (Django + PostgreSQL)
- **Processamento assíncrono de regras temporais** (Celery + Redis)
- **Experiência de uso orientada a papéis** (Vue 3, leitor vs. bibliotecário)

## Objetivos de Engenharia

- Garantir integridade de estoque em cenários concorrentes de empréstimo/devolução.
- Reduzir acoplamento entre ações síncronas da API e tarefas periódicas de negócio.
- Sustentar evolução do produto com API documentada, autenticação stateless e frontend desacoplado.

## Arquitetura

### Backend orientado a domínio (Django Apps)

O backend é modularizado em apps com fronteiras claras:
- `users`: autenticação/autorização e gestão de perfis.
- `books`: catálogo, filtros, busca híbrida e solicitações de compra.
- `loans`: ciclo de vida de empréstimos, atraso, pagamento e multas.

A API REST usa DRF com:
- **JWT (SimpleJWT)** para autenticação stateless.
- **Filtros, busca textual e ordenação** para consultas de acervo/empréstimos.
- **Permissões por papel** para separar leitura pública e operações administrativas.

### Processamento assíncrono e temporal

As regras de atraso/multa são processadas com Celery (broker/backend em Redis), incluindo rotina agendada diária:

```python
CELERY_BEAT_SCHEDULE = {
    'check-overdue-loans-every-day': {
        'task': 'loans.tasks.check_overdue_loans',
        'schedule': crontab(hour=0, minute=0),
    },
}
```

Isso evita depender de requisições de usuários para manter o estado financeiro atualizado.

### Frontend SPA orientado por rotas protegidas

A aplicação Vue 3 usa roteamento com guarda de autenticação e áreas distintas para operações administrativas (`/admin/*`) e fluxo do leitor (`/books`, `/loans`, `/profile`).

## Decisões Técnicas Relevantes

### 1) Integridade de estoque com transação e lock pessimista

No fluxo de criação/retorno de empréstimos, o livro é atualizado com `select_for_update` dentro de `transaction.atomic()`, prevenindo corrida entre requisições concorrentes:

```python
with transaction.atomic():
    book_locked = Book.objects.select_for_update().get(pk=book.pk)
    if book_locked.available_copies <= 0:
        raise exceptions.ValidationError('Este livro não está disponível no momento.')
    book_locked.available_copies -= 1
    book_locked.save()
```

**Por quê:** evita inconsistência de `available_copies` sob alta simultaneidade.

### 2) Modelagem explícita do ciclo de vida de empréstimo

`Loan` trabalha com estados (`PENDING`, `ACTIVE`, `OVERDUE`, `RETURNED`, `REJECTED`) e campos financeiros (`fine_amount`, `paid`, `paid_date`, `fine_last_updated`).

**Como isso resolve o problema:** centraliza regras de negócio no domínio e torna rastreável cada transição operacional e financeira.
O fluxo segue `PENDING -> ACTIVE -> RETURNED` (ou `REJECTED`), com `OVERDUE` sendo aplicado por rotina diária; `fine_last_updated` é avançado tanto no job agendado quanto no fechamento do empréstimo (`return_book`), evitando recalcular dias já cobrados.

### 3) Busca híbrida (acervo local + Google Books)

O sistema combina pesquisa local (dados institucionais) com integração externa para descoberta via Google Books API.

**Benefício:** amplia catálogo percebido pelo usuário sem poluir o banco principal com dados não curados.

### 4) Infraestrutura reproduzível por contêineres

`docker-compose` sobe frontend, backend, worker Celery, PostgreSQL e Redis em stack única.

**Por quê:** reduz fricção entre ambientes e acelera onboarding técnico.

## Escopo Funcional Entregue

- Cadastro e gestão de livros com metadados e capa.
- Solicitação, aprovação/rejeição e devolução de empréstimos.
- Cálculo de multa por atraso com atualização periódica automática.
- Gestão de usuários com papéis de leitor e bibliotecário.
- Painéis com métricas operacionais para apoio à gestão.
- API documentável (OpenAPI/Swagger) para integração e manutenção.

## Resultado Técnico

Projeto full-stack com foco em **consistência transacional, separação de responsabilidades e escalabilidade funcional**, aplicando padrões práticos de engenharia para produtos de operação contínua.

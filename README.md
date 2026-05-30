# Delart-flask

Projeto Flask sobre Delart Estética Automotiva. Conta com login e CRUD básico de agendamentos usando Flask e sqlite3.

O sistema possui CRUD HTML completo de agendamentos, com cadastro, listagem, detalhes, edição, remoção e filtros por string de consulta.

## Endpoints

| Método | Endpoint | Função |
|---|---|---|
| `GET` | `/` | Renderiza a página de cadastro |
| `GET` | `/agendamentos` | Lista todos os agendamentos do usuário logado (HTML) |
| `GET` | `/agendamentos/novo` | Formulário HTML para novo agendamento |
| `POST` | `/agendamentos/novo` | Cria um novo agendamento (HTML) |
| `GET` | `/agendamentos/<id>` | Detalhes do agendamento (HTML) |
| `GET` | `/agendamentos/<id>/editar` | Formulário de edição (HTML) |
| `POST` | `/agendamentos/<id>/editar` | Atualiza um agendamento (HTML) |
| `POST` | `/agendamentos/<id>/remover` | Remove um agendamento (HTML) |

---

## `GET /`

Renderiza a página inicial de cadastro.

**Retorno:**

```html
cadastro.html
```

---

## `GET /agendamentos`

Lista todos os agendamentos cadastrados do usuário logado (HTML). Aceita filtros por query string:

- `/agendamentos?busca=texto`
- `/agendamentos?status=0`
- `/agendamentos?status=1`
- `/agendamentos?status=2`

---

## `GET /agendamentos/<id>`

Exibe os detalhes de um agendamento específico pelo ID (HTML).

---

## CRUD HTML

O CRUD principal é feito por formulários HTML com redirecionamentos:

- Cadastro: `/agendamentos/novo`
- Edição: `/agendamentos/<id>/editar`
- Remoção: `/agendamentos/<id>/remover`

---

## Endpoints JSON (opcional)

Os endpoints JSON continuam disponíveis para compatibilidade:

- `GET /api/agendamentos`
- `GET /api/agendamentos/<id>`
- `POST /criar-agendamento`
- `PUT /agendamentos/<id>`
- `DELETE /agendamentos/<id>`

---

## Status dos agendamentos

| Código | Significado |
|---|---|
| `0` | Pendente |
| `1` | Confirmado |
| `2` | Finalizado |
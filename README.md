# Delart-flask

Projeto Flask sobre Delart Estética Automotiva. Conta com login e CRUD básico de agendamentos usando Flask e SQLAlchemy.

## Endpoints

| Método | Endpoint | Função |
|---|---|---|
| `GET` | `/` | Renderiza a página de cadastro |
| `GET` | `/agendamentos` | Lista todos os agendamentos |
| `GET` | `/agendamentos/<id>` | Busca um agendamento específico |
| `POST` | `/criar-agendamento` | Cria um novo agendamento |
| `PUT` | `/agendamentos/<id>` | Atualiza um agendamento existente |
| `DELETE` | `/agendamentos/<id>` | Remove um agendamento |

---

## `GET /`

Renderiza a página inicial de cadastro.

**Retorno:**

```html
cadastro.html
```

---

## `GET /agendamentos`

Lista todos os agendamentos cadastrados.

**Retorno esperado:**

```json
{
  "agendamentos": [
    {
      "id": 1,
      "agendamento_user": 1,
      "titulo": "Lavagem completa",
      "descricao": "Lavagem externa e interna do veículo",
      "status": 1
    }
  ]
}
```

---

## `GET /agendamentos/<id>`

Busca um agendamento específico pelo ID.

**Retorno esperado:**

```json
{
  "agendamento": {
    "id": 1,
    "agendamento_user": 1,
    "titulo": "Lavagem completa",
    "descricao": "Lavagem externa e interna do veículo",
    "status": 1
  }
}
```

**Caso não encontre:**

```json
{
  "message": "Agendamento não encontrado"
}
```

---

## `POST /criar-agendamento`

Cria um novo agendamento.

**Exemplo de envio:**

```json
{
  "agendamento_user": 1,
  "titulo": "Polimento",
  "descricao": "Polimento técnico automotivo",
  "status": 1
}
```

**Retorno esperado:**

```json
{
  "message": "Agendamento criado com sucesso",
  "agendamento": {
    "id": 1,
    "agendamento_user": 1,
    "titulo": "Polimento",
    "descricao": "Polimento técnico automotivo",
    "status": 1
  }
}
```

---

## `PUT /agendamentos/<id>`

Atualiza um agendamento existente.

**Exemplo de envio:**

```json
{
  "titulo": "Polimento atualizado",
  "descricao": "Polimento técnico com vitrificação",
  "status": 2
}
```

**Retorno esperado:**

```json
{
  "message": "Agendamento atualizado com sucesso",
  "agendamento": {
    "id": 1,
    "agendamento_user": 1,
    "titulo": "Polimento atualizado",
    "descricao": "Polimento técnico com vitrificação",
    "status": 2
  }
}
```

**Caso não encontre:**

```json
{
  "message": "Agendamento não encontrado"
}
```

---

## `DELETE /agendamentos/<id>`

Remove um agendamento pelo ID.

**Retorno esperado:**

```json
{
  "message": "Agendamento deletado com sucesso"
}
```

**Caso não encontre:**

```json
{
  "message": "Agendamento não encontrado"
}
```

---

## Status dos agendamentos

| Código | Significado |
|---|---|
| `0` | Pendente |
| `1` | Confirmado |
| `2` | Finalizado |
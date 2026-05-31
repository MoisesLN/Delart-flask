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

# Delart Flask

## Descrição do projeto
Aplicação web desenvolvida com Flask para gerenciamento de agendamentos de serviços. Possui cadastro de usuários, login, logout, controle de sessão e CRUD completo de agendamentos. Os dados são persistidos em banco SQLite3.

## Tema da aplicação
Sistema de gerenciamento de agendamentos/serviços para estética automotiva.

## Problema que a aplicação resolve
Organiza e centraliza os registros de agendamentos. Usuários autenticados podem gerenciar apenas os próprios agendamentos, garantindo controle e praticidade.

## Funcionalidades principais
- cadastro de usuários;
- login de usuários;
- logout;
- controle de sessão;
- área interna protegida;
- cadastro de agendamentos;
- listagem de agendamentos;
- visualização de detalhes;
- edição de agendamentos;
- remoção de agendamentos;
- filtro por busca/status usando string de consulta;
- uso de banco SQLite3.

## Tecnologias utilizadas
- Python
- Flask
- sqlite3
- HTML
- CSS
- JavaScript
- pytest

## Estrutura básica do projeto
```txt
app/
├── app.py
├── db.py
├── database.db
├── templates/
├── static/
└── requirements.txt
tests/
└── test_app.py
README.md
```

## Como instalar e executar
1) Clone o repositório e entre na pasta do projeto:

git clone LINK_DO_REPOSITORIO
cd NOME_DA_PASTA

2) Crie e ative o ambiente virtual:

Windows:
venv\Scripts\activate

Linux/macOS:
source venv/bin/activate

3) Instale as dependências:

pip install -r requirements.txt

4) Execute a aplicação:

python app.py

A aplicação estará disponível em:
http://127.0.0.1:5000

## Como executar os testes
Com o ambiente virtual ativo, execute:

pytest

## Banco de dados
O projeto utiliza SQLite3 com arquivo .db. O banco é criado/inicializado automaticamente pela função init_db() na inicialização do app. Existem duas tabelas principais:

- usuarios
- agendamentos

Não é utilizado ORM ou SQLAlchemy.

## Sessões de usuário
A aplicação usa session do Flask. Após o login, o id e o nome do usuário são armazenados na sessão. Rotas protegidas verificam se o usuário está logado e, no logout, a sessão é limpa.

## Rotas principais
| Rota | Método | Descrição |
|---|---|---|
| / | GET, POST | Página inicial e cadastro de usuário |
| /login | GET, POST | Login |
| /logout | GET | Logout |
| /dashboard | GET | Área interna |
| /agendamentos | GET | Lista agendamentos (HTML) |
| /agendamentos/novo | GET, POST | Cadastra agendamento |
| /agendamentos/<id> | GET | Mostra detalhes |
| /agendamentos/<id>/editar | GET, POST | Edita agendamento |
| /agendamentos/<id>/remover | POST | Remove agendamento |

## Exemplos de string de consulta
Filtros disponíveis na listagem:

- /agendamentos?busca=corte
- /agendamentos?status=1
- /agendamentos?busca=corte&status=1

## Observações para avaliação
Projeto atende aos requisitos de rotas Flask, templates com herança, arquivos estáticos, formulários GET/POST, sessões, SQLite3, CRUD completo, string de consulta e rotas parametrizadas.

## Integrantes
- Nome 1
- Nome 2
- Nome 3

## Repositório
Link: COLOCAR_LINK_DO_GITHUB_AQUI
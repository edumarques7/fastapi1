# ⚡ FastAPI1 · API de usuários e artigos

API REST de estudo construída com **FastAPI**, **PostgreSQL** e **SQLAlchemy assíncrono**. Permite cadastrar usuários, autenticar com JWT e publicar artigos vinculados a um autor.

**[Começar](#-como-rodar-localmente)** · **[Testar com Postman](#-testando-com-postman)** · **[Rotas](#-rotas-da-api)** · **[Limitações](#-limitações-e-cuidados)**

## ✨ O que o projeto faz

- Cadastro e consulta de usuários, incluindo seus artigos.
- Hash de senhas com Passlib e bcrypt.
- Login no formato OAuth2 Password e emissão de JWT.
- Criação, listagem, consulta, atualização e exclusão de artigos.
- Validação de e-mail e URL com Pydantic.
- Documentação interativa em Swagger UI e ReDoc.
- Acesso assíncrono ao PostgreSQL com `asyncpg`.

> O projeto possui limitações de autorização e configuração descritas ao final. Use um banco local de desenvolvimento para seguir este guia.

## 🧰 Stack

| Componente | Versão no projeto | Papel |
| --- | --- | --- |
| Python | Série 3.10 | Runtime; os arquivos de implantação indicam 3.10.12 |
| FastAPI | 0.75.2 | Rotas, dependências e OpenAPI |
| Pydantic | 1.9.0 | Schemas e configurações |
| SQLAlchemy | 1.4.36 | Modelos e sessões assíncronas |
| asyncpg | 0.25.0 | Driver PostgreSQL |
| Uvicorn | 0.17.6 | Servidor ASGI |
| python-jose | 3.3.0 | Assinatura e validação JWT |
| Passlib | 1.7.4 | Hash e verificação de senhas |

O guia complementa a instalação com `bcrypt==3.2.2`, ausente do `requirements.txt` e validado com esta versão do Passlib. Para reproduzir o ambiente, mantenha as versões fixadas; não atualize isoladamente para Pydantic 2 ou SQLAlchemy 2.

## 🚀 Como rodar localmente

### 1. Pré-requisitos

- Git e **Python 3.10**.
- PostgreSQL local; este guia foi validado com PostgreSQL 15.
- Postman Desktop para os testes.
- Docker apenas se você escolher iniciar o banco em um container.

### 2. Clone e prepare o ambiente

```bash
git clone https://github.com/edumarques7/fastapi1.git
cd fastapi1
```

**Linux / macOS:**

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

**Windows — PowerShell:**

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se a ativação for bloqueada no PowerShell, use `.\.venv\Scripts\python.exe` em vez de `python` nos próximos comandos.

Instale as dependências:

```bash
python -m pip install -r requirements.txt
python -m pip install bcrypt==3.2.2
```

### 3. Prepare um banco exclusivo para desenvolvimento

Se você já tem PostgreSQL, crie um banco vazio chamado `fastapi1` e use suas credenciais na próxima etapa.

Como alternativa, com o Docker em execução, este comando inicia somente um PostgreSQL local. Ele funciona em uma única linha no Bash e no PowerShell:

```bash
docker run --name fastapi1-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=senha_local_dev -e POSTGRES_DB=fastapi1 -p 127.0.0.1:5432:5432 -v fastapi1-pgdata:/var/lib/postgresql/data -d postgres:15-alpine
```

A senha acima é apenas um exemplo para desenvolvimento. Aguarde o banco aceitar conexões:

```bash
docker exec fastapi1-postgres pg_isready -U postgres -d fastapi1
```

Se a porta 5432 já estiver ocupada, use `127.0.0.1:5433:5432` no mapeamento e `5433` na `DB_URL`. Para parar e retomar esse container, use `docker stop fastapi1-postgres` e `docker start fastapi1-postgres`. O volume mantém os dados.

### 4. Configure o banco e a chave JWT

**Defina estas variáveis antes de executar qualquer script da aplicação.** O código possui uma URL remota e uma chave JWT fixas como valores padrão; este guia substitui ambos por configurações locais.

**Linux / macOS:**

```bash
export DB_URL='postgresql+asyncpg://postgres:senha_local_dev@127.0.0.1:5432/fastapi1'
export JWT_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

**Windows — PowerShell:**

```powershell
$env:DB_URL = 'postgresql+asyncpg://postgres:senha_local_dev@127.0.0.1:5432/fastapi1'
$env:JWT_SECRET = (python -c "import secrets; print(secrets.token_urlsafe(32))")
```

| Variável | Uso |
| --- | --- |
| `DB_URL` | Conexão com o prefixo `postgresql+asyncpg://` |
| `JWT_SECRET` | Segredo para assinar e validar tokens |
| `API_V1_STR` | Prefixo das rotas; padrão `/api/v1` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token; padrão `10080` minutos, ou 7 dias |

As variáveis são lidas por `BaseSettings`. O código não configura carregamento automático de `.env`; criar o arquivo sozinho não substitui os comandos acima. Consulte o [funcionamento das configurações do Pydantic](https://docs.pydantic.dev/1.10/usage/settings/).

Mantenha o terminal aberto para as próximas etapas. Ao abrir outro terminal, defina as variáveis novamente. Trocar `JWT_SECRET` invalida tokens emitidos com a chave anterior.

### 5. Crie as tabelas — somente no banco de teste

> **Atenção: `criar_tabelas.py` apaga as tabelas dos modelos antes de recriá-las. Todos os usuários e artigos dessas tabelas serão perdidos.** Confira se `DB_URL` aponta para o banco local recém-criado. Não execute esse script em um banco com dados que deseja manter.

```bash
python criar_tabelas.py
```

O script cria as tabelas `usuarios` e `artigos`; ele não cria o banco PostgreSQL. Não é necessário executá-lo a cada inicialização da API.

### 6. Inicie a API

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

| Endereço | Conteúdo |
| --- | --- |
| http://127.0.0.1:8000/docs | Swagger UI: explore e envie requisições |
| http://127.0.0.1:8000/redoc | Documentação ReDoc |
| http://127.0.0.1:8000/openapi.json | Contrato OpenAPI |
| http://127.0.0.1:8000/api/v1/artigos/ | Lista pública de artigos; inicialmente `[]` |

A raiz `/` não possui rota e retorna **404**. Para encerrar, pressione `Ctrl+C`. O parâmetro `--reload` é destinado ao desenvolvimento.

## 🧪 Testando com Postman

### Importe e execute a coleção

1. Baixe [FastAPI1.postman_collection.json](./FastAPI1.postman_collection.json).
2. No Postman Desktop, clique em **Import** e selecione o arquivo.
3. Abra **FastAPI1 — Usuários e artigos** e confira em **Variables**: `base_url = http://127.0.0.1:8000/api/v1`.
4. Com a API ligada, execute a pasta **Fluxo completo local** pelo **Run**, com uma iteração e a ordem original.
5. Confira os resultados no Runner. Para requisições individuais, use **Send** e veja **Test Results**.

A coleção gera um e-mail exclusivo e salva `usuario_id`, `artigo_id` e `access_token` automaticamente. Não exige configuração de e-mail: esta API não envia confirmação de cadastro.

O fluxo cadastra um usuário, testa e-mail duplicado e login incorreto, autentica, verifica a rejeição de criação de artigo sem token, cria e atualiza um artigo, consulta o relacionamento com o autor e exclui os dados de teste. As consultas finais esperam **404** para confirmar a remoção.

> Execute em banco de desenvolvimento. O fluxo remove o usuário e o artigo que criou; se interrompido, esses registros podem permanecer. Não substitua os IDs automáticos por IDs de dados reais. Depois de uma execução completa, faça novo cadastro e login para testar manualmente, pois o usuário anterior foi excluído.

### Cadastro manual

**POST** `{{base_url}}/usuarios/signup`

Em **Body → raw → JSON**:

```json
{
  "nome": "Edu",
  "sobrenome": "Marques",
  "email": "edu@example.com",
  "senha": "SenhaLocal123!",
  "eh_admin": false
}
```

Esperado: **201 Created**, com os dados do usuário e seu `id`, sem a senha. Um e-mail já cadastrado retorna **406**.

### Login: use formulário, não JSON

**POST** `{{base_url}}/usuarios/login`

Em **Body → x-www-form-urlencoded**, preencha:

| Key | Value |
| --- | --- |
| `username` | `edu@example.com` |
| `password` | `SenhaLocal123!` |

O campo se chama `username`, mas recebe o **e-mail** cadastrado. O Postman configura `Content-Type: application/x-www-form-urlencoded` para esse corpo.

Resposta de sucesso, **200 OK**:

```json
{
  "access_token": "TOKEN_JWT",
  "token_type": "bearer"
}
```

Na coleção, o token é salvo pelo script da requisição de login. Se criar a requisição manualmente, copie o valor para a variável `access_token`.

### Crie um artigo autenticado

**POST** `{{base_url}}/artigos/`

Em **Authorization → Bearer Token**, informe `{{access_token}}`. Em **Body → raw → JSON**:

```json
{
  "titulo": "Primeiros passos com FastAPI",
  "descricao": "Um guia de estudo sobre APIs em Python.",
  "url_fonte": "https://example.com/fastapi"
}
```

Esperado: **201 Created**. O autor é definido pelo usuário do token; não é necessário enviar `usuario_id`. A URL precisa ser válida.

Para atualizar, envie **PUT** `{{base_url}}/artigos/{{artigo_id}}`, com o mesmo formato de corpo e autenticação. Os três campos continuam obrigatórios e o sucesso retorna **202 Accepted**. Para excluir, use **DELETE** nessa URL: o retorno é **204**, sem corpo.

A API não implementa logout ou revogação de JWT. Apagar o token no Postman não o revoga no servidor.

## 📍 Rotas da API

Prefixo padrão: `/api/v1`.

| Método | Rota | Operação | JWT obrigatório | Sucesso |
| --- | --- | --- | --- | --- |
| POST | `/usuarios/signup` | Cadastrar usuário | Não | 201 |
| POST | `/usuarios/login` | Autenticar por formulário | Não | 200 |
| GET | `/usuarios/logado` | Consultar identidade autenticada | Sim | 200 |
| GET | `/usuarios/` | Listar usuários | Não | 200 |
| GET | `/usuarios/{id}` | Consultar usuário e artigos | Não | 200 |
| PUT | `/usuarios/{id}` | Atualizar usuário | Não | 200 |
| DELETE | `/usuarios/{id}` | Excluir usuário e seus artigos | Não | 204 |
| GET | `/artigos/` | Listar artigos | Não | 200 |
| GET | `/artigos/{id}` | Consultar artigo | Não | 200 |
| POST | `/artigos/` | Criar artigo para o usuário autenticado | Sim | 201 |
| PUT | `/artigos/{id}` | Atualizar artigo | Sim | 202 |
| DELETE | `/artigos/{id}` | Excluir artigo do usuário autenticado | Sim | 204 |

Preserve a barra final nas rotas de listagem e criação de artigos para evitar redirecionamentos. As listagens retornam arrays e não implementam paginação nem filtros de busca.

## 📁 Organização do projeto

```text
fastapi1/
├── main.py                       # Aplicação FastAPI
├── criar_tabelas.py               # Apaga e recria as tabelas
├── requirements.txt              # Dependências fixadas
├── FastAPI1.postman_collection.json
├── api/v1/
│   ├── api.py                    # Agrupamento de rotas
│   └── endpoints/
│       ├── usuario.py            # Cadastro, login e usuários
│       └── artigo.py             # Operações de artigos
├── core/
│   ├── configs.py                # Configurações via BaseSettings
│   ├── database.py               # Engine e sessão assíncrona
│   ├── deps.py                   # Sessão e usuário autenticado
│   ├── auth.py                   # Autenticação e JWT
│   └── security.py               # Hash de senha
├── models/                       # Entidades SQLAlchemy
├── schemas/                      # Contratos Pydantic
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── runtime.txt
└── app.yaml
```

## 🐳 Sobre os arquivos Docker existentes

O caminho principal deste guia executa a API em um ambiente virtual. O comando Docker mostrado acima é uma alternativa apenas para o banco e **não usa o Compose do repositório**.

O Compose existente precisa de ajustes antes de ser usado como fluxo completo:

- A `DB_URL` do serviço `app` aponta para `localhost`; entre containers, o host do banco deve ser `postgresql`, nome do serviço.
- Os serviços de banco e pgAdmin dependem de um `.env` não fornecido. Eles precisam de variáveis como `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `PGADMIN_DEFAULT_EMAIL` e `PGADMIN_DEFAULT_PASSWORD`.
- O serviço `app` precisa receber uma `JWT_SECRET` própria e ter `bcrypt` instalado na imagem.
- O Dockerfile usa a base antiga `python:3.10.12-slim-buster`; sua construção deve ser revisada antes de depender dela.
- Os volumes usam caminhos absolutos em `/var/cache`, que podem exigir permissões específicas. `depends_on` sozinho não verifica se o banco já aceita conexões.

Os arquivos `Procfile`, `runtime.txt` e `app.yaml` são configurações de implantação existentes, mas este guia não valida deploy em provedores externos.

## 🛠️ Solução de problemas

| Problema | O que verificar |
| --- | --- |
| Falha ao instalar `asyncpg`, `greenlet` ou outras dependências antigas | Use Python 3.10 e recrie o ambiente virtual. |
| `MissingBackendError` ao cadastrar ou autenticar | Instale `bcrypt==3.2.2` no mesmo ambiente da API. |
| Conexão recusada no PostgreSQL | Confirme se o banco está ativo, a porta e as credenciais da `DB_URL`. |
| A aplicação tenta acessar o banco remoto | Exporte `DB_URL` antes de iniciar o processo; um `.env` sozinho não é carregado. |
| `relation ... does not exist` | As tabelas ainda não foram criadas; leia o aviso de perda de dados antes de usar `criar_tabelas.py`. |
| 422 no login | Use `x-www-form-urlencoded`, com `username` e `password`. |
| 422 ao criar ou atualizar artigo | Envie `titulo`, `descricao` e uma `url_fonte` válida em JSON. |
| 400 no login | E-mail ou senha incorretos. |
| 401 em rota protegida | Confira o Bearer Token, sua validade e a chave JWT usada pela API. |
| 406 no cadastro | O e-mail já existe; use outro endereço. |
| 404 ao excluir artigo | O artigo não existe ou não pertence ao usuário autenticado. |
| 404 na raiz | Abra `/docs` ou `/api/v1/artigos/`. |

## 🚧 Limitações e cuidados

Estes pontos descrevem o código atual; a documentação não altera as regras da aplicação:

- **Segredos publicados:** `core/configs.py` contém credenciais de banco e uma chave JWT. Rotacione esses segredos caso ainda estejam ativos. Usar variáveis locais não remove o conteúdo já publicado no histórico.
- **Permissões de usuários:** consulta, atualização e exclusão de usuários são públicas. O cadastro aceita `eh_admin` do cliente, e esse campo não implementa controle de acesso nas rotas.
- **Autoria dos artigos:** o PUT exige login, mas não restringe a edição ao autor. Ao editar um artigo de outro usuário, o código transfere a autoria para quem fez a requisição. O DELETE, por sua vez, filtra pelo autor autenticado.
- **Atualização de usuários:** o código aplica apenas valores considerados verdadeiros; por exemplo, enviar `eh_admin=false` não remove esse atributo de quem já o possui.
- **Banco:** não há migrações versionadas, e o script fornecido recria as tabelas de forma destrutiva. A exclusão de usuário também exclui seus artigos por cascade.
- **Manutenção:** as dependências são antigas e precisam de revisão antes de uma exposição pública. O modo de desenvolvimento e os arquivos de deploy não representam uma configuração pronta para produção.

## ✅ Validação deste guia

A coleção foi executada com **Newman**, usando **Python 3.10.21**, **PostgreSQL 15.12**, as versões do `requirements.txt` e `bcrypt==3.2.2`: **16 requisições e 25 verificações aprovadas**.

A validação usou um banco local descartável, sem acessar a URL remota do código. A interface gráfica do Postman, os comandos de Windows/macOS, o fluxo Docker e o deploy externo não foram executados. Os testes cobrem o fluxo funcional descrito, não uma auditoria completa de segurança.

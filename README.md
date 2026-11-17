# Trabalho-de-Conclus-o-de-Curso

Projeto Integrador (Bolsa Futuro Digital) · Desafio Técnico 1 · **ETL, limpeza e enriquecimento de dados** da base de clientes da *Distribuidora Vetor* (empresa fictícia).

O projeto recebe um CSV de clientes com dados sujos (bairros escritos de vários jeitos, CNPJ, telefone e data em formatos diferentes, CEPs ausentes ou inválidos), limpa os dados, enriquece o bairro pela consulta de CEP (ViaCEP, com cache local), guarda **os dados brutos, os tratados e o registro de cada alteração** no PostgreSQL e mostra tudo em páginas web feitas em Django.

> Documentação completa: [Documentação técnica](DOCUMENTACAO_TECNICA.md) · [Regras de negócio](REGRAS_DE_NEGOCIO.md) · [Resumos por card](RESUMOS_DOS_CARDS.md) · [Estrutura dos documentos](ESTRUTURA_DOCUMENTOS.md)

*Última atualização: 17/11/2026 (Sprint 4).*

---

## 1. Status do projeto

| Funcionalidade | Situação |
|---|---|
| Diagnóstico dos dados (CNPJ, telefone, data, bairros) | Pronto |
| Funções de limpeza (CNPJ, telefone, data, bairro, CEP) | Pronto |
| Testes unitários da limpeza e da regra de prioridade | Pronto |
| Conexão Python ↔ PostgreSQL (SQLAlchemy + `.env`) | Pronto |
| Serviço de consulta de CEP com cache local | Pronto |
| Modelos Django: dados brutos, dados tratados e auditoria | Pronto |
| Páginas web: dados brutos, dados tratados e auditoria | Pronto |
| Regra de prioridade: bairro digitado × bairro da API | Implementada (ainda não ligada ao fluxo de carga) |
| Auditoria das alterações | Parcial (a carga audita só o campo bairro) |
| Carga no PostgreSQL (`loader.py`) | Parcial (funciona pelo script; veja a seção 5.2) |
| Testes com respostas simuladas (mocks) | Parcial (enriquecimento coberto; consulta HTTP do `cep_servico` ainda não) |
| Pipeline unificado (`main.py`) | Em desenvolvimento |
| Botão de upload, pesquisa, refresh e página de JSON | Em desenvolvimento |
| Enriquecimento do banco (consultar o banco antes do ViaCEP) | Em desenvolvimento |
| Diagrama do projeto | Em desenvolvimento |
| Teste de escalabilidade (5.000 a 50.000 clientes) | Planejado |

Este README descreve o que **existe hoje**. Os itens "em desenvolvimento" serão atualizados quando forem concluídos.

---

## 2. Requisitos

- **Python 3.12 ou superior** (exigência do Django 6.x; confira com `python --version`)
- **PostgreSQL** instalado localmente, na porta padrão `5432`
- **Git**
- Internet (somente para consultar CEPs novos no ViaCEP; CEPs já guardados no cache não precisam de internet)

As bibliotecas estão no `requirements.txt` **da raiz do projeto** (Django, SQLAlchemy, psycopg2, pandas, python-dotenv, requests, pytest e pytest-django, entre outras).

> Se existir outro `requirements.txt` dentro da pasta `web/` com apenas 5 bibliotecas (Django, asgiref, pillow, sqlparse, tzdata), **ele não serve para rodar o ETL**. Instale sempre o da raiz.

---

## 3. Instalação

### 3.1 Baixar o projeto

```bash
git clone https://github.com/fernandosilvaruy-ops/Projeto-Integrador-Primora.git
cd Projeto-Integrador-Primora
```

### 3.2 Criar e ativar o ambiente virtual

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\activate
```

Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.3 Instalar as bibliotecas

```bash
pip install -r requirements.txt
```

### 3.4 Configurar as variáveis de ambiente (`.env`)

As senhas **não** ficam no código. Cada pessoa cria o seu próprio `.env` na **raiz do projeto**, a partir do modelo:

```bash
copy .env.example .env        # Windows
cp .env.example .env          # Linux ou macOS
```

| Variável | O que é | Exemplo |
|---|---|---|
| `DB_NAME` | Nome do banco | `distribuidora_vetor` |
| `DB_USER` | Usuário do PostgreSQL | `postgres` |
| `DB_PASSWORD` | Senha do PostgreSQL (definida na instalação) | *(a sua)* |
| `DB_HOST` | Endereço do banco | `localhost` |
| `DB_PORT` | Porta | `5432` |
| `DJANGO_SECRET_KEY` | Chave secreta do Django | *(gere uma, veja abaixo)* |

Para gerar a `DJANGO_SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> O `.env` está no `.gitignore`: **nunca** suba esse arquivo para o GitHub.

---

## 4. Banco de dados

### 4.1 Criar o banco

No PostgreSQL (pgAdmin ou `psql`), crie o banco com o mesmo nome de `DB_NAME`:

```sql
CREATE DATABASE distribuidora_vetor;
```

### 4.2 Criar as tabelas do Django

```bash
cd web
python manage.py migrate
```

Isso cria três tabelas do projeto, além das internas do Django:

| Tabela | Guarda |
|---|---|
| `cliente_clientebruto` | Os clientes **como chegaram** no CSV original |
| `cliente_clientetratado` | Os clientes **depois da limpeza** |
| `cliente_auditoriaalteracao` | O registro de **cada alteração**: campo, valor original, valor tratado e critério |

### 4.3 Testar a conexão (SQLAlchemy)

Na raiz do projeto:

```bash
python src/database/connection.py
```

O script mostra a versão do PostgreSQL e faz um teste de escrita e leitura numa tabela temporária.

> **Atenção:** o passo que conta clientes ainda consulta a tabela antiga `cliente_cliente`, que não existe mais. Esse passo mostra uma mensagem de erro, **mas a conexão em si está funcionando** se a versão do PostgreSQL aparecer.

### 4.4 O `init.sql` e o `importar_clientes`

- O arquivo `init.sql` define as tabelas `clientes_tratados` e `auditoria_etl`, que **não são usadas** pelo Django atual. Ele também usa `##` como comentário, e o PostgreSQL provavelmente rejeita isso. Não é necessário para rodar o projeto.
- O comando `python manage.py importar_clientes` é **legado**: depende do modelo `Cliente`, que foi substituído pelos modelos novos. Use o fluxo da seção 5.

---

## 5. Executar o fluxo de dados

### 5.1 Gerar o CSV tratado

Na **raiz do projeto** (onde está `clientes_distribuidora_vetor.csv`):

```bash
python src1/etl/padronizar_Clientes.py
```

> Confirme o caminho do script com `git ls-files`. Ele precisa ser executado da raiz, porque lê o CSV e grava o resultado na pasta atual.

O que ele faz:

- limpa o CNPJ (fica só com os 14 números), o telefone, a data de cadastro e o CEP, e padroniza o bairro;
- se o bairro vier **vazio**, tenta descobrir o bairro pelo CEP, consultando o ViaCEP (com cache);
- grava `clientes_tratados.csv` e imprime um resumo (CNPJs válidos, telefones e datas não reconhecidos, CEPs ausentes e a contagem de bairros).

### 5.2 Carregar no banco, com auditoria

Também na raiz do projeto, com o `.env` preenchido e as migrations aplicadas:

```bash
python src/database/loader.py
```

O que ele faz, nesta ordem:

1. procura os CSVs na raiz (o bruto e o tratado);
2. **apaga** os registros antigos das três tabelas;
3. carrega os clientes brutos em `cliente_clientebruto`;
4. carrega os clientes tratados em `cliente_clientetratado`;
5. compara o bairro original com o tratado e grava uma linha em `cliente_auditoriaalteracao` para cada diferença.

> **Atenção 1:** o comando `python manage.py rodar_etl` **ainda não carrega nada**. Ele chama uma função que só imprime "ETL rodando..." e depois mostra "sucesso". Use o script acima.
>
> **Atenção 2:** o `loader.py` escolhe os arquivos pelo **início do nome**. Se na raiz existirem `clientes_padronizado.csv` (versão antiga) e `clientes_tratados.csv` (versão atual), ele pode carregar o antigo. Mantenha só o arquivo atual na raiz.

### 5.3 Ver os resultados no navegador

```bash
cd web
python manage.py runserver
```

Abra `http://127.0.0.1:8000/` (a raiz redireciona para `/clientes/`).

| Endereço | O que mostra |
|---|---|
| `/clientes/` | **Dados brutos**: os registros originais, antes de qualquer tratamento |
| `/clientes/tratados/` | **Dados tratados**: os registros depois da limpeza e do enriquecimento |
| `/clientes/auditoria/` | **Auditoria**: cada alteração (cliente, campo, valor original, valor tratado, critério e data) |

Cada página tem um contador de registros e botões para navegar entre as três telas.

### 5.4 Scripts de diagnóstico

```bash
python analise_clientes.py        # conta os formatos de CNPJ, telefone e data
python mapeamento_Bairros.py      # lista as grafias de bairro e gera mapeamento_bairros.csv
```

### 5.5 Consulta de CEP e cache

O módulo `cep_servico.py` consulta o ViaCEP e guarda cada resposta em `cache_cep.json`. Na segunda consulta ao mesmo CEP, a resposta vem do cache, sem internet. Para ver funcionando, na raiz:

```bash
python teste_cep.py
```

### 5.6 Regra de prioridade do bairro

O arquivo `regra_prioridade.py` decide qual bairro prevalece entre o digitado e o da API e **devolve também o motivo**, para a auditoria:

| Situação | Bairro que fica | Motivo registrado |
|---|---|---|
| A consulta ao CEP falhou | O original | `FALHA_CONSULTA` |
| A API não informou bairro | O original | `MANTIDO_ORIGINAL` |
| O bairro original estava vazio | O da API | `PREENCHIDO_API` |
| Os dois são iguais (sem diferenciar maiúsculas) | O original | `SEM_ALTERACAO` |
| Os dois são diferentes | **O da API** | `PRIORIDADE_API` |

> Essa regra está implementada e testada, mas **ainda não está ligada ao fluxo de carga**. Veja o impacto dela na [documentação técnica](DOCUMENTACAO_TECNICA.md#85-regra-de-prioridade-do-bairro).

### 5.7 Pipeline completo

> **Em desenvolvimento.** O objetivo é rodar todas as etapas com um único comando (`python main.py`). Esta seção será atualizada quando o `main.py` estiver pronto.

---

## 6. Testes

Os testes ficam na pasta `tests/`. Com o ambiente virtual ativo, na raiz do projeto, rode:

```bash
python -m pytest -v
```

> Use `python -m pytest`, e não só `pytest`: assim a raiz do projeto entra no caminho do Python e o import de `src1` funciona.

O `pytest.ini` já configura o Django (`DJANGO_SETTINGS_MODULE = core.settings`) e as pastas `web` e `src`.

| Teste | O que cobre | Precisa de banco? |
|---|---|---|
| Testes de limpeza (CNPJ, telefone, data, bairro, nulos) | As funções de `padronizar_Clientes.py` | Não |
| `test_regra_prioridade.py` | As 5 situações da regra de prioridade | Não |
| `test_enrich.py` | O enriquecimento, com a **resposta do ViaCEP simulada** (sem internet) | Não |
| `test_auditoria.py` | Criação de registros brutos, tratados e de auditoria | **Sim**: PostgreSQL ligado e usuário com permissão para criar o banco de testes |
| `test_smoke.py` | Verifica que o pytest roda | Não |

> **Atenção:** os testes de limpeza foram escritos para a versão anterior da função de bairro (que recebia um texto). A versão atual recebe a **linha inteira do cliente**, e a validação de CNPJ também mudou. Se esses testes forem executados, parte deles falha até serem atualizados. Detalhes na [documentação técnica](DOCUMENTACAO_TECNICA.md#12-limites-conhecidos-e-pontos-de-atencao).

---

## 7. Estrutura do projeto

```
Projeto-Integrador-Primora/
├── .env.example                      modelo das variáveis de ambiente
├── .gitignore
├── pytest.ini                        configuração do pytest e do Django
├── requirements.txt                  bibliotecas do projeto
├── init.sql                          tabelas SQL antigas (não usadas pelo Django)
├── clientes_distribuidora_vetor.csv  base original (47 clientes fictícios)
├── clientes_tratados.csv             resultado da limpeza
├── web/                              projeto Django
│   ├── manage.py
│   ├── core/                         settings, urls, wsgi, asgi
│   └── cliente/                      app de clientes
│       ├── models.py                 ClienteBruto, ClienteTratado, AuditoriaAlteracao
│       ├── views.py                  as três páginas
│       ├── urls.py                   endereços do app
│       ├── migrations/               histórico das mudanças no banco
│       ├── templates/cliente/        lista.html, clientes_tratados.html, auditoria.html
│       └── management/commands/      importar_clientes.py (legado) e rodar_etl.py
├── src/database/
│   ├── connection.py                 conexão SQLAlchemy
│   └── loader.py                     carga no PostgreSQL e auditoria
├── src1/
│   ├── etl/                          padronizar_Clientes.py, regra_prioridade.py, enrich.py
│   └── servico/                      cep_servico.py, cache_cep.json, auditoria_servico.py
└── tests/                            testes automatizados (pytest)
```

> A estrutura foi montada a partir dos caminhos usados no código. Confira com `git ls-files` e ajuste se alguma pasta estiver em outro lugar.

---

## 8. Documentação do projeto

| Documento | Conteúdo |
|---|---|
| [`DOCUMENTACAO_TECNICA.md`](DOCUMENTACAO_TECNICA.md) | Arquitetura, modelo de dados, fluxo do ETL, interface web, testes, limites e pendências |
| [`REGRAS_DE_NEGOCIO.md`](REGRAS_DE_NEGOCIO.md) | Todas as regras numeradas (RN-xx) e o histórico de mudanças |
| [`RESUMOS_DOS_CARDS.md`](RESUMOS_DOS_CARDS.md) | O que cada card entregou, onde está no código e como usar |
| [`ESTRUTURA_DOCUMENTOS.md`](ESTRUTURA_DOCUMENTOS.md) | Índice dos documentos da entrega e lista de conferência |

---

## 9. Licença

Veja o arquivo [`LICENSE`](LICENSE).

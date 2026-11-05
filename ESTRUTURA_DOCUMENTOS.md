# Estrutura dos documentos entregues

Este arquivo organiza **o que o grupo vai entregar**, onde cada documento fica, para quem ele é escrito e em que ponto está. Serve como índice e como lista de conferência antes da entrega final.

Base: entregáveis do Desafio Técnico 1 (ETL, Limpeza e Enriquecimento de Dados) e critérios de avaliação (cobertura do tratamento, qualidade da decisão, documentação e rastreabilidade, testes e comunicação).

---

## 1. Visão geral dos documentos

| # | Documento | Arquivo | Para quem | Responde à pergunta | Situação |
|---|---|---|---|---|---|
| 1 | README | `README.md` | Qualquer pessoa que abrir o repositório | "Como instalo e rodo isto?" | Rascunho pronto |
| 2 | Documentação técnica | `docs/DOCUMENTACAO_TECNICA.md` | Avaliadores e desenvolvedores | "Como a solução funciona e quais são seus limites?" | Rascunho pronto |
| 3 | Regras de negócio | `docs/REGRAS_DE_NEGOCIO.md` | Avaliadores, grupo, usuários do dado | "Quais decisões foram tomadas e por quê?" | Rascunho pronto |
| 4 | Estrutura dos documentos | `docs/ESTRUTURA_DOCUMENTOS.md` | O grupo | "O que falta entregar?" | Este arquivo |
| 5 | Relatório de trade-offs (1 a 2 páginas) | `docs/RELATORIO_TRADE_OFFS.md` | Público **não técnico** | "O que foi automatizado, o que ficou manual e por quê?" | A fazer |
| 6 | Log ou tabela de auditoria | tabela no PostgreSQL | Avaliadores | "Por que este registro ficou assim?" | Em desenvolvimento (outro card) |

Os documentos 1 a 4 formam o conjunto do card "rascunho da Documentação Técnica e README". O documento 5 e o log de auditoria são entregáveis do desafio que dependem do restante do grupo.

---

## 2. Onde cada coisa fica no repositório

```
Projeto-Integrador-Primora/
├── README.md                          porta de entrada (instalar e rodar)
├── docs/
│   ├── ESTRUTURA_DOCUMENTOS.md        este índice
│   ├── DOCUMENTACAO_TECNICA.md        como funciona + limites
│   ├── REGRAS_DE_NEGOCIO.md           regras numeradas (RN-xx)
│   └── RELATORIO_TRADE_OFFS.md        relatório curto (a fazer)
├── tests/                             testes automatizados
└── ...                                código do projeto
```

---

## 3. Ordem de leitura recomendada

1. **README**: instalar e rodar.
2. **Documentação técnica**: entender a solução.
3. **Regras de negócio**: ver o detalhe de cada decisão.
4. **Relatório de trade-offs**: ver a visão de alto nível, sem termos técnicos.

---

## 4. O que cada documento contém

### 4.1 README
Resumo do projeto · situação das etapas · requisitos · instalação · `.env` · banco de dados · como executar · testes · estrutura de pastas · licença.

### 4.2 Documentação técnica
Visão geral · entregáveis × situação · arquitetura do ETL · dados de entrada · resumo das regras · modelo de dados · serviço de CEP e cache · testes · configuração e segurança · **limites conhecidos** · decisões pendentes.

### 4.3 Regras de negócio
Princípios gerais · CNPJ · telefone · data · CEP · bairro · consulta de CEP e cache · validação de endereço · importação para o Django · regras pendentes. Cada regra tem um código (RN-xx) e indica a função do código onde está implementada.

### 4.4 Relatório de trade-offs (roteiro sugerido)
Escrito para quem **não é de tecnologia**. Em 1 a 2 páginas:

1. **O problema**, em duas frases e com um exemplo (o mesmo bairro aparecendo de cinco formas).
2. **O que o grupo decidiu automatizar** (limpeza de formato, dicionário de bairros, consulta de CEP) e **por quê**.
3. **O que decidiu tratar manualmente ou deixar sinalizado** (CNPJ com dígito errado, subdivisões como Sul e Norte, CEPs ausentes) e **por quê**.
4. **Como o grupo resolve conflitos** entre o bairro digitado e o da API (a regra de prioridade, quando estiver definida).
5. **O que se perde em cada escolha** (os trade-offs): por exemplo, padronizar o bairro facilita relatórios, mas apaga o "Sul" e o "Norte".
6. **Como confiar no resultado**: o log de auditoria permite explicar qualquer registro.
7. **Próximos passos** se o projeto continuasse.

---

## 5. Relação com os critérios de avaliação

| Critério do desafio | Documento que ajuda a comprovar |
|---|---|
| Cobertura do tratamento | Documentação técnica (seção 4, indicadores da amostra) |
| Qualidade da decisão | Regras de negócio e relatório de trade-offs |
| Documentação e rastreabilidade | Regras de negócio (códigos RN) e log de auditoria |
| Testes | Documentação técnica (seção 8) e README (seção 6) |
| Comunicação | Relatório de trade-offs |

---

## 6. Situação dos cards relacionados (Trello, 05/11/2026)

| Card | Situação |
|---|---|
| Função Python: limpeza de CNPJ, telefones e datas | Concluído |
| Função Python: normalização de texto de bairros | Concluído |
| Testes unitários dos módulos de limpeza | Concluído |
| Conexão Python com PostgreSQL | Concluído |
| Módulo de API com cache local de CEP | Concluído |
| Lógica de decisão: divergência entre bairro digitado e API | Planejado (Sprint 3) |
| Execução da carga final no PostgreSQL | Planejado (Sprint 3) |
| Testes automatizados da API com mocks | Planejado (Sprint 3) |
| Módulo de gravação na tabela de auditoria | Em andamento |
| Unificação do pipeline no `main.py` | Em andamento |
| Rascunho da documentação técnica e README | Em andamento |

---

## 7. Regras de manutenção

- Cada pessoa atualiza a seção do **seu** card quando ele for concluído, e troca "pendente" por "pronto" nas tabelas de situação.
- Mudou uma regra no código? Atualize o código `RN-xx` correspondente em `REGRAS_DE_NEGOCIO.md` e, se for o caso, o teste que a registra.
- Nenhum documento deve conter senhas, chaves ou dados reais.
- Antes da entrega final, percorrer este arquivo e conferir se todos os itens da seção 1 estão como "pronto".

---

## 8. Lista de conferência antes da entrega

- [ ] README testado em uma máquina limpa (alguém que não participou consegue instalar e rodar)
- [ ] Documentação técnica sem itens "pendente"
- [ ] Regras de negócio refletem o código final, incluindo RN-90 a RN-93
- [ ] Relatório de trade-offs escrito, com 1 a 2 páginas e linguagem simples
- [ ] Log de auditoria gerado e conferido
- [ ] Testes passando (`python -m pytest -v`)
- [ ] Nenhum arquivo `.env` ou senha no repositório

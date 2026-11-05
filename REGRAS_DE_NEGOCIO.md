# Regras de negócio

Este documento lista as regras que o projeto adota para limpar e validar a base de clientes da Distribuidora Vetor. O enunciado do desafio pede que as regras de negócio sejam **assumidas e documentadas pela própria equipe**, e é isso que este arquivo faz.

Cada regra tem um código (RN-01, RN-02...) para ser citada em outros documentos, no log de auditoria e nos testes. A coluna **Onde está no código** diz em qual função a regra foi implementada.

**Situação das regras:** *Implementada* (já existe no código) · *Pendente* (decisão ainda em desenvolvimento por outro card).

---

## 1. Princípios gerais

| Código | Regra | Situação |
|---|---|---|
| RN-01 | **Nenhum registro é descartado por ter dado sujo.** Quando um campo não pode ser corrigido, ele fica vazio (`None`) e o restante do cliente é mantido. | Implementada |
| RN-02 | **Limpar não é validar.** As funções `padronizar_*` só arrumam o formato. A conferência de validade (por exemplo, dígitos do CNPJ) é feita por funções separadas. | Implementada |
| RN-03 | **Valor nulo, vazio ou só com espaços** nunca causa erro. Cada função devolve `None`, com uma exceção: o bairro vazio vira o texto `Não informado`, para o relatório não ter linha em branco. | Implementada |
| RN-04 | O dado original **nunca é apagado**: o resultado do tratamento vai para colunas novas (`*_padronizado`) ou para a base final, e o valor original continua disponível para auditoria. | Implementada |

---

## 2. CNPJ

| Código | Regra | Onde está no código |
|---|---|---|
| RN-10 | Ponto, hífen, barra e espaço são removidos, e as letras viram maiúsculas. | `limpar_cnpj` |
| RN-11 | Um CNPJ tem **14 caracteres**: os 12 primeiros podem ser números ou letras (formato alfanumérico novo) e os 2 últimos, os dígitos verificadores, devem ser números. Fora desse formato, o resultado é `None`. | `limpar_cnpj` |
| RN-12 | O CNPJ limpo recebe a máscara `XX.XXX.XXX/XXXX-XX`. | `padronizar_cnpj` |
| RN-13 | **Validade:** os dois dígitos verificadores são conferidos pelo cálculo módulo 11 com os pesos oficiais. Cada letra vale seu código ASCII menos 48 (A = 17, B = 18...). CNPJs com todos os caracteres iguais são inválidos. | `cnpj_valido` |
| RN-14 | **CNPJ com dígito errado não é removido nem corrigido**: a coluna `cnpj_valido` recebe `False` e o registro segue. Os CNPJs da base são fictícios; na amostra de 47 clientes, **nenhum** passa na conferência dos dígitos (0 de 47). | `cnpj_valido` + `padronizar_cnpj` |

---

## 3. Telefone

| Código | Regra | Onde está no código |
|---|---|---|
| RN-20 | Só os dígitos são considerados. Parênteses, hífens, espaços e `+` são ignorados. | `padronizar_telefone` |
| RN-21 | Se sobrarem **12 ou 13 dígitos** começando com `55`, o `55` (código do país) é removido. | `padronizar_telefone` |
| RN-22 | **11 dígitos** = celular: `(DD) 9XXXX-XXXX`. **10 dígitos** = fixo: `(DD) XXXX-XXXX`. | `padronizar_telefone` |
| RN-23 | Qualquer outra quantidade de dígitos resulta em `None`. A função **não confere se o DDD existe**, só a quantidade de dígitos. | `padronizar_telefone` |

---

## 4. Data de cadastro

| Código | Regra | Onde está no código |
|---|---|---|
| RN-30 | Formatos aceitos: `AAAA-MM-DD`, `DD/MM/AAAA`, `DD-MM-AAAA` e `Mmm DD, AAAA` (mês em inglês com 3 letras, em maiúscula ou minúscula). | `padronizar_data` |
| RN-31 | O resultado é sempre `AAAA-MM-DD`. | `padronizar_data` |
| RN-32 | **Datas com barra ou hífen são lidas como DIA primeiro.** `08-01-2022` é 8 de janeiro, e não 1º de agosto. Essa é uma decisão assumida: a base não tem como indicar a intenção de quem digitou. | `padronizar_data` |
| RN-33 | Data que não existe (como 31/02) ou em formato desconhecido resulta em `None`. | `padronizar_data` |

---

## 5. CEP

| Código | Regra | Onde está no código |
|---|---|---|
| RN-40 | O CEP deve ter **8 dígitos** depois de remover tudo que não é número. Resultado no formato `XXXXX-XXX`. | `padronizar_cep` |
| RN-41 | O CEP `00000-000` é tratado como ausente (`None`). Na amostra, 16 dos 47 CEPs são ausentes (13 vazios e 3 zerados). | `padronizar_cep` |

---

## 6. Bairro

| Código | Regra | Onde está no código |
|---|---|---|
| RN-50 | O texto é comparado em versão neutra: **sem acento e em minúsculas**. | `_sem_acento` |
| RN-51 | Um **dicionário de trechos** define o nome oficial: `aguas claras` → *Águas Claras*, `taguatinga` → *Taguatinga*, `vicente pires`, `v. pires` e `vte pires` → *Vicente Pires*, `guara` → *Guará*. O bairro é encontrado se o trecho aparecer **em qualquer lugar** do texto. | `REGRAS_BAIRRO` |
| RN-52 | Vale a **primeira regra** da lista que combinar. A ordem do dicionário importa. | `padronizar_bairro` |
| RN-53 | Sufixos e ruídos (`- DF`, `/DF`, espaços sobrando, maiúsculas, parênteses) não impedem o reconhecimento. | `padronizar_bairro` |
| RN-54 | **Subdivisões (Sul, Norte, I, II) são descartadas** no bairro padronizado: `Sul (Águas Claras)` e `Norte (Águas Claras)` viram o mesmo *Águas Claras*. O detalhe perdido fica registrado na coluna `complemento` do `mapeamento_bairros.csv`. | `padronizar_bairro` e `mapeamento_Bairros.py` |
| RN-55 | Bairro que **não está no dicionário** só é arrumado: sem espaços nas pontas e com a primeira letra de cada palavra maiúscula (`asa norte` → *Asa Norte*). | `padronizar_bairro` |
| RN-56 | Bairro vazio resulta em `Não informado`. | `padronizar_bairro` |

---

## 7. Consulta de CEP (ViaCEP) e cache

| Código | Regra | Onde está no código |
|---|---|---|
| RN-60 | O CEP consultado só mantém os dígitos e precisa ter 8. Senão, devolve `{"erro": "CEP deve ter 8 dígitos"}` sem chamar a internet. | `buscar_cep` |
| RN-61 | **O cache local é consultado primeiro** (`cache_cep.json`). Se o CEP já estiver lá, não há chamada à internet. | `buscar_cep` |
| RN-62 | Sem cache, a consulta ao ViaCEP tem **limite de 5 segundos**. Falha de rede ou de HTTP devolve um dicionário com a chave `erro`, sem derrubar o programa. | `buscar_cep` |
| RN-63 | Se o ViaCEP responder que o CEP não existe, o resultado é `{"erro": "CEP não encontrado"}`. | `buscar_cep` |
| RN-64 | **Só respostas de sucesso são guardadas no cache.** Erros nunca são gravados. | `buscar_cep` |

---

## 8. Validação do endereço do cliente

A função `validar_endereco` compara o cadastro do cliente com a resposta do ViaCEP e **não altera nenhum dado do cliente**.

| Código | Regra |
|---|---|
| RN-70 | São comparados três campos: `bairro`, `cidade` (com `localidade` da API) e `uf`. |
| RN-71 | A comparação ignora **maiúsculas, acentos e espaços nas pontas**. |
| RN-72 | Campo vazio, do cliente ou da API, **não conta como igual**: vai para a lista `campos_nao_verificados`. |
| RN-73 | **Resultado geral:** `ERRO` (a consulta falhou), `DIVERGENTE` (algum campo comparado é diferente), `INCOMPLETO` (nenhuma divergência, mas faltou comparar algum campo) ou `VALIDADO` (os três campos conferem). |
| RN-74 | A comparação do bairro usa o texto **como foi cadastrado**, sem passar por `padronizar_bairro`. Por isso `Sul (Águas Claras)` é `DIVERGENTE` de `Águas Claras` (verificado em simulação). Se o grupo preferir comparar o bairro já padronizado, a regra muda. |

---

## 9. Importação para o Django

O comando `python manage.py importar_clientes` carrega o CSV na tabela `cliente_cliente`.

| Código | Regra |
|---|---|
| RN-80 | O arquivo é lido com separador `;` e codificação `utf-8-sig`. |
| RN-81 | Linhas **sem CNPJ e sem e-mail** são ignoradas. |
| RN-82 | O cliente é identificado pelo **CNPJ**: se já existir, é atualizado; se não, é criado. Rodar o comando duas vezes não duplica clientes. |
| RN-83 | Campos opcionais vazios são gravados como nulos. |
| RN-84 | Datas são testadas nesta ordem: `AAAA-MM-DD`, `DD/MM/AAAA`, `DD-MM-AAAA`, `Mmm DD, AAAA` e `MM-DD-AAAA`. Data que não bate com nenhum formato vira nula. |
| RN-85 | **Os dados são gravados como vieram, sem passar pelas funções de limpeza.** A base tratada é uma etapa separada. |

> **Diferença entre as regras de data (RN-30 e RN-84):** o importador aceita um formato a mais, `MM-DD-AAAA`. Na prática ele só é usado quando o "dia" é maior que 12 (por exemplo `08-13-2022`, lido como 13 de agosto), enquanto `padronizar_data` devolveria `None` para esse valor. O grupo deve decidir se mantém as duas regras ou unifica.

---

## 10. Regras pendentes

Estas regras dependem de cards ainda em desenvolvimento. Os critérios abaixo vêm dos próprios cards, e a decisão final será registrada aqui quando existir.

| Código | Assunto | O que o card pede |
|---|---|---|
| RN-90 | **Divergência entre bairro digitado e bairro da API** | Definir uma regra de prioridade (por exemplo, "quando a API discordar do bairro digitado, prevalece o dado X"), aplicá-la no código unificado e **registrar o motivo da escolha** para o log de auditoria. |
| RN-91 | **Auditoria** | Gravar, linha a linha, `id_cliente`, `campo_alterado`, `valor_original`, `valor_tratado` e `criterio`, comparando o dado original com o tratado. |
| RN-92 | **Carga final** | Salvar os dados totalmente tratados na tabela `clientes_tratados` e validar que a **quantidade de registros originais é igual à de salvos**. |
| RN-93 | **Pipeline único** | Executar extração, transformação e carga em ordem, com um único comando. |

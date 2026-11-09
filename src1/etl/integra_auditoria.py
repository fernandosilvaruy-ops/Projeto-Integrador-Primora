def enriquecer_cliente(cliente):

    print("TESTE: entrei no enriquecimento")

    cep = cliente["cep_padronizado"]
    bairro = cliente["bairro_padronizado"]

    dados_api = buscar_cep(cep)

    print("Resposta do ViaCEP:", dados_api)
import pandas as pd
from pathlib import Path
from src1.etl.enrich import enriquecer_cliente
# Localiza a raiz do projeto
RAIZ = Path(__file__).resolve().parents[2]

# Arquivo gerado pela etapa de padronização
CAMINHO = RAIZ / "clientes_padronizado.csv"

# Preserva os valores como txt
df = pd.read_csv(
    CAMINHO,
    sep=";",
    dtype=str , keep_default_na=False
)

# Mapeamento colunas originais e tratadas
CAMPOS = {
    "cnpj": ("cnpj", "cnpj_padronizado"),
    "telefone": ("telefone", "telefone_padronizado"),
    "data_cadastro": ("data_cadastro", "data_cadastro_padronizada"),
    "bairro": ("bairro_informado", "bairro_padronizado"),
    "cep": ("cep", "cep_padronizado")
}

print("Colunas disponíveis:")
print(df.columns.tolist())

from src1.servico.auditoria_servico import compararDados


todas_alteracoes = []

#A função iterrows() percorre os clientes do CSV, um por vez
for _, cliente in df.iterrows():
    original = {}
    tratado = {}

    # Monta os dicionários com os valores de cada cliente
    for campo, (col_original, col_tratada) in CAMPOS.items():
        original[campo] = cliente[col_original]
        tratado[campo] = cliente[col_tratada]
    # Executa o enriquecimento
    resultado = enriquecer_cliente(cliente)

# Atualiza o bairro tratado
    tratado["bairro"] = resultado["bairro_final"]

# Cria o dicionário de critérios
    criterios = {}

# Se a API alterou o bairro, registra o motivo
    if resultado["bairro_final"] != cliente["bairro_padronizado"]:
        criterios["bairro"] = resultado["criterio"]

    # Compara valoresoriginais e tratados
    alteracoes = compararDados(
        id_cliente=cliente["id_cliente"],        
        original=original,
        tratado=tratado,
        criterios_personalizados=criterios
    )

    todas_alteracoes.extend(alteracoes)

print("Total de alterações identificadas:", len(todas_alteracoes))

# Mostra apenas as três primeiras alterações
for alteracao in todas_alteracoes[:3]:
    print(alteracao)

sem_criterio = [
    a for a in todas_alteracoes
    if not a.get("criterio")
    or a["criterio"] in ("Critério não identificado", "Não informado")
]

print("Alterações sem critério:", len(sem_criterio))

    # Consulta o ViaCEP e aplica a regra de prioridade
resultado = enriquecer_cliente(cliente)

    # Atualiza o bairro tratado com o valor escolhido
tratado["bairro"] = resultado["bairro_final"]

    # Informa à auditoria o motivo da escolha
criterios = {}

if resultado["bairro_final"] != cliente["bairro_padronizado"]:
        criterios["bairro"] = resultado["criterio"]
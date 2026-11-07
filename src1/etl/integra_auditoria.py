import pandas as pd
from pathlib import Path

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

    # Compara valoresoriginais e tratados
    alteracoes = compararDados(
        id_cliente=cliente["id_cliente"],        
        original=original,
        tratado=tratado
    )

    todas_alteracoes.extend(alteracoes)

print("Total de alterações identificadas:", len(todas_alteracoes))

# Mostra apenas as três primeiras alterações
for alteracao in todas_alteracoes[:3]:
    print(alteracao)

sem_criterio = [
    a for a in todas_alteracoes
    if not a.get("criterio")
    or a["criterio"] == "Critério não identificado"
]

print("Alterações sem critério:", len(sem_criterio))
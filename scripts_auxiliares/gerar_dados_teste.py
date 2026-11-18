
import csv
import random
from pathlib import Path
from datetime import date, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# Pasta onde os arquivos de teste serão salvos
PASTA_SAIDA = BASE_DIR / "dados_teste"

# Quantidades de registros que serão geradas
QUANTIDADES = [5000, 10000, 25000, 50000]

# Campos iguais aos do CSV original
COLUNAS = [
    "id_cliente",
    "razao_social",
    "cnpj",
    "telefone",
    "email",
    "bairro_informado",
    "cep",
    "cidade",
    "uf",
    "data_cadastro",
    "vendedor_responsavel"
]

# Dados fictícios para geração dos clientes
BAIRROS = [
    ("Águas Claras", "71926-750"),
    ("Taguatinga", "72010-120"),
    ("Guará", "71010-000"),
    ("Vicente Pires", "72005-250")
]

VENDEDORES = [
    "Carlos Silva",
    "Mariana Souza",
    "João Santos",
    "Ana Oliveira"
]


def gerar_cnpj(numero):
    """Gera um identificador de CNPJ fictício com 14 dígitos."""
    return f"{numero:014d}"

def gerar_telefone():
    """Gera um telefone fictício no formato brasileiro."""
    ddd = random.choice([61, 62, 63])
    numero = random.randint(900000000, 999999999)

    return f"({ddd}) {numero // 10000:05d}-{numero % 10000:04d}"

def gerar_data():
    """Gera uma data aleatória entre 2020 e a data atual."""
    inicio = date(2020, 1, 1)
    fim = date.today()

    dias = (fim - inicio).days
    data = inicio + timedelta(days=random.randint(0, dias))

    return data.strftime("%d/%m/%Y")

def gerar_cliente(numero):
    """Monta um registro fictício de cliente."""

    bairro, cep = random.choice(BAIRROS)

    return {
        "id_cliente": f"CLI{numero:06d}",
        "razao_social": f"Empresa Fictícia {numero}",
        "cnpj": gerar_cnpj(numero),
        "telefone": gerar_telefone(),
        "email": f"empresa{numero}@exemplo.com",
        "bairro_informado": bairro,
        "cep": cep,
        "cidade": "Brasília",
        "uf": "DF",
        "data_cadastro": gerar_data(),
        "vendedor_responsavel": random.choice(VENDEDORES)
    }


def gerar_csv(quantidade):
    """Gera um CSV com a quantidade solicitada de clientes."""

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    caminho = PASTA_SAIDA / f"clientes_teste_{quantidade}.csv"

    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=COLUNAS,
            delimiter=";"
        )

        escritor.writeheader()

        for numero in range(1, quantidade + 1):
            escritor.writerow(gerar_cliente(numero))

    print(f"Arquivo criado: {caminho.name} ({quantidade} registros)")


if __name__ == "__main__":
    print("Iniciando geração dos dados de escalabilidade...")

    for quantidade in QUANTIDADES:
        gerar_csv(quantidade)

    print("Geração de dados concluída!")

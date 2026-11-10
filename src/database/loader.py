import os
import sys
import django
import pandas as pd

# 1. Calcula a raiz exata do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# 2. Configura o ambiente do Django
web_dir = os.path.join(BASE_DIR, 'web')
if web_dir not in sys.path:
    sys.path.insert(0, web_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cliente.models import ClienteBruto, ClienteTratado

def encontrar_arquivo_por_prefixo(prefixos):
    """Procura na raiz por ficheiros que comecem com determinados termos"""
    for f in os.listdir(BASE_DIR):
        f_lower = f.lower()
        if any(f_lower.startswith(p) for p in prefixos) and f.endswith('.csv'):
            return os.path.join(BASE_DIR, f)
    return None

def obter_valor(row, *nomes_possiveis):
    """Procura o valor numa linha testando vários nomes de colunas (limpando espaços e BOM)"""
    for nome in nomes_possiveis:
        for col in row.index:
            col_limpa = str(col).strip().lower().replace('\ufeff', '')
            if col_limpa == nome.lower():
                val = row[col]
                if pd.notna(val):
                    return str(val).strip()
    return ''

def carregar_dados():
    print("=== INICIANDO CARGA ETL DIAGNÓSTICO ===")
    
    caminho_bruto = encontrar_arquivo_por_prefixo(['clientes_bruto', 'clientes_distribuidora', 'clientes'])
    caminho_tratado = encontrar_arquivo_por_prefixo(['clientes_tratados', 'clientes_padronizado'])
    
    print(f"Ficheiro Bruto: {caminho_bruto}")
    print(f"Ficheiro Tratado: {caminho_tratado}")

    # Limpa as tabelas antes de recarregar para garantir a gravação limpa
    ClienteBruto.objects.all().delete()
    ClienteTratado.objects.all().delete()
    print("-> Registos antigos removidos da base de dados com sucesso.")

    # 1. CARREGAR DADOS BRUTOS
    if caminho_bruto and os.path.exists(caminho_bruto):
        df_bruto = pd.read_csv(caminho_bruto, sep=None, engine='python', dtype=str, encoding='utf-8-sig')
        print(f"-> Encontradas {len(df_bruto)} linhas no CSV bruto.")
        
        sucessos = 0
        for index, row in df_bruto.iterrows():
            try:
                id_cli = obter_valor(row, 'id_cliente', 'id', 'cliente_id', 'codigo')
                if not id_cli:
                    continue
                
                ClienteBruto.objects.create(
                    id_cliente=id_cli,
                    razao_social=obter_valor(row, 'razao_social', 'nome', 'cliente'),
                    cnpj=obter_valor(row, 'cnpj', 'cpf_cnpj'),
                    telefone=obter_valor(row, 'telefone', 'fone', 'celular'),
                    email=obter_valor(row, 'email', 'correio_eletronico'),
                    bairro_informado=obter_valor(row, 'bairro_informado', 'bairro', 'bairro_original'),
                    cidade=obter_valor(row, 'cidade', 'municipio'),
                    uf=obter_valor(row, 'uf', 'estado'),
                    data_cadastro=obter_valor(row, 'data_cadastro', 'data', 'cadastro'),
                    vendedor_responsavel=obter_valor(row, 'vendedor_responsavel', 'vendedor', 'representante', 'nome_vendedor')
                )
                sucessos += 1
            except Exception as e:
                print(f"[ERRO BRUTO linha {index}]: {e}")
        print(f"-> Sucesso bruto: {sucessos} de {len(df_bruto)} inseridos.")
    else:
        print("[ALERTA] Ficheiro bruto não encontrado.")

    # 2. CARREGAR DADOS TRATADOS
    if caminho_tratado and os.path.exists(caminho_tratado):
        df_tratado = pd.read_csv(caminho_tratado, sep=None, engine='python', dtype=str, encoding='utf-8-sig')
        print(f"-> Encontradas {len(df_tratado)} linhas no CSV tratado.")
        
        sucessos = 0
        for index, row in df_tratado.iterrows():
            try:
                id_cli = obter_valor(row, 'id_cliente', 'id', 'cliente_id', 'codigo', 'cod_cliente', 'idcliente')
                if not id_cli:
                    continue

                raw_data = obter_valor(row, 'data_cadastro', 'data', 'cadastro', 'datacadastro')
                data_cad = None
                if raw_data:
                    data_parsed = pd.to_datetime(raw_data, errors='coerce', dayfirst=True)
                    if pd.notna(data_parsed):
                        data_cad = data_parsed.strftime('%Y-%m-%d')

                # Tenta obter o bairro tratado da coluna 'bairro_informado' ou 'bairro'
                bairro_val = obter_valor(row, 'bairro_informado', 'bairro', 'bairro_padronizado')

                ClienteTratado.objects.create(
                    id_cliente=id_cli,
                    razao_social=obter_valor(row, 'razao_social', 'nome', 'cliente'),
                    cnpj=obter_valor(row, 'cnpj', 'cpf_cnpj'),
                    telefone=obter_valor(row, 'telefone', 'fone', 'celular') or None,
                    email=obter_valor(row, 'email', 'correio_eletronico') or None,
                    bairro_informado=bairro_val or None,
                    cidade=obter_valor(row, 'cidade', 'municipio') or None,
                    uf=obter_valor(row, 'uf', 'estado') or None,
                    data_cadastro=data_cad,
                    vendedor_responsavel=obter_valor(row, 'vendedor_responsavel', 'vendedor', 'representante', 'nome_vendedor') or None
                )
                sucessos += 1
            except Exception as e:
                print(f"[ERRO TRATADO linha {index}]: {e}")
        print(f"-> Sucesso tratado: {sucessos} de {len(df_tratado)} inseridos.")
    else:
        print("[ALERTA] Ficheiro tratado não encontrado.")

    print("=== FIM DA CARGA ETL ===")

if __name__ == '__main__':
    carregar_dados()
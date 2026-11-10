import os
import sys
import django
import pandas as pd

# procura os arquivos na raiz exata do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

web_dir = os.path.join(BASE_DIR, 'web')
if web_dir not in sys.path:
    sys.path.insert(0, web_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cliente.models import ClienteBruto, ClienteTratado, AuditoriaAlteracao

def executar_etl():
    print("ETL rodando...")

if __name__ == "__main__":
    executar_etl()

def encontrar_arquivo_por_prefixo(prefixos):
    for f in os.listdir(BASE_DIR):
        f_lower = f.lower()
        if any(f_lower.startswith(p) for p in prefixos) and f.endswith('.csv'):
            return os.path.join(BASE_DIR, f)
    return None

def obter_valor(row, *nomes_possiveis):
    for nome in nomes_possiveis:
        for col in row.index:
            col_limpa = str(col).strip().lower().replace('\ufeff', '')
            if col_limpa == nome.lower():
                val = row[col]
                if pd.notna(val):
                    return str(val).strip()
    return ''

def carregar_dados():
    print("=== INICIANDO CARGA ETL E AUDITORIA ===")
    
    caminho_bruto = encontrar_arquivo_por_prefixo(['clientes_bruto', 'clientes_distribuidora', 'clientes'])
    caminho_tratado = encontrar_arquivo_por_prefixo(['clientes_tratados', 'clientes_padronizado'])
    
    print(f"Ficheiro Bruto: {caminho_bruto}")
    print(f"Ficheiro Tratado: {caminho_tratado}")

    # Limpa as tabelas antes de recarregar
    AuditoriaAlteracao.objects.all().delete()
    ClienteTratado.objects.all().delete()
    ClienteBruto.objects.all().delete()
    print("-> Registos antigos e auditorias limpos da base de dados.")

    # Dicionário para guardar os dados brutos e facilitar a comparação na auditoria
    dados_brutos_dict = {}

    #  CARREGAR DADOS BRUTOS
    if caminho_bruto and os.path.exists(caminho_bruto):
        df_bruto = pd.read_csv(caminho_bruto, sep=None, engine='python', dtype=str, encoding='utf-8-sig')
        print(f"-> Encontradas {len(df_bruto)} linhas no CSV bruto.")
        
        sucessos = 0
        for index, row in df_bruto.iterrows():
            try:
                id_cli = obter_valor(row, 'id_cliente', 'id', 'cliente_id', 'codigo')
                if not id_cli:
                    continue
                
                bairro_raw = obter_valor(row, 'bairro_informado', 'bairro', 'bairro_original')
                razao_raw = obter_valor(row, 'razao_social', 'nome', 'cliente')
                cnpj_raw = obter_valor(row, 'cnpj', 'cpf_cnpj')
                tel_raw = obter_valor(row, 'telefone', 'fone', 'celular')
                email_raw = obter_valor(row, 'email', 'correio_eletronico')
                cidade_raw = obter_valor(row, 'cidade', 'municipio')
                uf_raw = obter_valor(row, 'uf', 'estado')
                data_raw = obter_valor(row, 'data_cadastro', 'data', 'cadastro')
                vend_raw = obter_valor(row, 'vendedor_responsavel', 'vendedor', 'representante')

                ClienteBruto.objects.create(
                    id_cliente=id_cli,
                    razao_social=razao_raw,
                    cnpj=cnpj_raw,
                    telefone=tel_raw,
                    email=email_raw,
                    bairro_informado=bairro_raw,
                    cidade=cidade_raw,
                    uf=uf_raw,
                    data_cadastro=data_raw,
                    vendedor_responsavel=vend_raw
                )

                # Guarda num dicionário para auditoria posterior
                dados_brutos_dict[id_cli] = {
                    'bairro_informado': bairro_raw,
                    'telefone': tel_raw,
                    'cidade': cidade_raw,
                }
                sucessos += 1
            except Exception as e:
                print(f"[ERRO BRUTO linha {index}]: {e}")
        print(f"-> Sucesso bruto: {sucessos} de {len(df_bruto)} inseridos.")

    # CARREGAR OS DADOS TRATADOS E GERAR AUDITORIA
    if caminho_tratado and os.path.exists(caminho_tratado):
        df_tratado = pd.read_csv(caminho_tratado, sep=None, engine='python', dtype=str, encoding='utf-8-sig')
        print(f"-> Encontradas {len(df_tratado)} linhas no CSV tratado.")
        
        sucessos = 0
        auditorias_criadas = 0
        for index, row in df_tratado.iterrows():
            try:
                id_cli = obter_valor(row, 'id_cliente', 'id', 'cliente_id', 'codigo')
                if not id_cli:
                    continue

                raw_data = obter_valor(row, 'data_cadastro', 'data', 'cadastro')
                data_cad = None
                if raw_data:
                    data_parsed = pd.to_datetime(raw_data, errors='coerce', dayfirst=True)
                    if pd.notna(data_parsed):
                        data_cad = data_parsed.strftime('%Y-%m-%d')

                bairro_tratado = obter_valor(row, 'bairro_informado', 'bairro', 'bairro_padronizado')
                tel_tratado = obter_valor(row, 'telefone', 'fone', 'celular')
                cidade_tratada = obter_valor(row, 'cidade', 'municipio')

                # Cria o cliente tratado na BD
                cliente_obj = ClienteTratado.objects.create(
                    id_cliente=id_cli,
                    razao_social=obter_valor(row, 'razao_social', 'nome', 'cliente'),
                    cnpj=obter_valor(row, 'cnpj', 'cpf_cnpj'),
                    telefone=tel_tratado or None,
                    email=obter_valor(row, 'email', 'correio_eletronico') or None,
                    bairro_informado=bairro_tratado or None,
                    cidade=cidade_tratada or None,
                    uf=obter_valor(row, 'uf', 'estado') or None,
                    data_cadastro=data_cad,
                    vendedor_responsavel=obter_valor(row, 'vendedor_responsavel', 'vendedor') or None
                )
                sucessos += 1

                # Compara com o bruto para gerar registo de auditoria automático
                if id_cli in dados_brutos_dict:
                    bruto_info = dados_brutos_dict[id_cli]
                    
                    # Verifica se o bairro mudou (padronização ViaCEP/ETL)
                    bairro_original = bruto_info.get('bairro_informado', '')
                    if bairro_original != bairro_tratado:
                        AuditoriaAlteracao.objects.create(
                            cliente=cliente_obj,
                            id_cliente=id_cli,
                            campo_alterado='bairro_informado',
                            valor_original=bairro_original,
                            valor_tratado=bairro_tratado,
                            criterio='Padronização e Enriquecimento via ViaCEP / Pipeline ETL'
                        )
                        auditorias_criadas += 1

            except Exception as e:
                print(f"[ERRO TRATADO linha {index}]: {e}")
        
        print(f"-> Sucesso tratado: {sucessos} de {len(df_tratado)} inseridos.")
        print(f"-> Registos de auditoria gerados automaticamente: {auditorias_criadas}")
    else:
        print("[ALERTA] Ficheiro tratado não encontrado.")

    print("=== FIM DA CARGA ETL E AUDITORIA ===")

if __name__ == '__main__':
    carregar_dados()
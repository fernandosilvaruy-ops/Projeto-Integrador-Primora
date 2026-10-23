import re
import pandas as pd

# Carregar o ficheiro CSV (separador por ponto e vírgula)
df = pd.read_csv('clientes_distribuidora_vetor.csv', sep=';')


# 1. Mapear formatos de CNPJ
def analisar_cnpj(val):
  val_str = str(val).strip()
  digitos = re.sub(r'\D', '', val_str)
  if len(digitos) != 14:
    return f'Inválido (tamanho {len(digitos)} dígitos)'
  elif not re.match(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', val_str):
    return 'Apenas números (sem pontuação)'
  else:
    return 'Formato Correto'


df['status_cnpj'] = df['cnpj'].apply(analisar_cnpj)

# 2. Mapear padrões de telefones
def analisar_telefone(val):
  val_str = str(val).strip()
  digitos = re.sub(r'\D', '', val_str)
  if '+' in val_str and len(digitos) == 13:
    return 'Com DDI e DDD (+55 ...)'
  elif len(digitos) == 11:
    return 'Com DDD (11 dígitos - com 9º dígito)'
  elif len(digitos) == 10:
    return 'Com DDD (10 dígitos)'
  else:
    return f'Outro formato ({len(digitos)} dígitos)'


df['status_telefone'] = df['telefone'].apply(analisar_telefone)


# 3. Mapear variações no formato das Datas
def analisar_data(val):
  val_str = str(val).strip()
  if re.match(r'^\d{4}-\d{2}-\d{2}$', val_str):
    return 'ISO (YYYY-MM-DD)'
  elif re.match(r'^\d{2}/\d{2}/\d{4}$', val_str):
    return 'BR (DD/MM/YYYY)'
  elif re.match(r'^\d{2}-\d{2}-\d{4}$', val_str):
    return 'Hífen (DD-MM-YYYY)'
  elif re.match(r'^[A-Za-z]{3}\s\d{1,2},\s\d{4}$', val_str):
    return 'Extenso Inglês (Mmm DD, YYYY)'
  else:
    return 'Outro formato'


df['status_data'] = df['data_cadastro'].apply(analisar_data)

# Exibir os resumos dos mapeamentos
print('=== RESUMO CNPJ ===')
print(df['status_cnpj'].value_counts())

print('\n=== RESUMO TELEFONES ===')
print(df['status_telefone'].value_counts())

print('\n=== RESUMO DATAS ===')
print(df['status_data'].value_counts())
import re
import sys

import pandas as pd

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'clientes_distribuidora_vetor.csv'

df = pd.read_csv(ARQUIVO, sep=';', dtype=str, encoding='utf-8')
df.columns = df.columns.str.strip().str.lower()


def _digito(base, pesos):
  resto = sum(n * p for n, p in zip(base, pesos)) % 11
  return 0 if resto < 2 else 11 - resto


def cnpj_valido(cnpj_limpo):
  """cnpj_limpo: 14 caracteres [0-9A-Z], sem pontuação, já em maiúsculas."""
  if cnpj_limpo == cnpj_limpo[0] * 14:
    return False
  valores = [ord(c) - 48 for c in cnpj_limpo]
  pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
  pesos2 = [6] + pesos1
  d1 = _digito(valores[:12], pesos1)
  d2 = _digito(valores[:12] + [d1], pesos2)
  return valores[12] == d1 and valores[13] == d2


def analisar_cnpj(val):
  if pd.isna(val) or not str(val).strip():
    return 'Vazio'
  val_str = str(val).strip().upper()
  # Remove só a pontuação (NÃO usar \D, que apagaria as letras)
  limpo = re.sub(r'[.\-/\s]', '', val_str)

  if not re.fullmatch(r'[0-9A-Z]{12}\d{2}', limpo):
    return 'Inválido (formato ou tamanho)'
  if not cnpj_valido(limpo):
    return 'Inválido (dígito verificador)'

  tipo = 'alfanumérico' if re.search(r'[A-Z]', limpo[:12]) else 'numérico'
  mascara = r'[0-9A-Z]{2}\.[0-9A-Z]{3}\.[0-9A-Z]{3}/[0-9A-Z]{4}-\d{2}'
  pontuacao = 'com pontuação' if re.fullmatch(mascara, val_str) else 'sem pontuação'
  return f'Válido ({tipo}, {pontuacao})'


df['status_cnpj'] = df['cnpj'].apply(analisar_cnpj)


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

print('=== RESUMO CNPJ ===')
print(df['status_cnpj'].value_counts())

print('\n=== RESUMO TELEFONES ===')
print(df['status_telefone'].value_counts())

print('\n=== RESUMO DATAS ===')
print(df['status_data'].value_counts())
import re
import sys
import unicodedata
from datetime import datetime

import pandas as pd

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'clientes_distribuidora_vetor.csv'
SAIDA = 'clientes_padronizado.csv'

df = pd.read_csv(ARQUIVO, sep=';', dtype=str, encoding='utf-8')
df.columns = df.columns.str.strip().str.lower()


# ---------------------------------------------------------------- CNPJ
def limpar_cnpj(val):
  """Tira a pontuação e devolve 14 caracteres [0-9A-Z], ou None se o formato não serve."""
  if pd.isna(val):
    return None
  limpo = re.sub(r'[.\-/\s]', '', str(val)).upper()
  return limpo if re.fullmatch(r'[0-9A-Z]{12}\d{2}', limpo) else None


def _digito(base, pesos):
  resto = sum(n * p for n, p in zip(base, pesos)) % 11
  return 0 if resto < 2 else 11 - resto


def cnpj_valido(val):
  limpo = limpar_cnpj(val)
  if limpo is None or limpo == limpo[0] * 14:
    return False
  valores = [ord(c) - 48 for c in limpo]  # '0'-'9' -> 0-9, 'A' -> 17, ...
  pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
  pesos2 = [6] + pesos1
  d1 = _digito(valores[:12], pesos1)
  d2 = _digito(valores[:12] + [d1], pesos2)
  return valores[12] == d1 and valores[13] == d2


def padronizar_cnpj(val):
  limpo = limpar_cnpj(val)
  if limpo is None:
    return None
  return f'{limpo[:2]}.{limpo[2:5]}.{limpo[5:8]}/{limpo[8:12]}-{limpo[12:]}'


def padronizar_telefone(val):
  if pd.isna(val):
    return None
  d = re.sub(r'\D', '', str(val))
  # Remove o DDI 55 quando ele está presente (12 ou 13 dígitos)
  if len(d) in (12, 13) and d.startswith('55'):
    d = d[2:]
  if len(d) == 11:  # celular: DDD + 9 dígitos
    return f'({d[:2]}) {d[2:7]}-{d[7:]}'
  if len(d) == 10:  # fixo: DDD + 8 dígitos
    return f'({d[:2]}) {d[2:6]}-{d[6:]}'
  return None


MESES = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
         'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}


def padronizar_data(val):
  """Converte qualquer formato conhecido para YYYY-MM-DD."""
  if pd.isna(val):
    return None
  s = str(val).strip()
  try:
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
      d = datetime.strptime(s, '%Y-%m-%d')
    elif re.fullmatch(r'\d{2}/\d{2}/\d{4}', s):
      d = datetime.strptime(s, '%d/%m/%Y') 
    elif re.fullmatch(r'\d{2}-\d{2}-\d{4}', s):
      d = datetime.strptime(s, '%d-%m-%Y')
    else:
      m = re.fullmatch(r'([A-Za-z]{3})\s(\d{1,2}),\s(\d{4})', s)
      if not m:
        return None
      d = datetime(int(m.group(3)), MESES[m.group(1).lower()], int(m.group(2)))
  except (ValueError, KeyError): 
    return None
  return d.strftime('%Y-%m-%d')


def _sem_acento(txt):
  return unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore').decode().lower()


REGRAS_BAIRRO = [
  ('aguas claras', 'Águas Claras'),
  ('taguatinga', 'Taguatinga'),
  ('vicente pires', 'Vicente Pires'),
  ('v. pires', 'Vicente Pires'),
  ('vte pires', 'Vicente Pires'),
  ('guara', 'Guará'),
]


def padronizar_bairro(val):
  if pd.isna(val) or not str(val).strip():
    return 'Não informado'
  texto = _sem_acento(str(val))
  for trecho, nome in REGRAS_BAIRRO:
    if trecho in texto:
      return nome
  return str(val).strip().title()  


def padronizar_cep(val):
  if pd.isna(val):
    return None
  d = re.sub(r'\D', '', str(val))
  if len(d) != 8 or d == '00000000': 
    return None
  return f'{d[:5]}-{d[5:]}'


df['cnpj_valido'] = df['cnpj'].apply(cnpj_valido)
df['cnpj_padronizado'] = df['cnpj'].apply(padronizar_cnpj)
df['telefone_padronizado'] = df['telefone'].apply(padronizar_telefone)
df['data_cadastro_padronizada'] = df['data_cadastro'].apply(padronizar_data)
df['bairro_padronizado'] = df['bairro_informado'].apply(padronizar_bairro)
df['cep_padronizado'] = df['cep'].apply(padronizar_cep)

# o Excel abre o arquivo com os acentos corretos
df.to_csv(SAIDA, sep=';', index=False, encoding='utf-8-sig')

print(f'Arquivo gerado: {SAIDA} ({len(df)} linhas)\n')
print(f"CNPJs válidos:           {df['cnpj_valido'].sum()} de {len(df)}")
print(f"Telefones não reconhecidos: {df['telefone_padronizado'].isna().sum()}")
print(f"Datas não reconhecidas:     {df['data_cadastro_padronizada'].isna().sum()}")
print(f"CEPs ausentes/inválidos:    {df['cep_padronizado'].isna().sum()}")
print('\nBairros após padronização:')
print(df['bairro_padronizado'].value_counts())
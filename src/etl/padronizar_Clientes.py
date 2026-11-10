import re
import sys
import unicodedata
from datetime import datetime
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src1.servico import cep_servico

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'clientes_distribuidora_vetor.csv'
SAIDA = 'clientes_tratados.csv'

df = pd.read_csv(ARQUIVO, sep=';', dtype=str, encoding='utf-8')
df.columns = df.columns.str.strip().str.lower()


# ---------------------------------------------------------------- CNPJ
def limpar_cnpj(val):
    """Tira a pontuação e devolve 14 caracteres [0-9], ou None se o formato não servir."""
    if pd.isna(val):
        return None
    limpo = re.sub(r'\D', '', str(val))
    return limpo if len(limpo) == 14 else None

def cnpj_valido(val):
    """
    Validação estrutural para dados fictícios:
    Verifica se tem 14 dígitos e se não é uma sequência repetida (ex: 00000000000000).
    """
    limpo = limpar_cnpj(val)
    if limpo is None or limpo == limpo[0] * 14:
        return False
    return True  # Aceita qualquer estrutura válida de 14 dígitos para fins de teste

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


def padronizar_bairro(row):
    """
    1. Tenta usar o bairro informado no CSV, aplicando as regras locais e acentuação.
    2. Se estiver vazio/ausente, consulta a API do ViaCEP via módulo do colega.
    """
    bairro_informado = row.get('bairro_informado')
    
    #  Se o bairro no CSV não está vazio/nulo, aplica a sua lógica existente
    if not pd.isna(bairro_informado) and str(bairro_informado).strip() not in ['', 'nan', 'None', 'Não informado']:
        texto = _sem_acento(str(bairro_informado))
        for trecho, nome in REGRAS_BAIRRO:
            if trecho in texto:
                return nome
        return str(bairro_informado).strip().title()
    
    #  Se não tem bairro informado, recorre ao ViaCEP usando o CEP do registo
    cep = row.get('cep')
    if not pd.isna(cep):
        resultado = cep_servico.buscar_cep(cep)
        if isinstance(resultado, dict) and "erro" not in resultado:
            bairro_api = resultado.get('bairro')
            if bairro_api:
                return bairro_api.strip().title()
                
    return 'Não informado'

def padronizar_cep(val):
  if pd.isna(val):
    return None
  d = re.sub(r'\D', '', str(val))
  if len(d) != 8 or d == '00000000': 
    return None
  return f'{d[:5]}-{d[5:]}'


# 1. Aplica todas as limpezas e preenchimentos
cnpj_limpo = df['cnpj'].apply(limpar_cnpj)
tel_pad = df['telefone'].apply(padronizar_telefone)
data_pad = df['data_cadastro'].apply(padronizar_data)
cep_pad = df['cep'].apply(padronizar_cep)
bairro_pad = df.apply(padronizar_bairro, axis=1)

# 2. Cria a coluna de validação do CNPJ (1 se for válido/14 dígitos, 0 caso contrário)
df['cnpj_valido'] = cnpj_limpo.notna().astype(int)

# 3. Atribui os dados limpos às colunas oficiais e de suporte
df['telefone_padronizado'] = tel_pad
df['data_cadastro_padronizada'] = data_pad
df['bairro_informado'] = bairro_pad
df['cep_padronizado'] = cep_pad

df['cnpj'] = cnpj_limpo
df['telefone'] = tel_pad
df['data_cadastro'] = data_pad
df['cep'] = cep_pad
df['bairro'] = bairro_pad

# 4. Guarda o ficheiro tratado
SAIDA = 'clientes_tratados.csv'
df.to_csv(SAIDA, sep=';', index=False, encoding='utf-8-sig')

# 5. Relatório de qualidade
print(f'Ficheiro gerado: {SAIDA} ({len(df)} linhas)\n')
print(f"CNPJs válidos:              {df['cnpj_valido'].sum()} de {len(df)}")
print(f"Telefones não reconhecidos: {df['telefone_padronizado'].isna().sum()}")
print(f"Datas não reconhecidas:     {df['data_cadastro_padronizada'].isna().sum()}")
print(f"CEPs ausentes/inválidos:    {df['cep_padronizado'].isna().sum()}")
print('\nBairros após padronização:')
print(df['bairro_informado'].value_counts())
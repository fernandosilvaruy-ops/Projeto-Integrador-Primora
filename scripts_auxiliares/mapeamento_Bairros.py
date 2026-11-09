import re
import sys
import unicodedata

import pandas as pd

ARQUIVO = sys.argv[1] if len(sys.argv) > 1 else 'clientes_distribuidora_vetor.csv'
SAIDA = 'mapeamento_bairros.csv'

df = pd.read_csv(ARQUIVO, sep=';', dtype=str, encoding='utf-8')
df.columns = df.columns.str.strip().str.lower()


def tirar_acento(txt):
  """Remove acentos mantendo maiúsculas/minúsculas."""
  return unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore').decode()


def chave(txt):
  """Forma 'neutra' do texto: sem acento, minúsculo, espaços normalizados.
  Dois valores com a mesma chave só diferem por acento, caixa ou espaços."""
  return re.sub(r'\s+', ' ', tirar_acento(txt).lower()).strip()


# (trecho que aparece no texto, nome padrão do bairro)
REGRAS_BAIRRO = [
  ('aguas claras', 'Águas Claras'),
  ('taguatinga', 'Taguatinga'),
  ('vicente pires', 'Vicente Pires'),
  ('v. pires', 'Vicente Pires'),
  ('vte pires', 'Vicente Pires'),
  ('guara', 'Guará'),
]


def bairro_base(txt):
  c = chave(txt)
  for trecho, nome in REGRAS_BAIRRO:
    if trecho in c:
      return nome
  return 'REVISAR (sem regra)'


def complemento(txt):
  """Detalhe que se perderia ao padronizar: Sul, Norte, I, II."""
  c = chave(txt)
  achados = re.findall(r'\b(sul|norte)\b', c)
  if re.search(r'\bguara\s+(i{1,2})\b', c):
    achados.append(re.search(r'\bguara\s+(i{1,2})\b', c).group(1).upper())
  return ', '.join(a.capitalize() if a in ('sul', 'norte') else a for a in achados)



contagem = df['bairro_informado'].value_counts(dropna=False)
linhas = []
for valor, qtd in contagem.items():
  vazio = pd.isna(valor) or not str(valor).strip()
  raw = '' if pd.isna(valor) else str(valor)
  base = 'Não informado' if vazio else bairro_base(raw)
  linhas.append({
    'valor_original': raw,
    'ocorrencias': qtd,
    # --- 2. acento, caixa e espaços
    'tem_acento': raw != tirar_acento(raw),
    'caixa': ('vazio' if vazio else 'MAIÚSCULAS' if raw.isupper()
              else 'minúsculas' if raw.islower() else 'misto'),
    'espacos_extras': raw != raw.strip() or bool(re.search(r'\s{2,}', raw)),
    # --- 3. parênteses e outros ruídos
    'tem_parenteses': '(' in raw or ')' in raw,
    'sufixo_df': bool(re.search(r'\s*[-/]\s*df$', raw.strip(), re.I)),
    'abreviacao': bool(re.search(r'(^|\s)(v\.|vte)(\s|$)', raw, re.I)),
    'complemento': complemento(raw),
    # --- 4. proposta
    'chave_neutra': chave(raw),
    'bairro_base_sugerido': base,
  })

mapa = pd.DataFrame(linhas)
# Precisa de dicionário se o texto não é exatamente o nome padrão
mapa['precisa_correcao'] = mapa['valor_original'] != mapa['bairro_base_sugerido']
mapa = mapa.sort_values(['bairro_base_sugerido', 'chave_neutra', 'valor_original'])
mapa.to_csv(SAIDA, sep=';', index=False, encoding='utf-8-sig')


print(f"Valores únicos: {len(mapa)} (em {len(df)} clientes)\n")

print('=== 1. TODOS OS VALORES ÚNICOS ===')
print(mapa[['valor_original', 'ocorrencias', 'bairro_base_sugerido']].to_string(index=False))

print('\n=== 2. MESMA CHAVE, ESCRITAS DIFERENTES (acento / caixa / espaços) ===')
grupos = mapa.groupby('chave_neutra')['valor_original'].apply(list)
for k, vs in grupos.items():
  if len(vs) > 1:
    print(f"  {k!r}: {vs}")

print('\n=== 2b. CONTAGEM POR TIPO DE PROBLEMA ===')
print(f"  Com acento:               {mapa['tem_acento'].sum()} valores")
print(f"  Tudo MAIÚSCULAS:          {(mapa['caixa'] == 'MAIÚSCULAS').sum()} valores")
print(f"  Tudo minúsculas:          {(mapa['caixa'] == 'minúsculas').sum()} valores")
print(f"  Espaços extras:           {mapa['espacos_extras'].sum()} valores")
print(f"  Sufixo -DF ou /DF:        {mapa['sufixo_df'].sum()} valores")
print(f"  Abreviação (V., Vte):     {mapa['abreviacao'].sum()} valores")

print('\n=== 3. CASOS COM PARÊNTESES ===')
print(mapa.loc[mapa['tem_parenteses'], ['valor_original', 'ocorrencias']].to_string(index=False))

print('\n=== 4. LISTA INICIAL PARA O DICIONÁRIO DE CORREÇÃO ===')
lista = mapa[mapa['precisa_correcao']]
print(lista[['valor_original', 'bairro_base_sugerido', 'complemento']].to_string(index=False))

print('\n=== COMPLEMENTOS QUE SE PERDEM SE PADRONIZAR SÓ O BAIRRO ===')
comp = mapa[mapa['complemento'] != '']
print(comp.groupby(['bairro_base_sugerido', 'complemento'])['ocorrencias'].sum().to_string())

print(f"\nTabela completa salva em: {SAIDA}")
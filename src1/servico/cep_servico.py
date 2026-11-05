import requests
import json
import pathlib
import unicodedata

CAMINHO_CACHE = pathlib.Path(__file__).resolve().parent / "cache_cep.json"

def carregar_cache():
    try:
        with open(CAMINHO_CACHE, "r", encoding="utf-8") as arquivo:
            cache = json.load(arquivo)

        if not isinstance(cache, dict):
            raise ValueError("O cache deve ser um dicionário.")
        
        return cache

    except FileNotFoundError:
        print("Arquivo de cache não encontrado. Criando um novo cache...")
        return {}
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo de cache. Criando um novo cache...")
        return {}

def salvar_cache(cache):
    try:
     with open(CAMINHO_CACHE, "w", encoding="utf-8") as arquivo:
        json.dump(cache, arquivo, indent=4, ensure_ascii=False)
   
    except OSError as e:
        print(f"Erro ao salvar o cache: {e}")
    
def buscar_cep(cep):  # Remove caracteres especiais (como traços ou pontos), mantendo apenas os números
    cep = "".join(c for c in str(cep) if c.isdigit())
    
    # Valida se o CEP limpo possui exatamente 8 dígitos
    if len(cep) != 8:
        return {"erro": "CEP deve ter 8 dígitos"}
    
    cache = carregar_cache()
    if cep in cache:
        return cache[cep]    
        
    try:
        # Faz a requisição HTTP GET para a API do ViaCEP com limite de tempo (timeout) de 5 segundos
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        
        # Dispara um erro caso a resposta HTTP tenha retornado falha (ex: 404, 500)
        r.raise_for_status()
        
        # Converte o conteúdo da resposta da API de JSON para um dicionário em Python
        dados = r.json()
        
        # O ViaCEP retorna um campo "erro: true" quando o CEP tem 8 dígitos mas não existe na base
        if dados.get("erro"):
            return {"erro": "CEP não encontrado"}

        cache[cep] = dados
        salvar_cache(cache)

        # Retorna o dicionário com os dados do endereço caso tudo ocorra bem
        return dados
        
    except requests.RequestException as e:
        # Captura erros de conexão, falhas de rede ou problemas no timeout
        return {"erro": f"Falha na requisição: {e}"}

# Bloco de teste: está no teste_cep.py


def normalizar_texto(texto):
    """
    Padroniza textos para comparação, ignorando
    diferenças de maiúsculas, espaços e acentos.
    """
    if not texto:
        return ""

    texto = str(texto).strip().lower()

    texto = unicodedata.normalize("NFKD", texto)

    return "".join(
        caractere for caractere in texto
        if not unicodedata.combining(caractere)
    )


def validar_endereco(cliente):
    """
    Compara o endereço cadastrado do cliente
    com os dados retornados pelo ViaCEP.

    Não modifica os dados do cliente.
    """

    # Consulta o CEP utilizando o serviço e o cache existentes
    dados_api = buscar_cep(cliente.cep)

    # Verifica se houve erro na consulta
    if "erro" in dados_api:
        return {
            "cliente": cliente.razao_social,
            "status": "ERRO",
            "motivo": dados_api["erro"]
        }

    # Campos que serão comparados
    campos = {
        "bairro": "bairro",
        "cidade": "localidade",
        "uf": "uf"
    }

    divergencias = {}
    campos_nao_verificados = []

    # Compara os dados cadastrados com os retornados pela API
    for campo_cliente, campo_api in campos.items():

        valor_cliente = getattr(cliente, campo_cliente, None)
        valor_api = dados_api.get(campo_api)

        # Não considera campos vazios como correspondentes
        if not valor_cliente or not valor_api:
            campos_nao_verificados.append(campo_cliente)
            continue

        if normalizar_texto(valor_cliente) != normalizar_texto(valor_api):
            divergencias[campo_cliente] = {
                "cadastrado": valor_cliente,
                "viacep": valor_api
            }

    # Define o resultado geral da validação
    if divergencias:
        status = "DIVERGENTE"
    elif campos_nao_verificados:
        status = "INCOMPLETO"
    else:
        status = "VALIDADO"

    return {
        "cliente": cliente.razao_social,
        "cep": cliente.cep,
        "status": status,
        "divergencias": divergencias,
        "campos_nao_verificados": campos_nao_verificados
    }


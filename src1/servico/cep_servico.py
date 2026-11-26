import json
import pathlib
import unicodedata
import requests
from urllib.parse import quote

CAMINHO_CACHE = pathlib.Path(__file__).resolve().parent / "cache_cep.json"


def carregar_cache():
    try:
        with open(CAMINHO_CACHE, "r", encoding="utf-8") as arquivo:
            cache = json.load(arquivo)

        if not isinstance(cache, dict):
            return {}

        return cache
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def salvar_cache(cache):
    try:
        with open(CAMINHO_CACHE, "w", encoding="utf-8") as arquivo:
            json.dump(cache, arquivo, indent=4, ensure_ascii=False)
    except OSError as e:
        print(f"Erro ao salvar o cache: {e}")


def buscar_cep(cep):
    if cep is None:
        return {"erro": "CEP não informado"}

    cep_limpo = "".join(c for c in str(cep) if c.isdigit())

    if len(cep_limpo) != 8:
        return {"erro": "CEP deve ter 8 dígitos"}

    cache = carregar_cache()
    if cep_limpo in cache and isinstance(cache[cep_limpo], dict):
        return cache[cep_limpo]

    try:
        resposta = requests.get(
            f"https://viacep.com.br/ws/{cep_limpo}/json/",
            timeout=5,
        )
        resposta.raise_for_status()
        dados = resposta.json()

        if not isinstance(dados, dict) or dados.get("erro"):
            return {"erro": "CEP não encontrado"}

        endereco_enriquecido = {
            "cep": str(dados.get("cep") or cep_limpo).strip(),
            "logradouro": str(dados.get("logradouro") or "").strip().title(),
            "bairro": str(dados.get("bairro") or "").strip().title(),
            "localidade": str(dados.get("localidade") or "").strip().title(),
            "uf": str(dados.get("uf") or "").strip().upper(),
        }

        cache[cep_limpo] = endereco_enriquecido
        salvar_cache(cache)
        return endereco_enriquecido

    except requests.RequestException as e:
        return {"erro": f"Falha na requisição: {e}"}
    except ValueError:
        return {"erro": "Resposta inválida da API ViaCEP"}


def normalizar_texto(texto):
    if not texto:
        return ""

    texto_limpo = str(texto).strip().lower()
    texto_sem_acento = unicodedata.normalize("NFKD", texto_limpo)
    return "".join(
        caractere for caractere in texto_sem_acento
        if not unicodedata.combining(caractere)
    )


def obter_bairro_cliente(cliente):
    bairro = getattr(cliente, "bairro_informado", None)
    if bairro not in (None, ""):
        return bairro
    return getattr(cliente, "bairro", "")


def validar_endereco(cliente):
    nome_cliente = getattr(cliente, "razao_social", "") or str(cliente)
    cep_cliente = getattr(cliente, "cep", "")
    dados_api = buscar_cep(cep_cliente)

    if "erro" in dados_api:
        return {
            "cliente": nome_cliente,
            "cep": cep_cliente,
            "status": "ERRO",
            "motivo": dados_api["erro"],
            "dados_enriquecidos": None,
        }

    campos = {
        "bairro": (obter_bairro_cliente(cliente), "bairro"),
        "cidade": (getattr(cliente, "cidade", None), "localidade"),
        "uf": (getattr(cliente, "uf", None), "uf"),
    }

    divergencias = {}
    campos_nao_verificados = []

    for campo_cliente, (valor_cliente, campo_api) in campos.items():
        valor_api = dados_api.get(campo_api)

        if not valor_cliente or not valor_api:
            campos_nao_verificados.append(campo_cliente)
            continue

        if normalizar_texto(valor_cliente) != normalizar_texto(valor_api):
            divergencias[campo_cliente] = {
                "cadastrado": valor_cliente,
                "viacep": valor_api,
            }

    if divergencias:
        status = "DIVERGENTE"
    elif campos_nao_verificados:
        status = "INCOMPLETO"
    else:
        status = "VALIDADO"

    return {
        "cliente": nome_cliente,
        "cep": cep_cliente,
        "status": status,
        "divergencias": divergencias,
        "campos_nao_verificados": campos_nao_verificados,
        "dados_enriquecidos": dados_api,
    }

def buscar_cep_por_bairro(cidade: str, uf: str, bairro: str) -> str:
    cidade_limpa = (cidade or "").strip()
    uf_limpa = (uf or "").strip().upper()
    bairro_limpo = (bairro or "").strip()

    if not bairro_limpo or not cidade_limpa or len(bairro_limpo) < 3:
        return ""

    uf_rota = uf_limpa if len(uf_limpa) == 2 else "SP"
    chave_cache = (
        f"bairro:{uf_rota}:"
        f"{normalizar_texto(cidade_limpa)}:"
        f"{normalizar_texto(bairro_limpo)}"
    )

    cache = carregar_cache()
    if chave_cache in cache and isinstance(cache[chave_cache], str) and cache[chave_cache]:
        return cache[chave_cache]

    cidade_sem_acento = normalizar_texto(cidade_limpa).title()
    bairro_sem_acento = normalizar_texto(bairro_limpo).title()

    tentativas = [
        (cidade_limpa, bairro_limpo),
        (cidade_sem_acento, bairro_sem_acento),
        (cidade_sem_acento, cidade_sem_acento),
    ]

    for cid, termo_busca in tentativas:
        if len(termo_busca.strip()) < 3:
            continue

        url = (
            f"https://viacep.com.br/ws/{quote(uf_rota)}/"
            f"{quote(cid.strip())}/{quote(termo_busca.strip())}/json/"
        )
        try:
            resp = requests.get(url, timeout=6)
            if resp.status_code != 200 or not resp.text.strip():
                continue
            dados = resp.json()
            if isinstance(dados, list):
                for item in dados:
                    if isinstance(item, dict):
                        cep = str(item.get("cep") or "").strip()
                        if cep:
                            cache[chave_cache] = cep
                            salvar_cache(cache)
                            return cep
        except (requests.RequestException, ValueError):
            continue

    return ""
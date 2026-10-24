import requests

def buscar_cep(cep):
    cep = "".join(c for c in cep if c.isdigit())
    if len(cep) != 8:
        return {"erro": "CEP deve ter 8 dígitos"}
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        r.raise_for_status()
        dados = r.json()
        if dados.get("erro"):
            return {"erro": "CEP não encontrado"}
        return dados
    except requests.RequestException as e:
        return {"erro": f"Falha na requisição: {e}"}

for c in ["71725-100", "99999999", "123"]:
    print(c, "->", buscar_cep(c))


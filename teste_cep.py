import requests

# Função responsável por consultar um CEP na API do ViaCEP
def buscar_cep(cep):
    # Remove caracteres especiais (como traços ou pontos), mantendo apenas os números
    cep = "".join(c for c in cep if c.isdigit())
    
    # Valida se o CEP limpo possui exatamente 8 dígitos
    if len(cep) != 8:
        return {"erro": "CEP deve ter 8 dígitos"}
        
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
            
        # Retorna o dicionário com os dados do endereço caso tudo ocorra bem
        return dados
        
    except requests.RequestException as e:
        # Captura erros de conexão, falhas de rede ou problemas no timeout
        return {"erro": f"Falha na requisição: {e}"}

# Bloco de teste: percorre uma lista com diferentes formatos de CEP e imprime o resultado
for c in ["71725-100", "99999999", "123"]:
    print(c, "->", buscar_cep(c))

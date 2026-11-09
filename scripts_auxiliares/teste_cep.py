from src1.servico.cep_servico import buscar_cep
from src1.servico.cep_servico import carregar_cache, salvar_cache, buscar_cep

cache = carregar_cache()

print("Dados armazenados:", cache)
print("CEP encontrado:", "01001000" in cache)
cep = "71725-100"

resultado = buscar_cep(cep)
    
print(resultado)
    
print("Conteúdo do cache:", carregar_cache()) 

cache_teste = {
    "71725100": {
        "bairro": "Candangolândia",
        "cidade": "Brasília",
        "uf": "DF"
    }
}



resultado = carregar_cache()

print(resultado)

buscar_cep("01001-000")
buscar_cep("01001-000")
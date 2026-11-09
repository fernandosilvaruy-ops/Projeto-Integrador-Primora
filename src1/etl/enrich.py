from src1.servico.cep_servico import buscar_cep
from src1.etl.regra_prioridade import decidir_bairro


def enriquecer_cliente(cliente):

    # Pega os dados do cliente
    cep = cliente["cep_padronizado"]
    bairro = cliente["bairro_padronizado"]

    # Consulta o CEP
    dados_api = buscar_cep(cep)

    print("Bairro retornado pelo ViaCEP:", dados_api.get("bairro")) 
    # Verifica se houve erro na consulta
    if "erro" in dados_api:
        bairro_api = ""
        consulta_ok = False
    else:
        bairro_api = dados_api.get("bairro", "")
        consulta_ok = True

    # Decide qual bairro deve prevalecer
    bairro_final, criterio = decidir_bairro(
        bairro,
        bairro_api,
        consulta_ok
    )

    # Retorna os resultados
    return {
        "id_cliente": cliente["id_cliente"],
        "bairro_original": bairro,
        "bairro_final": bairro_final,
        "criterio": criterio
    }
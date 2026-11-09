from src1.etl import enrich


def test_enriquecimento_prioriza_api(monkeypatch):

    # Simula a resposta do ViaCEP
    def api_simulada(cep):
        return {"bairro": "Asa Sul"}

    # momkeypatch afunciona como um mock da api imitnado apenas logica de retorno do bairro, sem fazer a chamada real ao ViaCEP
    monkeypatch.setattr(
        enrich,
        "buscar_cep",
        api_simulada
    )

    # Cliente fictício
    cliente = {
        "id_cliente": "CLI0001",
        "cep_padronizado": "70000000",
        "bairro_padronizado": "Asa Norte"
    }

    resultado = enrich.enriquecer_cliente(cliente)

    assert resultado["bairro_final"] == "Asa Sul"
    assert resultado["criterio"] == "PRIORIDADE_API"
from src1.etl.regra_prioridade import decidir_bairro


def test_bairros_diferentes():
    assert decidir_bairro("Asa Norte", "Asa Sul") == (
        "Asa Sul", "PRIORIDADE_API"
    )


def test_bairro_original_vazio():
    assert decidir_bairro("", "Asa Sul") == (
        "Asa Sul", "PREENCHIDO_API"
    )


def test_api_sem_bairro():
    assert decidir_bairro("Asa Norte", "") == (
        "Asa Norte", "MANTIDO_ORIGINAL"
    )


def test_bairros_iguais():
    assert decidir_bairro("Asa Norte", "asa norte") == (
        "Asa Norte", "SEM_ALTERACAO"
    )


def test_falha_consulta():
    assert decidir_bairro("Asa Norte", None, False) == (
        "Asa Norte", "FALHA_CONSULTA"
    )

from src1.servico.auditoria_servico import compararDados


def test_criterio_padrao():


    original = {"telefone": "61999999999"}
    tratado = {"telefone": "+5561999999999"}

    alteracoes = compararDados(
        id_cliente="CLI0001",
        original=original,
        tratado=tratado
    )

    assert alteracoes[0]["criterio"] == (
        "Padronização de telefone e DDI"
    )
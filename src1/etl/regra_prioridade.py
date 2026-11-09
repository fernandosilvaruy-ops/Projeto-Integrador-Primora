def decidir_bairro(bairro_original, bairro_api, consulta_ok=True):
    """
    Decide qual bairro prevalece e registra o motivo.
    """

    # Normaliza os valores para evitar erros com None
    original = str(bairro_original or "").strip()
    api = str(bairro_api or "").strip()

    # Regra 1: API indisponível ou consulta inválida
    if not consulta_ok:
        return original, "FALHA_CONSULTA"

    # Regra 2: API não informmou o bairro
    if not api:
        return original, "MANTIDO_ORIGINAL"

    # Regra 3: Ba=irro original vazio
    if not original:
        return api, "PREENCHIDO_API"

    # Regra 4: Bairros iguais
    if original.casefold() == api.casefold():
        return original, "SEM_ALTERACAO"

    # Regra 5: Bairros diferentes
    return api, "PRIORIDADE_API"
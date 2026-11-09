CRITERIOS = {
    "cnpj": "Formatação e padronização do CNPJ",
    "telefone": "Padronização de telefone e DDI",
    "data_cadastro": "Conversão de data para YYYY-MM-DD",
    "bairro": "Padronização de bairro e nomenclatura",
    "cep": "Validação e formatação de CEP"
}

def compararDados(id_cliente, original, tratado, criterios_personalizados=None):
    alteracoes =[]

    # Se nenhum critério personalizado for informado,
    # utiliza um dicionário vazio.
    if criterios_personalizados is None:
        criterios_personalizados = {}

    for campo in original:

        if campo not in tratado:
            continue

        valor_original = original[campo]
        valor_tratado = tratado[campo]

        if valor_original != valor_tratado:

            # Primeiro tenta usar o critério personalizado.
            # Caso não exista, utiliza o critério padrão.
            criterio = criterios_personalizados.get(
                campo,
                CRITERIOS.get(campo, "Não informado")
            )

            alteracoes.append({
                'id_cliente': id_cliente,
                'campo_alterado': campo,
                'valor_original': valor_original,
                'valor_tratado': valor_tratado,
                "criterio": criterio
            })

    return alteracoes

def registrarAlteracoes(alteracoes):
    from cliente.models import AuditoriaAlteracao

    for alteracao in alteracoes:
        AuditoriaAlteracao.objects.create(
            cliente_id=alteracao["id_cliente"],
            campo_alterado=alteracao["campo_alterado"],
            valor_original=alteracao["valor_original"],
            valor_tratado=alteracao["valor_tratado"],
            criterio=alteracao["criterio"]
        )


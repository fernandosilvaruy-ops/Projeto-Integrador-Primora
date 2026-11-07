from src1.servico.auditoria_servico import compararDados 

original = {
    "cep": "71725100",
    "bairro": "v. pires",
    "telefone": "61999998888",
    "uf": "DF"
}

tratado = {
    "cep": "71725-100",
    "bairro": "Vicente Pires",
    "telefone": "(61) 99999-8888",
    "uf": "DF"
}

resultado = compararDados(
    id_cliente=15,
    original=original,
    tratado=tratado
)

for alteracao in resultado:
    print(alteracao)
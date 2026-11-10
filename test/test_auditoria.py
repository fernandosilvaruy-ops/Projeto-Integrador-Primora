import pytest
from cliente.models import ClienteBruto, ClienteTratado, AuditoriaAlteracao

@pytest.mark.django_db
def test_criacao_cliente_bruto():
    cliente = ClienteBruto.objects.create(
        razao_social="Empresa Exemplo Ltda",
        telefone="61999999999"
    )
    assert cliente.pk is not None
    assert cliente.razao_social == "Empresa Exemplo Ltda"

@pytest.mark.django_db
def test_auditoria_alteracao_fluxo():
    tratado = ClienteTratado.objects.create(
        razao_social="Teste Tratado",
        id_cliente="123"
    )
    
    auditoria = AuditoriaAlteracao.objects.create(
        cliente=tratado,
        campo_alterado="razao_social",
        valor_original="Teste Bruto",
        valor_tratado="Teste Tratado"
    )
    
    assert auditoria.pk is not None
    assert auditoria.campo_alterado == "razao_social"
    assert auditoria.valor_original == "Teste Bruto"
    assert auditoria.valor_tratado == "Teste Tratado"
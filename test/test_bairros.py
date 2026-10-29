import pytest

from padronizar_Clientes import padronizar_bairro


@pytest.mark.parametrize('entrada', [
    'Águas Claras',
    'Aguas claras',
    'aguas claras',
    'AGUAS CLARAS',
    'Aguas Claras - DF',
    'Águas Claras/DF',
    'Sul (Águas Claras)',
    'Norte (Aguas Claras)',
    'Águas Claras Norte',
    'Águas Claras Sul',
    '  aguas claras  ',
    'Aguas Claras/DF',
    'águas claras',
])
def test_variacoes_de_aguas_claras(entrada):
    assert padronizar_bairro(entrada) == 'Águas Claras'


@pytest.mark.parametrize('entrada', [
    'Taguatinga', 'TAGUATINGA', 'Taguatinga - DF', 'Taguatinga/DF',
    'taguatinga sul',
    ' Taguatinga ',
    'Taguatinga Norte',
])
def test_variacoes_de_taguatinga(entrada):
    assert padronizar_bairro(entrada) == 'Taguatinga'


@pytest.mark.parametrize('entrada', [
    'Vicente Pires', 'VICENTE PIRES', 'Vicente Pires - DF',
    'V. Pires',
    'Vte Pires',
    'v. pires',
    'VTE PIRES',
])
def test_variacoes_de_vicente_pires(entrada):
    assert padronizar_bairro(entrada) == 'Vicente Pires'


@pytest.mark.parametrize('entrada', [
    'guara - df',
    'Guará I',
    'Guará II',
    'GUARÁ',
    'Guara',
])
def test_variacoes_de_guara(entrada):
    assert padronizar_bairro(entrada) == 'Guará'


def test_bairro_desconhecido_vira_titulo():
    assert padronizar_bairro('asa norte') == 'Asa Norte'
    assert padronizar_bairro('  CEILÂNDIA ') == 'Ceilândia'


def test_bairro_vazio_vira_nao_informado():
    assert padronizar_bairro('') == 'Não informado'


def test_subdivisao_se_perde_na_padronizacao():
    sul = padronizar_bairro('Sul (Águas Claras)')
    norte = padronizar_bairro('Norte (Águas Claras)')
    assert sul == norte == 'Águas Claras'

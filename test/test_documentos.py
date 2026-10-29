import pytest

from padronizar_Clientes import (
    cnpj_valido,
    padronizar_cnpj,
    padronizar_data,
    padronizar_telefone,
)


@pytest.mark.parametrize('entrada, esperado', [
    ('84.959.310/3413-16', '84.959.310/3413-16'),
    ('27868011280598', '27.868.011/2805-98'),
    ('  27868011280598  ', '27.868.011/2805-98'),
    ('27.868.011280598', '27.868.011/2805-98'),
    ('12.abc.345/01de-35', '12.ABC.345/01DE-35'),
    ('27 868 011 2805 98', '27.868.011/2805-98'),
    ('27868011\t280598', '27.868.011/2805-98'),
    ('27868011/2805-98', '27.868.011/2805-98'),
])
def test_padronizar_cnpj_formatos_aceitos(entrada, esperado):
    assert padronizar_cnpj(entrada) == esperado


@pytest.mark.parametrize('entrada', [
    '123',
    '1234567890123',
    '123456789012345',
    'abc',
    '1122233300018A',
    '11.222.333/0001-8X',
    'AB.CDE.FGH/IJKL-MN',
    '11.222.333/0001-8',
])
def test_padronizar_cnpj_invalido_devolve_none(entrada):
    assert padronizar_cnpj(entrada) is None


@pytest.mark.parametrize('entrada', [
    '11.222.333/0001-81',
    '11222333000181',
    ' 11.222.333/0001-81 ',
    '12.ABC.345/01DE-35',
    '12abc34501de35',
])
def test_cnpj_valido_aceita_cnpj_correto(entrada):

    assert cnpj_valido(entrada) is True


@pytest.mark.parametrize('entrada', [
    '11.222.333/0001-82',
    '00000000000000',
    '123',
])
def test_cnpj_valido_rejeita_cnpj_errado(entrada):
    assert cnpj_valido(entrada) is False


@pytest.mark.parametrize('entrada, esperado', [
    ('61970855700', '(61) 97085-5700'),
    ('+55 61 95386-2084', '(61) 95386-2084'),
    ('(61) 98433-1053', '(61) 98433-1053'),
    ('61 3970-2193', '(61) 3970-2193'),
    ('(61) 3491-1634', '(61) 3491-1634'),
    ('556139702193', '(61) 3970-2193'),
    ('+55 61 91035-7396', '(61) 91035-7396'),
    ('61 3356-1423', '(61) 3356-1423'),
    ('(61)98433-1053', '(61) 98433-1053'),
    ('61-98433-1053', '(61) 98433-1053'),
    ('+55 (61) 3970-2193', '(61) 3970-2193'),
    ('5561999038359', '(61) 99903-8359'),
    ('  61999038359  ', '(61) 99903-8359'),
])
def test_padronizar_telefone_formatos_aceitos(entrada, esperado):
    assert padronizar_telefone(entrada) == esperado


@pytest.mark.parametrize('entrada', [
    '123',
    'abc',
    '+55 61 9 5386 2084 99',
    '1234567890123456',
    '3970-219',
    '(61) 3970-219',
    'sem telefone',
])
def test_padronizar_telefone_invalido_devolve_none(entrada):
    assert padronizar_telefone(entrada) is None


@pytest.mark.parametrize('entrada, esperado', [
    ('2022-06-21', '2022-06-21'),
    ('28/02/2022', '2022-02-28'),
    ('08-01-2022', '2022-01-08'),
    ('Dec 24, 2023', '2023-12-24'),
    ('jul 21, 2022', '2022-07-21'),
    ('Apr 3, 2025', '2025-04-03'),
    ('  2022-06-21  ', '2022-06-21'),
    ('29/02/2024', '2024-02-29'),
    ('15-08-2024', '2024-08-15'),
    ('nov 19, 2021', '2021-11-19'),
    ('Feb 28, 2023', '2023-02-28'),
    ('DEC 24, 2023', '2023-12-24'),
    ('04/08/2023', '2023-08-04'),
])
def test_padronizar_data_formatos_aceitos(entrada, esperado):
    assert padronizar_data(entrada) == esperado


def test_data_com_hifen_e_dia_mes_ano():
    assert padronizar_data('08-01-2022') == '2022-01-08'


@pytest.mark.parametrize('entrada', [
    '31/02/2022',
    '29/02/2023',
    '2022-13-45',
    'Xyz 10, 2022',
    'ontem',
    '2022/06/21',
    '2022-02-30',
    '31-04-2022',
    'Feb 30, 2022',
    '08/01/22',
    'January 5, 2022',
    '2022-6-21',
])
def test_padronizar_data_invalida_devolve_none(entrada):
    assert padronizar_data(entrada) is None


def test_padronizar_cnpj_formata_mas_nao_confere_digito_verificador():
    assert padronizar_cnpj('11222333000182') == '11.222.333/0001-82'
    assert cnpj_valido('11222333000182') is False

import pandas as pd
import pytest

from padronizar_Clientes import (
    cnpj_valido,
    padronizar_bairro,
    padronizar_cep,
    padronizar_cnpj,
    padronizar_data,
    padronizar_telefone,
)

VALORES_VAZIOS = [None, '', '   ', float('nan'), pd.NA]


@pytest.mark.parametrize('funcao', [
    padronizar_cnpj,
    padronizar_telefone,
    padronizar_data,
    padronizar_cep,
])
@pytest.mark.parametrize('valor', VALORES_VAZIOS)
def test_funcoes_devolvem_none_para_vazio(funcao, valor):
    assert funcao(valor) is None


@pytest.mark.parametrize('valor', VALORES_VAZIOS)
def test_cnpj_valido_vazio_e_falso(valor):
    assert cnpj_valido(valor) is False


@pytest.mark.parametrize('valor', VALORES_VAZIOS)
def test_bairro_vazio_vira_nao_informado(valor):
    assert padronizar_bairro(valor) == 'Não informado'

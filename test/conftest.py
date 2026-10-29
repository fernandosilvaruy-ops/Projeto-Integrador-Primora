import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NOME_MODULO = 'padronizar_Clientes'
CSV_EXEMPLO = 'clientes_distribuidora_vetor.csv'
PASTAS_IGNORADAS = {'venv', '.venv', 'env', '.git', '__pycache__', 'node_modules', 'tests'}


def _achar_arquivo(nome):
    for pasta, subpastas, arquivos in os.walk(RAIZ):
        subpastas[:] = [s for s in subpastas if s not in PASTAS_IGNORADAS]
        if nome in arquivos:
            return Path(pasta) / nome
    return None


def _carregar_modulo():
    arquivo = _achar_arquivo(f'{NOME_MODULO}.py')
    if arquivo is None:
        raise ImportError(
            f'Não achei {NOME_MODULO}.py dentro de {RAIZ}. '
            'Rode o pytest a partir da pasta do projeto.'
        )

    csv = _achar_arquivo(CSV_EXEMPLO)
    pasta_original = os.getcwd()
    argv_original = sys.argv

    with tempfile.TemporaryDirectory() as pasta_temp:
        if csv is not None:
            shutil.copy(csv, pasta_temp)
        os.chdir(pasta_temp)
        sys.argv = [str(arquivo)]
        try:
            spec = importlib.util.spec_from_file_location(NOME_MODULO, arquivo)
            modulo = importlib.util.module_from_spec(spec)
            sys.modules[NOME_MODULO] = modulo
            with contextlib.redirect_stdout(io.StringIO()):
                spec.loader.exec_module(modulo)
        finally:
            os.chdir(pasta_original)
            sys.argv = argv_original
    return modulo


if NOME_MODULO not in sys.modules:
    _carregar_modulo()

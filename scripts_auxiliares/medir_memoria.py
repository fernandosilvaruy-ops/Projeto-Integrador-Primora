
import sys
import time
import subprocess
from pathlib import Path
import psutil

BASE_DIR = Path(__file__).resolve().parent.parent

tamanho = sys.argv[1]

arquivo_csv = BASE_DIR / "dados_teste" / f"clientes_teste_{tamanho}.csv"
script_etl = BASE_DIR / "src" / "etl" / "padronizar_Clientes.py"

inicio = time.perf_counter()

processo = subprocess.Popen(
    [sys.executable, str(script_etl), str(arquivo_csv)],
    cwd=Path.cwd()
)

processo_ps = psutil.Process(processo.pid)
pico_memoria = 0

while True:
    try:
        processos = [processo_ps] + processo_ps.children(recursive=True)

        memoria_total = sum(
            p.memory_info().rss
            for p in processos
            if p.is_running()
        )

        memoria_mb = memoria_total / (1024 * 1024)
        pico_memoria = max(pico_memoria, memoria_mb)

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    if processo.poll() is not None:
        break

    time.sleep(0.005)

fim = time.perf_counter()

print("\n===== RESULTADO DO TESTE =====")
print(f"Quantidade de clientes: {tamanho}")
print(f"Tempo de execução: {fim - inicio:.3f} segundos")
print(f"Pico de memória RAM: {pico_memoria:.2f} MB")
print(f"Código de saída: {processo.returncode}")

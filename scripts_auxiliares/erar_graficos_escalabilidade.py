
import matplotlib.pyplot as plt
from pathlib import Path

PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_SAIDA = PASTA_PROJETO / "resultados_escalabilidade"
PASTA_SAIDA.mkdir(exist_ok=True)

# Resultados do teste de escalabilidade
registros = [5000, 10000, 25000, 50000]
tempos = [1.165, 1.410, 1.743, 2.347]
memoria = [89.94, 93.55, 103.47, 124.47]

# Calcula o tempo médio por registro em milissegundos
tempo_medio = [
    (tempo / quantidade) * 1000
    for tempo, quantidade in zip(tempos, registros)
]

# Exibe os resultados no terminal
print("\nTempo médio por registro:")
for quantidade, tempo in zip(registros, tempo_medio):
    print(f"{quantidade} registros: {tempo:.5f} ms por registro")

# tempo de processamento- gráfico 1

plt.figure(figsize=(9, 5))
plt.plot(registros, tempos, marker="o")

plt.title("Tempo de Processamento - Teste de Escalabilidade")
plt.xlabel("Quantidade de registros")
plt.ylabel("Tempo (segundos)")

plt.xticks(registros, ["5 mil", "10 mil", "25 mil", "50 mil"])
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PASTA_SAIDA / "grafico_tempo_processamento.png",
    dpi=300
)

# consumo da memoria ram - grádico 2

plt.figure(figsize=(9, 5))
plt.plot(registros, memoria, marker="o")

plt.title("Consumo de Memória RAM - Teste de Escalabilidade")
plt.xlabel("Quantidade de registros")
plt.ylabel("Memória utilizada (MB)")

plt.xticks(registros, ["5 mil", "10 mil", "25 mil", "50 mil"])
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PASTA_SAIDA / "grafico_consumo_memoria.png",
    dpi=300
)

# tempo médio por registro - gráfico 3

plt.figure(figsize=(9, 5))
plt.plot(registros, tempo_medio, marker="o")

plt.title("Tempo Médio de Processamento por Registro")
plt.xlabel("Quantidade de registros")
plt.ylabel("Tempo médio (milissegundos)")

plt.xticks(registros, ["5 mil", "10 mil", "25 mil", "50 mil"])
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PASTA_SAIDA / "grafico_tempo_medio_registro.png",
    dpi=300
)

# Exibe os gráficos na tela
plt.show()

print("\nGráficos gerados com sucesso!")

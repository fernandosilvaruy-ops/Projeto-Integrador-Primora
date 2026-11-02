import os
from sqlalchemy.engine import URL
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Define o caminho da pasta raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

# Carrega o arquivo .env de forma segura
load_dotenv(dotenv_path=ENV_PATH)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Valida??o r?pida para garantir integridade das credenciais
if not all([DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Erro: As vari?veis de ambiente do banco de dados n?o foram totalmente preenchidas no arquivo .env!")

# Monta a URL de conex?o do SQLAlchemy para o PostgreSQL
DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=DB_USER,
    **{"password": DB_PASSWORD},
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

# Cria o engine de conex?o do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Configura a sess?o para transa??es
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def testar_conexao_banco():
    """Fun??o de teste completa: valida conex?o, conta registos e testa inser??o/leitura."""
    try:
        # Usamos engine.begin() para gerir a transa??o automaticamente
        with engine.begin() as conexao:
            # 1. Testa a vers?o do PostgreSQL
            versao = conexao.execute(text("SELECT version();")).fetchone()
            print(f"Conex?o bem-sucedida! PostgreSQL Vers?o: {versao[0]}")

            # 2. Testa a leitura na tabela existente de clientes
            total_clientes = conexao.execute(text("SELECT COUNT(*) FROM cliente_cliente;")).scalar()
            print(f"Total de clientes registados na base de dados: {total_clientes}")

            # 3. Testa inser??o e leitura numa tabela tempor?ria
            conexao.execute(text("""
                CREATE TEMP TABLE IF NOT EXISTS teste_etl_conexao (
                    id SERIAL PRIMARY KEY,
                    mensagem VARCHAR(150)
                );
            """))

            # Insere uma linha de teste
            mensagem_teste = "Teste de escrita e leitura realizado com sucesso!"
            conexao.execute(
                text("INSERT INTO teste_etl_conexao (mensagem) VALUES (:msg);"),
                {"msg": mensagem_teste}
            )

            # L? de volta a linha inserida
            resultado_inserido = conexao.execute(
                text("SELECT mensagem FROM teste_etl_conexao ORDER BY id DESC LIMIT 1;")
            ).fetchone()

            print(f"Linha inserida e lida com sucesso! Mensagem recuperada: '{resultado_inserido[0]}'")

    except Exception as e:
        print(f"Erro ao interagir com o banco de dados: {e}")

if __name__ == "__main__":
    testar_conexao_banco()

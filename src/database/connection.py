import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Define o caminho da pasta raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / '.env'

# Carrega explicitamente o arquivo .env da raiz
load_dotenv(dotenv_path=ENV_PATH)

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

# Validação rápida
if not all([DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Erro: As variáveis de ambiente do banco de dados não foram totalmente preenchidas no arquivo .env!")

# Monta a URL de conexão do SQLAlchemy para o PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Cria o engine de conexão do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Configura a sessão para transações
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def testar_conexao_banco():
    """Função de teste que valida a conexão e lê dados do banco."""
    try:
        with engine.connect() as conexao:
            # Testa uma query simples de versão do PostgreSQL
            resultado = conexao.execute(text("SELECT version();"))
            versao = resultado.fetchone()
            print(f"Conexão bem-sucedida! PostgreSQL Versão: {versao[0]}")
            
            # Testa a leitura na tabela de clientes
            total_clientes = conexao.execute(text("SELECT COUNT(*) FROM cliente_cliente;")).scalar()
            print(f"Total de clientes registados na base de dados: {total_clientes}")
            
    except Exception as e:
        print(f"Erro ao conectar ou consultar o banco de dados: {e}")

if __name__ == "__main__":
    testar_conexao_banco()
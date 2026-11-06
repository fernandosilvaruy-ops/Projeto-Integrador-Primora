import os
from sqlalchemy.engine import URL
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Define o caminho da pasta raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / '.env'

# Carrega o arquivo .env de forma segura
load_dotenv(dotenv_path=ENV_PATH)

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

# Validação rápida para garantir integridade das credenciais
if not all([DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("Erro: As variáveis de ambiente do banco de dados não foram totalmente preenchidas no arquivo .env!")

# Monta a URL de conexão do SQLAlchemy para o PostgreSQL(atualizada;-;)
DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)

# Cria o engine de conexão do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Configura a sessão para transações
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def testar_conexao_banco():
    """Função de teste completa: valida conexão, conta registos e testa inserção/leitura."""
    try:
        # Usamos engine.begin() para gerir a transação automaticamente
        with engine.begin() as conexao:
            # 1. Testa a versão do PostgreSQL
            versao = conexao.execute(text("SELECT version();")).fetchone()
            print(f"Conexão bem-sucedida! PostgreSQL Versão: {versao[0]}")
            
            # 2. Testa a leitura na tabela existente de clientes
            total_clientes = conexao.execute(text("SELECT COUNT(*) FROM cliente_cliente;")).scalar()
            print(f"Total de clientes registados na base de dados: {total_clientes}")
            
            # 3. Testa inserção e leitura numa tabela temporária
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
            
            # Lê de volta a linha inserida
            resultado_inserido = conexao.execute(
                text("SELECT mensagem FROM teste_etl_conexao ORDER BY id DESC LIMIT 1;")
            ).fetchone()
            
            print(f"Linha inserida e lida com sucesso! Mensagem recuperada: '{resultado_inserido[0]}'")
            
    except Exception as e:
        print(f"Erro ao interagir com o banco de dados: {e}")

if __name__ == "__main__":
    testar_conexao_banco()
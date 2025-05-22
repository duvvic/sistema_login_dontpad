from peewee import *
import os

# Caminho absoluto do diretório atual para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'usuarios.db')

# Define a conexão com o banco de dados SQLite
db = SqliteDatabase(db_path)


# Modelo do usuário
class Usuario(Model):
    nome = CharField(unique=True, max_length=50)
    email = CharField(unique=True, null=False)
    senha = CharField(max_length=255)
    codigo_aleatorio = CharField(null=True)

    class Meta:
        database = db
        table_name = 'usuario'


# Função para conectar e criar as tabelas (caso não existam)
def inicializar_db():
    try:
        if db.is_closed():
            db.connect()
        db.create_tables([Usuario], safe=True)
        print("[✓] Banco de dados conectado e tabelas verificadas/criadas.")
    except OperationalError as e:
        print(f"[ERRO CRÍTICO] Falha ao conectar/criar tabelas no banco de dados: {e}")
    except Exception as e:
        print(f"[ERRO INESPERADO] no banco de dados: {e}")
import sqlite3
from config import DB_PATH

def _column_exists(conn, table, column):
    cur = conn.execute(f'PRAGMA table_info({table})')
    return any(row[1] == column for row in cur.fetchall())

def init_db_all():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---------------- TABELAS ----------------
    cur.execute('''
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT, rg TEXT, sexo TEXT,
        nascimento TEXT, telefone TEXT, email TEXT,
        endereco TEXT, alergias TEXT,
        anamnese TEXT,              -- observações livres
        anamnese_json TEXT,         -- NOVO: anamnese estruturada (JSON)
        observacoes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS modelos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        html TEXT NOT NULL,
        meta TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS documentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER NOT NULL,
        modelo_id INTEGER,
        parametros TEXT,
        caminho_pdf TEXT NOT NULL,
        data_criacao TEXT NOT NULL,
        FOREIGN KEY(paciente_id) REFERENCES pacientes(id),
        FOREIGN KEY(modelo_id) REFERENCES modelos(id)
    )''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS lookups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,             -- cid, medicamento, procedimento
        codigo TEXT,
        descricao TEXT
    )''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS clinica (
        id INTEGER PRIMARY KEY CHECK (id=1),
        nome TEXT,
        cnpj TEXT,
        epao TEXT,
        responsavel_tecnico TEXT,
        cro TEXT,
        telefone TEXT,
        email TEXT,
        endereco TEXT,
        cidade TEXT,
        uf TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    cur.execute("INSERT OR IGNORE INTO clinica (id, nome) VALUES (1, 'Minha Clínica Odontológica')")

    # ---------------- MIGRAÇÕES ----------------
    # pacientes.anamnese_json
    if not _column_exists(conn, 'pacientes', 'anamnese_json'):
        try:
            cur.execute("ALTER TABLE pacientes ADD COLUMN anamnese_json TEXT")
        except Exception:
            pass

    # lookups colunas (para bases antigas)
    def ensure_lookup_col(col):
        if not _column_exists(conn, 'lookups', col):
            try: cur.execute(f"ALTER TABLE lookups ADD COLUMN {col} TEXT")
            except Exception: pass
    ensure_lookup_col('tipo'); ensure_lookup_col('codigo'); ensure_lookup_col('descricao')

    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_lookups_tipo ON lookups(tipo)")
    except Exception:
        pass

    conn.commit()
    conn.close()

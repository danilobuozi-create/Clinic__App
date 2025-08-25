import json
import sqlite3
from pathlib import Path

# Caminhos do projeto
try:
    from config import DB_PATH, ASSETS_DIR
except Exception:
    BASE = Path(__file__).resolve().parent
    DB_PATH = str(Path.home() / ".clinic_app" / "clinic.db")
    ASSETS_DIR = BASE / "assets"

def read_text(p: Path) -> str:
    if not p.exists():
        raise FileNotFoundError(f"Template não encontrado: {p}")
    return p.read_text(encoding="utf-8")

def ensure_table(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS modelos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        html TEXT NOT NULL,
        meta TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

def get_model(conn: sqlite3.Connection, name: str):
    cur = conn.execute("SELECT * FROM modelos WHERE nome=?", (name,))
    row = cur.fetchone()
    return dict(row) if row else None

def rename_if_exists(conn: sqlite3.Connection, old: str, new: str):
    row_old = get_model(conn, old)
    row_new = get_model(conn, new)
    if row_old and not row_new:
        conn.execute("UPDATE modelos SET nome=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (new, row_old["id"]))
        print(f"[RENAME] {old} -> {new}")
    elif row_old and row_new:
        print(f"[SKIP] já existe '{new}', mantendo ambos")

def upsert_model(conn: sqlite3.Connection, name: str, html: str, meta: dict,
                 force_update_html: bool = True, force_update_meta: bool = True):
    meta_json = json.dumps(meta, ensure_ascii=False)
    row = get_model(conn, name)
    if row is None:
        conn.execute("INSERT INTO modelos (nome, html, meta) VALUES (?, ?, ?)", (name, html, meta_json))
        print(f"[ADD] {name}")
    else:
        set_parts, vals = [], []
        if force_update_html:
            set_parts.append("html=?"); vals.append(html)
        if force_update_meta:
            set_parts.append("meta=?"); vals.append(meta_json)
        if set_parts:
            set_parts.append("updated_at=CURRENT_TIMESTAMP")
            vals.append(row["id"])
            conn.execute(f"UPDATE modelos SET {', '.join(set_parts)} WHERE id=?", vals)
            print(f"[UPDATE] {name}")
        else:
            print(f"[KEEP] {name}")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_table(conn)

    contrato_crosp = ASSETS_DIR / "templates" / "contrato_crosp.html"
    prontuario = ASSETS_DIR / "templates" / "prontuario.html"
    receita = ASSETS_DIR / "templates" / "receita.html"
    orcamento = ASSETS_DIR / "templates" / "orcamento.html"

    # 0) Renomear antigo
    rename_if_exists(conn, "Contrato (padrão)", "Contrato (LEGADO)")

    # 1) Contrato (CROSP)
    contrato_crosp_meta = {
        "fields": [
            {"name": "area_tratamento", "label": "Área de tratamento", "type": "text"},
            {"name": "duracao_prevista", "label": "Duração prevista", "type": "text"},
            {"name": "procedimentos", "label": "Procedimentos (selecione do catálogo)", "type": "lookup_multi", "lookup_type": "procedimento"},
            {"name": "valor_total", "label": "Valor total (R$)", "type": "text"},
            {"name": "forma_pagamento", "label": "Forma de pagamento", "type": "choice", "options": ["PIX", "Crédito", "Débito", "Dinheiro", "Boleto"]},
            {"name": "forma_pagamento_obs", "label": "Detalhes da forma de pagamento", "type": "longtext"},
            {"name": "foro", "label": "Foro", "type": "text"}
        ]
    }
    upsert_model(conn, "Contrato (CROSP)", read_text(contrato_crosp), contrato_crosp_meta,
                 force_update_html=True, force_update_meta=True)

    # 2) Prontuário – atualiza HTML (puxa anamnese estruturada)
    prontuario_meta = {
        "fields": [
            {"name": "data", "label": "Data (sobrescreve hoje, opcional)", "type": "date"},
            {"name": "observacoes", "label": "Observações adicionais", "type": "longtext"}
        ]
    }
    upsert_model(conn, "Prontuário/Registro Clínico (padrão)", read_text(prontuario), prontuario_meta,
                 force_update_html=True, force_update_meta=False)

    # 3) Receituário (simples) – força META para usar catálogo
    receita_meta = {
        "fields": [
            {"name": "medicamento", "label": "Medicamento", "type": "lookup", "lookup_type": "medicamento"},
            {"name": "posologia", "label": "Posologia", "type": "text"},
            {"name": "quantidade", "label": "Quantidade", "type": "int"},
            {"name": "observacoes", "label": "Observações", "type": "longtext"}
        ]
    }
    upsert_model(conn, "Receituário (simples)", read_text(receita), receita_meta,
                 force_update_html=True, force_update_meta=True)

    # 4) Orçamento (padrão) – atualiza HTML (Anexo II)
    orc_meta = {"fields": [{"name": "observacoes", "label": "Observações", "type": "longtext"}]}
    upsert_model(conn, "Orçamento (padrão)", read_text(orcamento), orc_meta,
                 force_update_html=True, force_update_meta=False)

    # 5) Orçamento (Assistente) – novo com lookup_items + forma de pagamento
    orc_ass_meta = {
        "fields": [
            {"name": "opcao_tratamento", "label": "Opção de tratamento", "type": "text"},
            {"name": "procedimentos_itens", "label": "Procedimentos (selecione + informe valor)", "type": "lookup_items", "lookup_type": "procedimento", "total_field": "total"},
            {"name": "forma_pagamento", "label": "Forma de pagamento", "type": "choice", "options": ["PIX", "Crédito", "Débito", "Dinheiro", "Boleto"]},
            {"name": "forma_pagamento_obs", "label": "Detalhes da forma de pagamento", "type": "longtext"}
        ]
    }
    upsert_model(conn, "Orçamento (Assistente)", read_text(orcamento), orc_ass_meta,
                 force_update_html=True, force_update_meta=True)

    conn.commit()
    conn.close()
    print("OK: templates atualizados.")

if __name__ == "__main__":
    main()

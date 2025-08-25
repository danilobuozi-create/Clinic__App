import sys, json
from PySide6.QtWidgets import QApplication
from init_db import init_db_all
from ui.main_window import MainWindow
from models.repositories import ModeloRepo
from config import ASSETS_DIR

def seed_templates_if_empty():
    repo = ModeloRepo()
    if not repo.listar_todos():
        # Atestado
        with open(ASSETS_DIR / 'templates' / 'atestado.html', 'r', encoding='utf-8') as f:
            atestado_html = f.read()
        atestado_meta = json.dumps({
            "fields": [
                {"name": "cid", "label": "CID", "type": "lookup", "lookup_type": "cid"},
                {"name": "repouso_dias", "label": "Repouso (dias)", "type": "int"},
                {"name": "data", "label": "Data do atendimento", "type": "date"}
            ]
        }, ensure_ascii=False)
        repo.add("Atestado Odontológico (padrão)", atestado_html, atestado_meta)

        # Receituário
        with open(ASSETS_DIR / 'templates' / 'receita.html', 'r', encoding='utf-8') as f:
            receita_html = f.read()
        receita_meta = json.dumps({
            "fields": [
                {"name": "medicamento", "label": "Medicamento", "type": "lookup", "lookup_type": "medicamento"},
                {"name": "posologia", "label": "Posologia", "type": "text"},
                {"name": "quantidade", "label": "Quantidade", "type": "int"},
                {"name": "observacoes", "label": "Observações", "type": "longtext"}
            ]
        }, ensure_ascii=False)
        repo.add("Receituário (simples)", receita_html, receita_meta)

        # Contrato (padrão antigo)
        with open(ASSETS_DIR / 'templates' / 'contrato.html', 'r', encoding='utf-8') as f:
            contrato_html = f.read()
        contrato_meta = json.dumps({
            "fields": [
                {"name": "procedimentos", "label": "Procedimentos (separados por vírgula)", "type": "text"},
                {"name": "pagamento", "label": "Condições de pagamento", "type": "text"}
            ]
        }, ensure_ascii=False)
        repo.add("Contrato (padrão)", contrato_html, contrato_meta)

        # Contrato CROSP (NOVO)
        with open(ASSETS_DIR / 'templates' / 'contrato_crosp.html', 'r', encoding='utf-8') as f:
            contrato_crosp_html = f.read()
        contrato_crosp_meta = json.dumps({
            "fields": [
                {"name": "area_tratamento", "label": "Área de tratamento", "type": "text"},
                {"name": "duracao_prevista", "label": "Duração prevista", "type": "text"},
                {"name": "procedimentos", "label": "Procedimentos (selecione do catálogo)", "type": "lookup_multi", "lookup_type": "procedimento"},
                {"name": "valor_total", "label": "Valor total (R$)", "type": "text"},
                {"name": "forma_pagamento", "label": "Forma de pagamento", "type": "choice", "options": ["PIX", "Crédito", "Débito", "Dinheiro", "Boleto"]},
                {"name": "forma_pagamento_obs", "label": "Detalhes da forma de pagamento", "type": "longtext"},
                {"name": "foro", "label": "Foro", "type": "text"}
            ]
        }, ensure_ascii=False)
        repo.add("Contrato (CROSP)", contrato_crosp_html, contrato_crosp_meta)

        # Termo de Consentimento
        with open(ASSETS_DIR / 'templates' / 'consentimento.html', 'r', encoding='utf-8') as f:
            consent_html = f.read()
        consent_meta = json.dumps({
            "fields": [
                {"name": "procedimento", "label": "Procedimento", "type": "lookup", "lookup_type": "procedimento"},
                {"name": "riscos", "label": "Riscos informados", "type": "longtext"},
                {"name": "beneficios", "label": "Benefícios esperados", "type": "longtext"},
                {"name": "responsavel", "label": "Responsável pelo esclarecimento", "type": "text"},
                {"name": "data", "label": "Data", "type": "date"}
            ]
        }, ensure_ascii=False)
        repo.add("Termo de Consentimento (padrão)", consent_html, consent_meta)

        # Prontuário / Registro
        with open(ASSETS_DIR / 'templates' / 'prontuario.html', 'r', encoding='utf-8') as f:
            pront_html = f.read()
        pront_meta = json.dumps({
            "fields": [
                {"name": "data", "label": "Data (sobrescreve hoje, opcional)", "type": "date"},
                {"name": "observacoes", "label": "Observações adicionais", "type": "longtext"}
            ]
        }, ensure_ascii=False)
        repo.add("Prontuário/Registro Clínico (padrão)", pront_html, pront_meta)

        # Orçamento/Plano (Anexo II) – gerado pela aba Orçamento
        with open(ASSETS_DIR / 'templates' / 'orcamento.html', 'r', encoding='utf-8') as f:
            orc_html = f.read()
        orc_meta = json.dumps({
            "fields": [
                {"name": "observacoes", "label": "Observações", "type": "longtext"}
            ]
        }, ensure_ascii=False)
        repo.add("Orçamento (padrão)", orc_html, orc_meta)

def main():
    init_db_all()
    seed_templates_if_empty()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

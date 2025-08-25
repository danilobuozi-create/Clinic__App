# ClinicApp (Offline, PySide6 + SQLite)
100% offline. Gera PDFs com WeasyPrint usando templates HTML (Jinja2).

## Como rodar
pip install -r requirements.txt
python main.py

## Dicas
- Preencha **Configurações da Clínica**.
- Cadastre **Catálogos** (CID/Medicamentos/Procedimentos).
- Cadastre **Pacientes**.
- Gere documentos pelas abas (Prescrição, Atestado, Orçamento) ou pelo **Assistente** na aba Pacientes.
- PDFs ficam em `~/.clinic_app/documents/`.

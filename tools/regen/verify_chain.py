#!/usr/bin/env python3
"""Verifica no banco do app (clinia_ops) que a cadeia clínica do último smoke persistiu
ligada: atendimento -> pre_diagnostico -> encaminhamento -> prontuario (com FKs corretas).
Lê APP_DIR/e2e-carry.json (gravado pelo smoke_e2e.js). Sai 0 se OK, 1 se falhou."""
import os, sys, json
import mysql.connector

APP = os.environ.get("APP_DIR", "/home/pasteurjr/clinia-app5")
carry = json.load(open(os.path.join(APP, "e2e-carry.json")))["cf"]
AT = carry.get("atendimento_id")
if not AT:
    print("[verify] sem atendimento_id no carry — smoke não completou a triagem"); sys.exit(1)

db = dict(host=os.environ.get("APP_DB_HOST", "camerascasas.no-ip.info"),
          port=int(os.environ.get("APP_DB_PORT", "3308")),
          user=os.environ.get("APP_DB_USER", "producao"),
          password=os.environ.get("APP_DB_PASSWORD", "112358123"),
          database=os.environ.get("APP_DB_NAME", "clinia_ops"))
c = mysql.connector.connect(**db); cur = c.cursor(dictionary=True)
def one(q, *a): cur.execute(q, a); return cur.fetchone()

at = one("SELECT a.id, p.nome FROM atendimentos a JOIN pacientes p ON p.id=a.paciente_id WHERE a.id=%s", AT)
enc = one("SELECT id, medico_id, especialidade_id FROM encaminhamentos WHERE atendimento_id=%s ORDER BY created_at DESC LIMIT 1", AT)
pron = one("SELECT id, pre_diagnostico_id, encaminhamento_id FROM prontuarios WHERE atendimento_id=%s ORDER BY created_at DESC LIMIT 1", AT)
cur.close(); c.close()

ok_at = bool(at)
ok_enc = bool(enc and enc.get("medico_id") and enc.get("especialidade_id"))
ok_pron = bool(pron and pron.get("pre_diagnostico_id") and pron.get("encaminhamento_id")
               and pron["encaminhamento_id"] == (enc or {}).get("id"))
print(f"[verify] atendimento={ok_at} ({(at or {}).get('nome')}) | encaminhamento(medico+esp)={ok_enc} | prontuario(liga pre_diag+enc)={ok_pron}")
sys.exit(0 if (ok_at and ok_enc and ok_pron) else 1)

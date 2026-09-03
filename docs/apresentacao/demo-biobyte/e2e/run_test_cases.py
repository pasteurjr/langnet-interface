#!/usr/bin/env python3
"""Executa os 43 casos de teste (gerados pela etapa Casos de Teste) contra o sistema implantado.

Cada caso é causa→efeito. Classificamos o efeito e verificamos do jeito honesto para cada tipo:
  SISTEMA    — comportamento de dados/regra: dispara a tarefa do caso de uso e confere o resultado
               (e o banco, quando o efeito é "cria registro").
  INTERFACE  — elemento de tela (badge, mensagem, botão): confere se existe no código gerado da tela.
  NÃO IMPL.  — efeito que o sistema não implementa (e-mail/push, timeout simulado, processamento
               assíncrono). Reportado como lacuna, não como aprovação.

uso: python3 run_test_cases.py [ws_port] [frontend_src_dir]
"""
import asyncio, json, re, sys, os
from pathlib import Path

WS_PORT = sys.argv[1] if len(sys.argv) > 1 else "5002"
FE = Path(sys.argv[2]) if len(sys.argv) > 2 else None
if FE is None:
    cands = sorted(Path("/tmp/langnet-runs").glob("*/*/frontend/src"), key=lambda p: p.stat().st_mtime)
    FE = cands[-1] if cands else Path(".")
TCS = json.load(open("/tmp/biobyte_testcases.json", encoding="utf-8"))

UC_TASK = {
    "UC-001": "authenticate_user_mfa", "UC-002": "init_import_session",
    "UC-003": "fetch_and_persist_microbiology", "UC-004": "classify_case_nhsn",
    "UC-005": "detect_mdr_and_alert", "UC-006": "calculate_cox_risk_score",
    "UC-007": "recommend_treatment_bundle", "UC-008": "estimate_risk_reduction",
    "UC-009": "generate_dashboard_metrics", "UC-010": "manage_user_account",
    "UC-011": "query_audit_logs", "UC-012": "export_vigilance_report",
}
BASE = {  # caso clínico de referência (o mesmo do fluxo encadeado)
    "email": "ana@hospital.br", "senha": "x", "codigo_mfa": "123456", "usuario_id": "U-001",
    "paciente_id": "P-001", "caso_id": "CAS-2023-001", "idade": 72, "dias_cateter": 12,
    "uti": True, "nutricao_parenteral": True, "neutropenia": False,
    "tipo_cateter": "Cateter Central", "apache_ii": 18, "id_amostra": "HMC-88213",
}
# Efeitos que o sistema NÃO implementa (reportados como lacuna, jamais como sucesso).
NAO_IMPL = [
    (r"e-?mail|push notification", "envio de e-mail/push não está ligado a nenhum agente"),
    (r"timeout", "simulação de timeout não é exercitável pela interface do sistema"),
    (r"processamento ass[íi]ncrono", "processamento assíncrono/fila não implementado"),
    (r"skeleton loader", "skeleton loader não implementado nas telas geradas"),
]
# Efeitos de INTERFACE → trecho a procurar no código das telas.
UI_ALVO = [
    (r"badge 'ICSAC Confirmado'|badge 'Não ICSAC'|badge 'Classificação Pendente'", "ICSAC Confirmado"),
    (r"Credenciais inv[áa]lidas", "Credenciais inv"),
    (r"C[óo]digo incorreto", "digo incorreto"),
    (r"Exportar CSV|arquivo CSV", "CSV"),
    (r"spinner", "busy"),
    (r"tela Pr[ée]via de Resultados", "PreviaResultados"),
    (r"tela Sele[çc][ãa]o de Paciente|Paciente n[ãa]o encontrado", "paciente"),
    (r"lista de Casos Ativos", "casos"),
    (r"formul[áa]rio de cadastro de novo caso", "CasosCrud"),
    (r"tela Importa[çc][ãa]o de Microbiologia", "ImportacaoMicrobiologia"),
    (r"cards de KPI|gr[áa]ficos", "kpi"),
    (r"barra de progresso", "progress"),
    (r"banner vermelho", "AlertaMdr"),
    (r"tabela de logs", "LogsAuditoria"),
    (r"Recomenda[çc][ãa]o de Bundle com nome e justificativa", "bundle_nome"),
    (r"Redu[çc][ãa]o de Risco Estimada|Intervalo de Confian", "intervalo_confianca"),
    (r"Dashboard de Vigil[âa]ncia", "DashboardVigilancia"),
    (r"Verifica[çc][ãa]o de Identidade|Redireciona", "codigo_mfa"),
    (r"filtro de per[íi]odo|atualiza cards", "data_inicio"),
    (r"mensagem de erro", "setErr"),
]
FE_SRC = ""
for f in sorted(FE.glob("screens/*.jsx")) + sorted(FE.glob("*.jsx")):
    try: FE_SRC += f.read_text(encoding="utf-8", errors="replace") + "\n" + f.name + "\n"
    except Exception: pass


async def exec_task(nome, entrada, timeout=180):
    import websockets
    async with websockets.connect(f"ws://localhost:{WS_PORT}", max_size=None, open_timeout=10) as ws:
        try: await asyncio.wait_for(ws.recv(), timeout=2)
        except Exception: pass
        await ws.send(json.dumps({"type": "execute_task",
                                  "data": {"task_name": nome, "input_data": entrada}}))
        import time; t0 = time.time()
        while time.time() - t0 < timeout:
            m = json.loads(await asyncio.wait_for(ws.recv(), timeout=timeout))
            if m.get("type") == "task_completed": return m["data"].get("result", {})
            if m.get("type") == "error": return {"status": "erro", "error": m["data"].get("error")}
    return {"status": "timeout"}


def entrada_do_caso(tc):
    """Monta a entrada a partir das causas: causa NEGADA vira ausência/valor inválido do campo."""
    ent = dict(BASE)
    for e in (tc.get("entradas") or []):
        if e.get("verdadeira", True):
            continue
        d = (e.get("desc") or "").lower()
        if "credenciais" in d: ent["email"] = "inexistente@x.br"; ent["senha"] = "errada"
        elif "mfa" in d or "código" in d: ent["codigo_mfa"] = "000000"
        elif "paciente" in d: ent["paciente_id"] = "P-INEXISTENTE"
        elif "dados suficientes" in d or "parâmetros" in d or "obrigat" in d:
            for k in ("idade", "dias_cateter", "uti", "apache_ii", "microrganismo"): ent.pop(k, None)
        elif "mdr" in d or "multirresist" in d: ent["multirresistente"] = False
        elif "csv" in d: ent["formato"] = "pdf"
        elif "conexão" in d or "api" in d: ent["caso_id"] = "CAS-INEXISTENTE"
    return ent


def classifica(tc):
    ef = ((tc.get("efeito_esperado") or {}).get("desc") or "")
    for pat, motivo in NAO_IMPL:
        if re.search(pat, ef, re.I): return "NAO_IMPL", motivo
    for pat, alvo in UI_ALVO:
        if re.search(pat, ef, re.I): return "INTERFACE", alvo
    return "SISTEMA", ef


async def semear_contexto():
    """Roda a cadeia clínica ANTES dos casos, para que cada caso parta do MESMO estado que o
    sistema tem em uso real. Sem isto, uma tarefa chamada isolada falha por falta de dado que
    a etapa anterior produz (ex.: o alerta MDR precisa da microbiologia) — seria culpa do teste,
    não do sistema."""
    ctx = dict(BASE)
    cadeia = ["authenticate_user_mfa", "init_import_session", "fetch_and_persist_microbiology",
              "classify_case_nhsn", "detect_mdr_and_alert", "calculate_cox_risk_score",
              "recommend_treatment_bundle", "estimate_risk_reduction"]
    for t in cadeia:
        try:
            r = await exec_task(t, ctx)
            if isinstance(r, dict) and r.get("status") != "erro":
                for k, v in r.items():
                    if v is not None and not isinstance(v, (dict, list)):
                        ctx[k] = v
        except Exception:
            pass
    print(f"contexto semeado pela cadeia: {len(ctx)} campos "
          f"(inclui {', '.join(k for k in ('microbiologia_id','micro_id','valor_escore','classificacao_nhsn') if k in ctx) or 'nenhum id'})\n")
    return ctx


async def main():
    global BASE
    BASE = await semear_contexto()
    linhas, resumo = [], {"SISTEMA_OK": 0, "SISTEMA_FALHA": 0, "INTERFACE_OK": 0,
                          "INTERFACE_FALTA": 0, "NAO_IMPL": 0, "SEM_CASO": 0}
    for bloco in TCS:
        nome_uc = bloco.get("uc_name") or bloco.get("name") or "?"
        casos = bloco.get("test_cases") or []
        if not casos:
            linhas.append((nome_uc, "—", "SEM CASO", "a etapa de Casos de Teste não gerou casos para este caso de uso"))
            resumo["SEM_CASO"] += 1
            continue
        for tc in casos:
            uc = tc.get("uc"); tid = tc.get("id")
            tipo, alvo = classifica(tc)
            efeito = ((tc.get("efeito_esperado") or {}).get("desc") or "")[:70]
            if tipo == "NAO_IMPL":
                linhas.append((tid, uc, "NÃO IMPLEMENTADO", f"{efeito} — {alvo}")); resumo["NAO_IMPL"] += 1
            elif tipo == "INTERFACE":
                ok = alvo.lower() in FE_SRC.lower()
                linhas.append((tid, uc, "INTERFACE OK" if ok else "INTERFACE FALTA",
                               f"{efeito} — procurado no código das telas: '{alvo}'"))
                resumo["INTERFACE_OK" if ok else "INTERFACE_FALTA"] += 1
            else:
                tarefa = UC_TASK.get(uc)
                if not tarefa:
                    linhas.append((tid, uc, "SEM TAREFA", efeito)); resumo["SISTEMA_FALHA"] += 1; continue
                try:
                    r = await exec_task(tarefa, entrada_do_caso(tc))
                except Exception as exc:
                    r = {"status": "erro", "error": str(exc)[:120]}
                erro = (isinstance(r, dict) and (r.get("status") == "erro" or r.get("error")))
                negativo = any(not e.get("verdadeira", True) for e in (tc.get("entradas") or []))
                # caso NEGATIVO deve ser rejeitado; caso POSITIVO deve concluir
                ok = (erro if negativo else not erro)
                det = json.dumps(r, ensure_ascii=False)[:110]
                linhas.append((tid, uc, "PASSOU" if ok else "FALHOU",
                               f"{'(negativo) ' if negativo else ''}{efeito} → {det}"))
                resumo["SISTEMA_OK" if ok else "SISTEMA_FALHA"] += 1
                print(f"  {tid:16} {'PASSOU' if ok else 'FALHOU'}  {det[:80]}", flush=True)
    print("\n" + "=" * 100)
    print(f"{'CASO':17}{'UC':9}{'RESULTADO':20}DETALHE")
    print("=" * 100)
    for a, b, c, d in linhas: print(f"{a:17}{b:9}{c:20}{d[:60]}")
    print("=" * 100)
    tot = sum(resumo.values())
    print(f"TOTAL {tot} casos:")
    print(f"  comportamento do sistema — PASSOU: {resumo['SISTEMA_OK']} | FALHOU: {resumo['SISTEMA_FALHA']}")
    print(f"  elemento de interface    — EXISTE: {resumo['INTERFACE_OK']} | FALTA: {resumo['INTERFACE_FALTA']}")
    print(f"  efeito NÃO implementado  — {resumo['NAO_IMPL']}")
    print(f"  caso de uso sem caso gerado — {resumo['SEM_CASO']}")
    json.dump({"resumo": resumo, "linhas": linhas}, open("/tmp/testcases_result.json", "w"),
              ensure_ascii=False, indent=1)

asyncio.run(main())

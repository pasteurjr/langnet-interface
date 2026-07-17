#!/usr/bin/env python3
"""Gera o Documento de Validação por Caso de Uso (PDF) da app Quântica.
Formato padrão: por UC → objetivo, ator, pré-condição, tabela de casos de teste
(1 por passo do fluxo), esperado vs obtido, evidência (screenshot), status.
Também consolida a execução real das tasks via WebSocket.
Serve de TEMPLATE pra inserir validação por UC no pipeline LangNet.
"""
import json, os, base64, time
from weasyprint import HTML

BASE = "/tmp/uso-solo-pipeline"
SHOTS = f"{BASE}/uc-shots"
results = json.load(open(f"{BASE}/uc-results.json"))
try:
    ws = json.load(open(f"{BASE}/ws-exec-results.json"))
except Exception:
    ws = {}

def img_b64(path, w="100%"):
    if not path or not os.path.exists(path):
        return "<span style='color:#999'>[sem screenshot]</span>"
    b = base64.b64encode(open(path, "rb").read()).decode()
    return f'<img style="width:{w};border:1px solid #ccc;border-radius:4px" src="data:image/png;base64,{b}"/>'

STCOLOR = {"PASS": "#137333", "PARCIAL": "#a56300", "FAIL": "#b3261e", "VISUAL": "#1a56db", "N/EXEC": "#666", "N/A": "#888"}
def badge(st):
    return f'<span style="background:{STCOLOR.get(st,"#666")};color:#fff;padding:1px 8px;border-radius:10px;font-size:9pt">{st}</span>'

# sumário
n = len(results)
from collections import Counter
cnt = Counter(r["status"] for r in results)
tot_steps = sum(len(r["steps"]) for r in results)
executed = [r for r in results if r["evidence"].get("executed")]

ws_rows = ""
for task, r in ws.items():
    oc = r.get("outcome")
    color = "#137333" if oc == "completed" else ("#b3261e" if oc in ("error","exception") else "#a56300")
    res = r.get("result")
    res_s = (json.dumps(res, ensure_ascii=False)[:90] if res is not None else r.get("error","")) or ""
    ws_rows += f'<tr><td><code>{task}</code></td><td style="color:{color}">{oc}</td><td>{r.get("secs")}s</td><td style="font-size:8pt">{res_s}</td></tr>'

uc_sections = ""
for r in results:
    uc = r["id"]
    ev = r["evidence"]
    delta = ev.get("db_delta") or {}
    delta_s = ", ".join(f"{k}: +{v}" for k, v in delta.items() if v) if any(delta.values()) else "—"
    wsr = ws.get(r["target"]) if r.get("target") else None
    ws_line = ""
    if wsr:
        oc = wsr.get("outcome")
        ws_line = f'<p><b>Execução da task (WebSocket):</b> <code>{r["target"]}</code> → <b>{oc}</b> em {wsr.get("secs")}s.'
        if wsr.get("result"):
            ws_line += f' Resultado: <code style="font-size:8pt">{json.dumps(wsr["result"],ensure_ascii=False)[:120]}</code>'
        if wsr.get("error"):
            ws_line += f' Erro: {wsr["error"][:120]}'
        ws_line += "</p>"

    rows = ""
    for i, s in enumerate(r["steps"], 1):
        rows += (f'<tr><td>TC-{uc}-{i:02d}</td><td>{s["acao"]}</td>'
                 f'<td>{s["esperado"]}</td><td>{s["nota"]}</td><td>{badge(s["status"])}</td></tr>')
    if not rows:
        rows = '<tr><td colspan="5" style="color:#888">Sem passos de fluxo principal na spec.</td></tr>'

    result_shot = f"{SHOTS}/{uc}-result.png"
    shot_html = img_b64(r.get("shot"), "72%")
    if os.path.exists(result_shot):
        shot_html += "<br/><div style='font-size:8pt;color:#666;margin-top:6px'>Resultado após ação:</div>" + img_b64(result_shot, "72%")

    uc_sections += f"""
    <div class="uc">
      <h2>{uc} — {r['name']} {badge(r['status'])}</h2>
      <table class="meta">
        <tr><th>Ator</th><td>{r['actor']}</td><th>Tela</th><td>{r['screen']} ({r['layout']})</td></tr>
        <tr><th>Objetivo</th><td colspan="3">{r['objetivo']}</td></tr>
        <tr><th>Task vinculada</th><td>{r.get('target') or '—'}</td><th>Persistência no banco</th><td>{delta_s}</td></tr>
      </table>
      {ws_line}
      <h4>Casos de teste (um por passo do fluxo)</h4>
      <table class="tc">
        <tr><th>ID</th><th>Ação (passo do UC)</th><th>Resposta esperada (spec)</th><th>Obtido / evidência</th><th>Status</th></tr>
        {rows}
      </table>
      <h4>Evidência visual</h4>
      {shot_html}
    </div>
    """

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
  @page {{ size: A4; margin: 1.4cm; }}
  body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; color:#222; font-size:10.5pt; line-height:1.45; }}
  h1 {{ color:#1a56db; border-bottom:3px solid #1a56db; padding-bottom:6px; }}
  h2 {{ color:#123; margin-top:4px; font-size:14pt; }}
  h4 {{ color:#1a56db; margin:12px 0 4px; font-size:10.5pt; }}
  .uc {{ page-break-before: always; border-top:2px solid #e5e7eb; padding-top:8px; }}
  table {{ border-collapse:collapse; width:100%; margin:6px 0; }}
  th,td {{ border:1px solid #d0d0d0; padding:4px 7px; text-align:left; vertical-align:top; font-size:9pt; }}
  th {{ background:#eef2f8; }}
  table.meta th {{ width:110px; }}
  table.tc th {{ background:#f3f4f6; }}
  code {{ background:#f4f4f4; padding:1px 4px; border-radius:3px; }}
  .box {{ background:#f5f9fc; border:1px solid #dbe7f0; border-radius:6px; padding:12px 16px; margin:10px 0; }}
  .kpi {{ display:inline-block; background:#fff; border:1px solid #ddd; border-radius:8px; padding:8px 14px; margin:4px 6px 4px 0; }}
  .kpi b {{ font-size:16pt; color:#1a56db; display:block; }}
</style></head><body>

<h1>Documento de Validação por Caso de Uso</h1>
<p><b>Sistema:</b> Quântica Comercial — aplicação gerada pelo pipeline LangNet ·
<b>Data:</b> {time.strftime('%d/%m/%Y')} · <b>Método:</b> execução da app real (frontend React
+ ws-server + banco) com Playwright + verificação no MySQL.</p>

<div class="box">
  <b>Como ler este documento.</b> Cada Caso de Uso da especificação é validado convertendo
  <b>cada passo do seu fluxo principal em um caso de teste</b> (TC-UC-XXX-NN). Para cada caso de
  teste registra-se a resposta esperada (da spec) e o obtido na app, com evidência (screenshot
  e/ou delta no banco), e um status. As tarefas foram ainda disparadas diretamente no servidor
  de execução (WebSocket) para comprovar a resposta ponta a ponta.
</div>

<h4>Sumário</h4>
<div>
  <span class="kpi"><b>{n}</b>Casos de uso</span>
  <span class="kpi"><b>{tot_steps}</b>Casos de teste</span>
  <span class="kpi"><b>{cnt.get('PASS',0)}</b>UC PASS</span>
  <span class="kpi"><b>{cnt.get('PARCIAL',0)}</b>UC Parcial</span>
  <span class="kpi"><b>{len(executed)}</b>UC com escrita no banco</span>
</div>

<h4>Legenda de status</h4>
<p>{badge('PASS')} passo verificado &nbsp; {badge('VISUAL')} verificado pela tela renderizada
(exibição/ação agêntica) &nbsp; {badge('PARCIAL')} parcial &nbsp; {badge('N/EXEC')} não executado
automaticamente &nbsp; {badge('FAIL')} falhou.</p>

<h4>Execução das tarefas no servidor (WebSocket)</h4>
<table>
  <tr><th>Task</th><th>Resultado</th><th>Tempo</th><th>Amostra do retorno / erro</th></tr>
  {ws_rows or '<tr><td colspan=4 style="color:#888">execução WS não disponível</td></tr>'}
</table>
<p style="font-size:9pt;color:#555">Observação honesta: a task <code>cadastrar_persona_alvo</code>
é <b>determinística</b> (Python puro, escreve no banco). As demais são <b>agênticas</b> (dependem
do LLM local Qwen); o resultado reflete o que o modelo produziu no momento do teste.</p>

{uc_sections}

<div class="uc">
<h2>Uso como template no pipeline LangNet</h2>
<p>Este formato — <b>UC → passos → casos de teste → esperado vs obtido → evidência → status</b> —
é a base para inserir uma <b>etapa de Validação</b> no pipeline, após a Geração de Código:
o LangNet parseia os UCs da especificação, gera os casos de teste automaticamente, executa contra
a app gerada (UI + servidor + banco) e emite este documento como artefato de aceitação.</p>
</div>

</body></html>"""

out = f"{BASE}/validacao-por-uc-quantica.pdf"
HTML(string=html).write_pdf(out)
print(f"PDF: {out} ({os.path.getsize(out)//1024} KB)")

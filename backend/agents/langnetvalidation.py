"""
LangNet — Documento de Validação por Casos de Teste (a partir do CEG).

Formata os casos de teste gerados pelo Grafo de Causa-Efeito num documento padrão
de VALIDAÇÃO POR CASO DE USO — o template reutilizável:

  Capa → método → matriz-resumo → (por UC: cabeçalho + grafo + tabela de decisão +
  tabela de casos de teste com colunas "Resultado Obtido" e "Status" a preencher).

A coluna "Resultado Obtido" fica em branco (preenchida depois pelo Executor, ou
manualmente na validação assistida). Assim o documento serve tanto de roteiro de
teste quanto de registro de validação.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional

from agents.ceg_render import ceg_to_svg, _esc


def _cond_entrada(case: dict) -> str:
    """Renderiza as condições de entrada (ações do ator) de um caso como <li>."""
    itens = []
    for en in case.get("entradas", []):
        flag = "V" if en.get("verdadeira") else "F"
        cls = "vt" if en.get("verdadeira") else "vf"
        itens.append(f'<li><span class="flag {cls}">{flag}</span>{_esc(en.get("desc",""))}</li>')
    return "<ul class='conds'>" + "".join(itens) + "</ul>" if itens else "<span class='muted'>—</span>"


def _uc_block(r: dict, idx: int) -> str:
    if r.get("error"):
        return (f'<section class="uc"><h2>{_esc(r["uc"])} — {_esc(r.get("name",""))}</h2>'
                f'<p class="err">⚠ Grafo causa-efeito não gerado para este caso de uso '
                f'({_esc(r.get("error",""))}). Sem casos de teste.</p></section>')

    ceg = r.get("ceg", {})
    svg = ""
    try:
        svg = ceg_to_svg(ceg)
    except Exception:
        svg = "<p class='muted'>(grafo indisponível)</p>"

    # cabeçalho do UC
    meta_rows = ""
    for label, key in [("Ator", "actor"), ("Objetivo", "objetivo")]:
        val = r.get(key)
        if val:
            meta_rows += f"<tr><th>{label}</th><td>{_esc(val)}</td></tr>"
    meta_rows += (f"<tr><th>Cobertura</th><td>{r.get('n_causes',0)} causas · "
                  f"{r.get('n_effects',0)} efeitos · <b>{r.get('n_cases',0)} casos de teste</b></td></tr>")

    # tabela de decisão
    cols = ceg.get("_columns") or r.get("decision_table", [])
    cause_ids = [c["id"] for c in ceg.get("causes", [])]
    effect_ids = [e["id"] for e in ceg.get("effects", [])]

    def _cell(v):
        return "1" if v is True else ("0" if v is False else "X")

    dt_head = "".join(f"<th>C{i+1}</th>" for i in range(len(cols)))
    dt_rows = ""
    for cid in cause_ids:
        desc = next((c["desc"] for c in ceg.get("causes", []) if c["id"] == cid), cid)
        dt_rows += (f"<tr><td class='lbl' title='{_esc(desc)}'>{cid}</td>"
                    + "".join(f"<td>{_cell(c['causes'].get(cid))}</td>" for c in cols) + "</tr>")
    dt_rows += f"<tr class='sep'><td colspan='{len(cols)+1}'></td></tr>"
    for eid in effect_ids:
        desc = next((e["desc"] for e in ceg.get("effects", []) if e["id"] == eid), eid)
        dt_rows += (f"<tr><td class='lbl eff' title='{_esc(desc)}'>{eid}</td>"
                    + "".join(f"<td class='{'on' if c['effects'].get(eid) else ''}'>"
                              f"{'1' if c['effects'].get(eid) else '0'}</td>" for c in cols) + "</tr>")

    # tabela de casos de teste (formato de validação)
    tc_rows = ""
    for case in r.get("test_cases", []):
        tc_rows += (
            f"<tr>"
            f"<td class='tcid'>{_esc(case['id'])}</td>"
            f"<td>{_cond_entrada(case)}</td>"
            f"<td class='exp'>{_esc(case.get('efeito_esperado',{}).get('desc',''))}</td>"
            f"<td class='obt'></td>"
            f"<td class='st'><span class='chk'>☐ Aprovado</span><br><span class='chk'>☐ Reprovado</span></td>"
            f"</tr>"
        )

    return f"""
<section class="uc">
  <h2>{_esc(r['uc'])} — {_esc(r.get('name',''))}</h2>
  <table class="meta"><tbody>{meta_rows}</tbody></table>

  <h3>Grafo de Causa-Efeito</h3>
  <div class="graph">{svg}</div>

  <h3>Tabela de Decisão</h3>
  <table class="dt"><thead><tr><th></th>{dt_head}</tr></thead><tbody>{dt_rows}</tbody></table>
  <p class="legend">1 = verdadeiro · 0 = falso · X = indiferente (don't-care). Cada coluna Cn = um caso de teste.</p>

  <h3>Casos de Teste — Validação</h3>
  <table class="tc">
    <thead><tr>
      <th>ID</th><th>Condições de Entrada (ações do ator)</th>
      <th>Resultado Esperado (resposta do sistema)</th>
      <th>Resultado Obtido</th><th>Status</th>
    </tr></thead>
    <tbody>{tc_rows}</tbody>
  </table>
</section>
"""


def build_validation_html(results: List[dict], project_name: str, generated_at: str,
                          method_note: Optional[str] = None) -> str:
    """Monta o documento de validação completo (HTML) a partir dos resultados do CEG."""
    ok = [r for r in results if not r.get("error")]
    total_cases = sum(r.get("n_cases", 0) for r in ok)

    # matriz-resumo
    summary_rows = ""
    for r in results:
        n = "—" if r.get("error") else r.get("n_cases", 0)
        badge = "<span class='b-err'>falhou</span>" if r.get("error") else "<span class='b-ok'>pronto</span>"
        summary_rows += (f"<tr><td class='mono'>{_esc(r['uc'])}</td><td>{_esc(r.get('name',''))}</td>"
                         f"<td class='c'>{n}</td><td class='c'>{badge}</td></tr>")

    uc_blocks = "".join(_uc_block(r, i) for i, r in enumerate(results))

    method = method_note or (
        "Os casos de teste foram derivados dos casos de uso pela técnica do "
        "<b>Grafo de Causa-Efeito</b> (cause-effect graphing): as <b>causas</b> são as ações do ator "
        "e condições de entrada; os <b>efeitos</b> são as respostas do sistema. Para cada efeito, "
        "enumeram-se as combinações de causas que o ativam (tabela de decisão minimizada), e cada "
        "coluna da tabela vira um caso de teste. A coluna <b>Resultado Obtido</b> é preenchida na "
        "execução da validação (esperado × obtido)."
    )

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 18mm 14mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1e293b; font-size: 12px; line-height: 1.5; margin: 0; }}
  .cover {{ text-align: center; padding: 80px 20px 40px; }}
  .cover .tag {{ color: #1a56db; font-weight: 700; letter-spacing: 0.08em; font-size: 13px; text-transform: uppercase; }}
  .cover h1 {{ font-size: 30px; margin: 14px 0 6px; color: #0f172a; }}
  .cover .proj {{ font-size: 20px; color: #1a56db; font-weight: 600; }}
  .cover .sub {{ color: #64748b; margin-top: 8px; }}
  .cover .stats {{ display: inline-flex; gap: 30px; margin-top: 34px; padding: 18px 34px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; }}
  .cover .stats b {{ display: block; font-size: 28px; color: #1a56db; }}
  .cover .stats span {{ color: #64748b; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }}
  h2 {{ color: #1a56db; font-size: 17px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 30px; }}
  h3 {{ color: #334155; font-size: 13px; margin: 16px 0 8px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 4px 0; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 6px 9px; text-align: left; vertical-align: top; }}
  th {{ background: #f1f5f9; font-size: 11px; color: #475569; }}
  .meta {{ width: auto; margin-bottom: 6px; }}
  .meta th {{ background: #f8fafc; width: 90px; }}
  .section-intro {{ background: #f8fafc; border-left: 3px solid #1a56db; padding: 12px 16px; border-radius: 0 8px 8px 0; }}
  table.summary td.c, table.summary th.c {{ text-align: center; }}
  .mono {{ font-family: 'Courier New', monospace; font-weight: 700; color: #1a56db; }}
  .b-ok {{ color: #166534; background: #dcfce7; padding: 1px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; }}
  .b-err {{ color: #b91c1c; background: #fee2e2; padding: 1px 8px; border-radius: 10px; font-size: 10px; font-weight: 700; }}
  .uc {{ page-break-inside: avoid; margin-top: 26px; }}
  .graph {{ overflow: hidden; border: 1px solid #e2e8f0; border-radius: 8px; }}
  .graph svg {{ width: 100%; height: auto; }}
  table.dt {{ width: auto; font-size: 11px; }}
  table.dt th, table.dt td {{ text-align: center; padding: 3px 9px; }}
  table.dt td.lbl {{ font-weight: 700; background: #f8fafc; text-align: left; }}
  table.dt td.eff {{ color: #1d4ed8; }}
  table.dt td.on {{ background: #dcfce7; font-weight: 700; color: #166534; }}
  table.dt tr.sep td {{ border: none; height: 4px; padding: 0; }}
  .legend {{ font-size: 10px; color: #64748b; margin: 4px 0 0; }}
  table.tc th:nth-child(1) {{ width: 70px; }}
  table.tc th:nth-child(4), table.tc th:nth-child(5) {{ width: 110px; }}
  .tcid {{ font-family: 'Courier New', monospace; font-weight: 700; font-size: 10px; color: #1a56db; }}
  ul.conds {{ margin: 0; padding-left: 2px; list-style: none; }}
  ul.conds li {{ margin: 2px 0; }}
  .flag {{ display: inline-block; width: 15px; height: 15px; border-radius: 4px; text-align: center; line-height: 15px; font-size: 9px; font-weight: 700; margin-right: 6px; }}
  .flag.vt {{ background: #dcfce7; color: #166534; }}
  .flag.vf {{ background: #fee2e2; color: #b91c1c; }}
  td.exp {{ color: #166534; }}
  td.obt {{ background: #fffdf5; }}
  .chk {{ font-size: 10px; color: #64748b; }}
  .err {{ color: #b91c1c; }}
  .muted {{ color: #94a3b8; }}
  footer {{ margin-top: 40px; text-align: center; color: #94a3b8; font-size: 10px; border-top: 1px solid #e2e8f0; padding-top: 10px; }}
</style></head><body>

<div class="cover">
  <div class="tag">Documento de Validação</div>
  <h1>Casos de Teste &amp; Validação</h1>
  <div class="proj">{_esc(project_name)}</div>
  <div class="sub">Derivados por Grafo de Causa-Efeito · {_esc(generated_at)}</div>
  <div class="stats">
    <div><b>{len(ok)}</b><span>Casos de Uso</span></div>
    <div><b>{total_cases}</b><span>Casos de Teste</span></div>
  </div>
</div>

<h2>1. Método</h2>
<div class="section-intro">{method}</div>

<h2>2. Matriz-Resumo</h2>
<table class="summary">
  <thead><tr><th>UC</th><th>Caso de Uso</th><th class="c">Casos</th><th class="c">Grafo</th></tr></thead>
  <tbody>{summary_rows}</tbody>
</table>

<h2>3. Casos de Teste por Caso de Uso</h2>
{uc_blocks}

<footer>Gerado pelo LangNet · técnica Grafo de Causa-Efeito · {_esc(generated_at)}</footer>
</body></html>"""

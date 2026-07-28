"""
Contrato de coerência UC ⟷ Mockup ⟷ Modelo de Dados.

O protótipo (ui_spec) é DERIVADO de duas fontes de verdade:
  - Modelo de Dados: autoridade sobre o que é PERSISTIDO (tabelas/colunas).
  - Caso de Uso: autoridade sobre COMPORTAMENTO e sobre QUAIS telas existem.
O mockup nunca deve inventar entidade/coluna. Este módulo cruza as três
representações e devolve um relatório de divergências + correções propostas
(sem aplicar nada — a aplicação é decidida pelo usuário: "propor e você aprova").

Puro/determinístico (sem LLM): dá pra rodar sempre, barato.
"""
from __future__ import annotations

import difflib
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from prompts.generate_ui_spec import parse_schema_tables, find_uc_block


# ─────────────────────────────────────────────────────────────────────
# Tipo de tela a partir da INTENÇÃO do caso de uso (verbo)
# ─────────────────────────────────────────────────────────────────────
# Cada kind mapeia para os layouts de mockup aceitáveis.
_KIND_VERBS: List[Tuple[str, Tuple[str, ...]]] = [
    ("create",    ("cadastrar", "criar", "adicionar", "registrar", "incluir", "novo", "nova")),
    ("edit",      ("editar", "alterar", "atualizar", "modificar")),
    ("approve",   ("aprovar", "revisar", "validar", "homologar", "aprovacao")),
    ("dashboard", ("relatorio", "relatorios", "metrica", "metricas", "dashboard", "painel", "indicador", "indicadores", "monitorar")),
    ("action",    ("gerar", "verificar", "classificar", "coletar", "identificar", "publicar",
                   "sugerir", "sugestao", "sugestoes", "agendar", "sincronizar", "exportar", "disparar", "processar")),
    ("list",      ("listar", "consultar", "gerenciar", "pesquisar", "buscar", "visualizar")),
    ("view",      ("ver", "detalhar", "exibir", "mostrar")),
]

# layouts de mockup aceitáveis por kind
_KIND_OK_LAYOUTS: Dict[str, Tuple[str, ...]] = {
    "create":    ("form", "detail"),
    "edit":      ("form", "detail"),
    "view":      ("detail", "form"),
    "approve":   ("detail", "form", "table"),
    "list":      ("table",),
    "dashboard": ("dashboard", "detail"),
    "action":    ("detail", "dashboard", "form"),
}
_KIND_SUGGESTED_LAYOUT: Dict[str, str] = {
    "create": "form", "edit": "form", "view": "detail", "approve": "detail",
    "list": "table", "dashboard": "dashboard", "action": "detail",
}


def _norm(s: str) -> str:
    """minúsculas sem acento, para casar verbos."""
    s = (s or "").lower()
    for a, b in (("á", "a"), ("â", "a"), ("ã", "a"), ("é", "e"), ("ê", "e"),
                 ("í", "i"), ("ó", "o"), ("ô", "o"), ("õ", "o"), ("ú", "u"), ("ç", "c")):
        s = s.replace(a, b)
    return s


def derive_screen_kind(uc: Dict[str, str]) -> str:
    """Deriva o tipo de tela a partir do verbo do nome do UC (fonte: comportamento).
    Ordem importa: verbos mais específicos (create/edit/approve/action) antes de
    'visualizar' (que é ambíguo com list)."""
    name = _norm(uc.get("name", ""))
    first = name.split()[0] if name.split() else ""
    for kind, verbs in _KIND_VERBS:
        if first in verbs or any(re.search(rf"\b{re.escape(v)}\b", name) for v in verbs):
            return kind
    return "view"


# ─────────────────────────────────────────────────────────────────────
# Schema real (tabela → colunas)
# ─────────────────────────────────────────────────────────────────────
def schema_columns(schema_sql: str) -> Dict[str, List[str]]:
    """{tabela: [colunas]} a partir do DDL real."""
    tables = parse_schema_tables(schema_sql) if schema_sql else {}
    out: Dict[str, List[str]] = {}
    for name, ddl in tables.items():
        cols = []
        for m in re.finditer(
            r'^\s*[`"]?(\w+)[`"]?\s+(?:CHAR|VARCHAR|TEXT|LONGTEXT|MEDIUMTEXT|INT|INTEGER|BIGINT|'
            r'SMALLINT|TINYINT|DECIMAL|NUMERIC|FLOAT|DOUBLE|DATE|DATETIME|TIMESTAMP|TIME|ENUM|SET|'
            r'BOOLEAN|BOOL|JSON|BLOB|GEOMETRY)',
            ddl, re.I | re.M,
        ):
            cols.append(m.group(1))
        out[name] = cols
    return out


def schema_fks(schema_sql: str) -> Dict[str, Dict[str, str]]:
    """Mapa de chaves estrangeiras: {tabela: {coluna: tabela_referenciada}}.
    Detecta FK explícita (FOREIGN KEY ... REFERENCES) e, como fallback, a convenção
    `<x>_id` → tabela `<x>` / `<x>s` / `<x>es` quando ela existe no schema."""
    tables = parse_schema_tables(schema_sql) if schema_sql else {}
    names = set(tables.keys())
    fks: Dict[str, Dict[str, str]] = {}
    for tname, ddl in tables.items():
        m: Dict[str, str] = {}
        for fm in re.finditer(
            r'FOREIGN\s+KEY\s*\(\s*[`"]?(\w+)[`"]?\s*\)\s*REFERENCES\s*[`"]?(\w+)[`"]?', ddl, re.I):
            if fm.group(2) in names:
                m[fm.group(1)] = fm.group(2)
        for cm in re.finditer(r'^\s*[`"]?(\w+_id)[`"]?\s', ddl, re.I | re.M):
            col = cm.group(1)
            if col in m:
                continue
            base = col[:-3]
            for cand in (base, base + "s", base + "es", base.rstrip("s")):
                if cand in names:
                    m[col] = cand
                    break
        if m:
            fks[tname] = m
    return fks


def _parse_bindto(bind: str) -> Optional[Tuple[str, str]]:
    """'tabela.coluna' | 'tabela_filha[].coluna' | 'tabela.coluna[]' → (tabela, coluna)."""
    if not bind or "." not in bind:
        return None
    left, right = bind.split(".", 1)
    table = left.replace("[]", "").strip()
    col = right.split("[")[0].replace("[]", "").strip()
    if not table or not col:
        return None
    return table, col


def _closest(name: str, options: List[str], cutoff: float = 0.72) -> Optional[str]:
    m = difflib.get_close_matches(name.lower(), [o.lower() for o in options], n=1, cutoff=cutoff)
    if not m:
        return None
    # devolve com a capitalização original
    for o in options:
        if o.lower() == m[0]:
            return o
    return m[0]


def _guess_sql_type(col: str) -> str:
    """Tipo SQL provável a partir do nome da coluna (para propostas de DM)."""
    c = col.lower()
    if c == "id" or c.endswith("_id"):
        return "INT"
    if c.startswith("data") or c.endswith("_em") or c in ("created_at", "updated_at"):
        return "DATETIME"
    if c.startswith("is_") or c.startswith("tem_") or c.startswith("ativo"):
        return "BOOLEAN"
    if c in ("hora",):
        return "TIME"
    if c in ("valor", "preco", "total", "quantidade", "qtd"):
        return "DECIMAL(12,2)"
    if any(k in c for k in ("descricao", "conteudo", "texto", "observ", "corpo", "mensagem")):
        return "TEXT"
    return "VARCHAR(255)"


# ─────────────────────────────────────────────────────────────────────
# Checagem por tela
# ─────────────────────────────────────────────────────────────────────
def check_screen_coherence(
    screen: Dict[str, Any],
    cols_by_table: Dict[str, List[str]],
    uc: Optional[Dict[str, str]],
) -> Dict[str, Any]:
    """Cruza UMA tela contra o schema real + o UC de origem. Devolve issues +
    correções propostas (ordem de preferência)."""
    issues: List[Dict[str, Any]] = []
    tables = list(cols_by_table.keys())

    # 1) tipo de tela x intenção do UC
    kind = derive_screen_kind(uc) if uc else None
    layout = (screen.get("layout") or "").lower()
    if kind and layout:
        ok_layouts = _KIND_OK_LAYOUTS.get(kind, ())
        if ok_layouts and layout not in ok_layouts:
            issues.append({
                "type": "kind_mismatch",
                "severity": "warning",
                "detail": f"UC é '{kind}' mas o mockup está como '{layout}'",
                "expected_layout": _KIND_SUGGESTED_LAYOUT.get(kind),
                "proposed_fixes": [
                    {"action": "regenerate_screen",
                     "label": f"Regenerar a tela como '{_KIND_SUGGESTED_LAYOUT.get(kind)}'"}
                ],
            })

    # 2) vínculos bindTo x schema real
    for comp in (screen.get("components") or []):
        bind = comp.get("bindTo")
        if not bind or "." not in str(bind):
            continue
        parsed = _parse_bindto(bind)
        if not parsed:
            continue
        table, col = parsed
        field_label = comp.get("label") or comp.get("field") or col

        if table not in cols_by_table:
            near = _closest(table, tables)
            fixes = []
            if near:
                fixes.append({"action": "rebind_table", "to": near,
                              "label": f"Religar para a tabela existente '{near}'"})
            fixes.append({"action": "add_to_dm", "table": table, "column": col,
                          "sql_type": _guess_sql_type(col), "new_table": True,
                          "label": f"Adicionar tabela '{table}' ao Modelo de Dados"})
            fixes.append({"action": "mark_non_persistent",
                          "label": "Marcar campo como não-persistente (bindTo nulo)"})
            issues.append({
                "type": "missing_table", "severity": "error",
                "detail": f"campo '{field_label}' → '{bind}': tabela '{table}' não existe no banco",
                "bindTo": bind, "table": table, "column": col,
                "proposed_fixes": fixes,
            })
        elif col not in [c.lower() for c in cols_by_table[table]] and col not in cols_by_table[table]:
            near = _closest(col, cols_by_table[table])
            fixes = []
            if near:
                fixes.append({"action": "rebind_column", "to": f"{table}.{near}",
                              "label": f"Religar para a coluna existente '{table}.{near}'"})
            fixes.append({"action": "add_to_dm", "table": table, "column": col,
                          "sql_type": _guess_sql_type(col), "new_table": False,
                          "label": f"Adicionar coluna '{col}' à tabela '{table}'"})
            fixes.append({"action": "mark_non_persistent",
                          "label": "Marcar campo como não-persistente (bindTo nulo)"})
            issues.append({
                "type": "missing_column", "severity": "error",
                "detail": f"campo '{field_label}' → '{bind}': coluna '{col}' não existe em '{table}'",
                "bindTo": bind, "table": table, "column": col,
                "proposed_fixes": fixes,
            })

    return {
        "screen_id": screen.get("id"),
        "screen_name": screen.get("name"),
        "uc_id": (screen.get("uc") or [None])[0],
        "kind": kind,
        "layout": layout,
        "entity": screen.get("entity"),
        "issues": issues,
        "ok": len(issues) == 0,
    }


# ─────────────────────────────────────────────────────────────────────
# Relatório da suíte inteira + propostas agregadas para o Modelo de Dados
# ─────────────────────────────────────────────────────────────────────
def check_ui_spec_coherence(
    ui_spec: Dict[str, Any],
    schema_sql: str,
    specification_document: str = "",
) -> Dict[str, Any]:
    """Relatório de coerência de TODAS as telas + mudanças propostas ao Modelo de
    Dados (agregadas e deduplicadas). Não aplica nada."""
    cols_by_table = schema_columns(schema_sql)
    screens = ui_spec.get("screens", []) if ui_spec else []

    per_screen: List[Dict[str, Any]] = []
    # dedup de propostas de DM: chave (tabela, coluna)
    dm_changes: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for sc in screens:
        uc_id = (sc.get("uc") or [None])[0]
        uc = None
        if uc_id and specification_document:
            found = find_uc_block(specification_document, uc_id)
            uc = found["uc"] if found else None
        rep = check_screen_coherence(sc, cols_by_table, uc)
        per_screen.append(rep)

        for iss in rep["issues"]:
            for fx in iss.get("proposed_fixes", []):
                if fx.get("action") == "add_to_dm":
                    key = (fx["table"], fx["column"])
                    entry = dm_changes.setdefault(key, {
                        "table": fx["table"], "column": fx["column"],
                        "sql_type": fx.get("sql_type", "VARCHAR(255)"),
                        "new_table": fx.get("new_table", False),
                        "screens": [],
                    })
                    if sc.get("id") not in entry["screens"]:
                        entry["screens"].append(sc.get("id"))

    n_broken = sum(1 for r in per_screen for i in r["issues"] if i["type"] in ("missing_table", "missing_column"))
    n_kind = sum(1 for r in per_screen for i in r["issues"] if i["type"] == "kind_mismatch")
    total_binds = sum(
        1 for sc in screens for comp in (sc.get("components") or [])
        if comp.get("bindTo") and "." in str(comp.get("bindTo"))
    )

    # agrupa propostas por tabela (nova tabela vs coluna nova)
    proposed = sorted(dm_changes.values(), key=lambda x: (not x["new_table"], x["table"], x["column"]))

    return {
        "summary": {
            "screens": len(screens),
            "screens_with_issues": sum(1 for r in per_screen if not r["ok"]),
            "broken_binds": n_broken,
            "total_binds": total_binds,
            "kind_mismatches": n_kind,
            "proposed_dm_changes": len(proposed),
        },
        "screens": per_screen,
        "proposed_dm_changes": proposed,
    }


# ─────────────────────────────────────────────────────────────────────
# Reconciliação (aplica no Modelo de Dados) — DETERMINÍSTICO, sem LLM
# ─────────────────────────────────────────────────────────────────────
def _emit_column_ddl(col: str, sql_type: str) -> str:
    return f"  `{col}` {sql_type} NULL,"


def apply_dm_changes(
    entities_json: str,
    schema_sql: str,
    changes: List[Dict[str, Any]],
) -> Tuple[str, str, List[Dict[str, Any]]]:
    """Aplica ADIÇÕES (colunas/tabelas) ao Modelo de Dados de forma determinística:
    atualiza entities_json (fonte lógica) e injeta no schema_sql. Nunca altera/remove
    nada existente. Retorna (novo_entities_json, novo_schema_sql, aplicadas)."""
    try:
        model = json.loads(entities_json) if entities_json else {}
    except Exception:
        model = {}
    if not isinstance(model, dict):
        model = {}
    tables = model.setdefault("tables", [])
    by_name = {t.get("name"): t for t in tables if isinstance(t, dict)}
    existing_sql = parse_schema_tables(schema_sql) if schema_sql else {}

    applied: List[Dict[str, Any]] = []
    # agrupa por tabela para criar tabela nova uma única vez
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for ch in changes:
        grouped.setdefault(ch["table"], []).append(ch)

    new_schema = schema_sql or ""

    for table, chs in grouped.items():
        cols_to_add = []
        for ch in chs:
            col = ch["column"]
            sql_type = ch.get("sql_type", "VARCHAR(255)")
            # ── entities_json ──
            tdef = by_name.get(table)
            if tdef is None:
                tdef = {"name": table,
                        "description": "(auto) criada pela reconciliação de coerência de telas",
                        "columns": [{"name": "id", "type": "INT", "pk": True, "nullable": False}]}
                tables.append(tdef); by_name[table] = tdef
            existing_cols = {c.get("name") for c in tdef.get("columns", [])}
            if col not in existing_cols:
                tdef.setdefault("columns", []).append(
                    {"name": col, "type": sql_type, "nullable": True})
                cols_to_add.append((col, sql_type))
                applied.append({"table": table, "column": col, "sql_type": sql_type,
                                "kind": "new_table" if table not in existing_sql else "new_column"})

        if not cols_to_add:
            continue

        # ── schema_sql ──
        if table in existing_sql:
            old_ddl = existing_sql[table]
            # injeta as novas colunas logo após "CREATE TABLE `x` (" (vira 1ª coluna,
            # seguida de vírgula — sempre válido, sem problema de vírgula final)
            m = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"]?' +
                          re.escape(table) + r'[`"]?\s*\(', old_ddl, re.I)
            if m:
                inject = "\n" + "\n".join(_emit_column_ddl(c, t) for c, t in cols_to_add)
                new_ddl = old_ddl[:m.end()] + inject + old_ddl[m.end():]
                new_schema = new_schema.replace(old_ddl, new_ddl, 1)
        else:
            # tabela nova: emite CREATE TABLE com id + colunas
            body = ["  `id` INT NOT NULL AUTO_INCREMENT,"]
            body += [_emit_column_ddl(c, t) for c, t in cols_to_add]
            body.append("  PRIMARY KEY (`id`)")
            block = (f"\n\nCREATE TABLE `{table}` (\n" + "\n".join(body) +
                     "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;")
            new_schema = (new_schema.rstrip() + block) if new_schema.strip() else block.strip()

    return json.dumps(model, ensure_ascii=False, indent=2), new_schema, applied


def apply_rebind(ui_spec: Dict[str, Any], screen_id: str, bind_old: str, bind_new: str) -> bool:
    """Religa um componente do mockup a uma coluna existente (correção lado-mockup).
    Retorna True se aplicou."""
    for s in ui_spec.get("screens", []):
        if s.get("id") != screen_id:
            continue
        for comp in (s.get("components") or []):
            if comp.get("bindTo") == bind_old:
                comp["bindTo"] = bind_new
                return True
    return False

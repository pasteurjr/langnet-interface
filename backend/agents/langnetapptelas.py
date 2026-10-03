"""Telas do aplicativo = telas do protótipo aprovado (F4 do plano v1.1).

O desenho NÃO é refeito: a tela do aplicativo é o mesmo HTML que foi aprovado na etapa de
Interface & Protótipo. O que muda é a fonte do comportamento — no protótipo cada botão só dizia
quem o executa; no aplicativo um CONTROLADOR por tela (escrito pelo modelo, conferido pelo
programa) liga as marcas do desenho aos executores:

  data-acao      → pronto (moldes da API) · código gerado (regras do caso de uso) · agente (framework)
  data-campo     → o valor real (registro aberto, lista, resultado do agente)
  data-agente    → o bloco do agente, com os cinco estados
  data-mensagem  → a mensagem do fluxo, quando o caso acontece

Medido no BioByte v5 (03/10/2026): a Geração de Código nunca lia o desenho (zero usos de
mockup_html); as telas saíam de outro molde, com "—" nos campos, e quatro semanas de refino do
protótipo paravam na etapa de Interface.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Tuple

# ── biblioteca de tempo de execução (igual em todo aplicativo) ───────────────

LNX_JS = r"""// lnx.js — liga o desenho aprovado aos executores (gerado pelo LangNet; não editar à mão)
import { runTask } from "./screens/wsClient";

const API = process.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_API_URL || "http://localhost:8001";
const CHAVE = "lnx.sessao";

export function sessao() { try { return JSON.parse(localStorage.getItem(CHAVE) || "null"); } catch (e) { return null; } }
export function sair() { try { localStorage.removeItem(CHAVE); } catch (e) {} if (window.LNX_TEM_LOGIN) window.location.reload(); }

async function pedir(metodo, caminho, corpo) {
  const s = sessao();
  const r = await fetch(API + caminho, {
    method: metodo,
    headers: { "Content-Type": "application/json", ...(s && s.token ? { Authorization: "Bearer " + s.token } : {}) },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  });
  let d = null; try { d = await r.json(); } catch (e) {}
  if (r.status === 401 && caminho !== "/api/auth/login") { sair(); }
  if (!r.ok) throw new Error((d && (d.erro || d.detail)) || ("Falha " + r.status));
  return d;
}
export const api = {
  get: (c) => pedir("GET", c), post: (c, b) => pedir("POST", c, b || {}),
  put: (c, b) => pedir("PUT", c, b || {}), del: (c) => pedir("DELETE", c),
  async login(email, senha) {
    const d = await pedir("POST", "/api/auth/login", { email, senha });
    localStorage.setItem(CHAVE, JSON.stringify(d)); return d;
  },
};

// contexto: o caso/atendimento aberto, que passa de uma tela para a outra
export function contexto(chave, valor) {
  let c = {}; try { c = JSON.parse(localStorage.getItem("lnx.contexto") || "{}"); } catch (e) {}
  if (valor === undefined) return chave ? c[chave] : c;
  c[chave] = valor; localStorage.setItem("lnx.contexto", JSON.stringify(c)); return valor;
}

// agente: a tarefa do framework, pelo nome; as entradas que vêm do banco o PROGRAMA busca antes
export async function agente(tarefa, entradas, bloco) {
  estado(bloco, "executando");
  try {
    const doBanco = await api.post("/api/agente/entradas/" + tarefa, entradas || {});
    const r = await runTask(tarefa, { ...(doBanco || {}), ...(entradas || {}) });
    const res = (r && r.result !== undefined) ? r.result : r;
    if (res && (res.status === "recusado" || res.dados_insuficientes)) { estado(bloco, "recusado"); return { recusado: true, ...res }; }
    estado(bloco, "concluído"); return res;
  } catch (e) { estado(bloco, "erro"); throw e; }
}

export function estado(bloco, e) {
  if (!bloco) return;
  bloco.setAttribute("data-estado", e);
  bloco.classList.toggle("lnx-executando", e === "executando");
  const passos = bloco.querySelector("[data-andamento]");
  if (passos) passos.style.display = e === "executando" ? "" : "none";
}

// preencher: põe os valores reais nos elementos marcados com data-campo
export function preencher(raiz, dados) {
  if (!raiz || !dados) return;
  raiz.querySelectorAll("[data-campo]").forEach((el) => {
    const k = el.getAttribute("data-campo");
    if (!(k in dados)) return;
    const v = dados[k];
    if ("value" in el && /^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName)) {
      if (el.type === "checkbox") el.checked = !!v; else el.value = v == null ? "" : v;
    } else if (Array.isArray(v)) { el.textContent = v.join(", "); }
    else el.textContent = v == null || v === "" ? "—" : (typeof v === "boolean" ? (v ? "Sim" : "Não") : String(v));
  });
}

// colher: lê os campos de entrada marcados com data-campo
export function colher(raiz) {
  const o = {};
  (raiz || document).querySelectorAll("input[data-campo], select[data-campo], textarea[data-campo]").forEach((el) => {
    const k = el.getAttribute("data-campo");
    o[k] = el.type === "checkbox" ? el.checked : el.value;
  });
  return o;
}

// linhas: repete a PRIMEIRA linha do corpo da tabela (o desenho aprovado) para cada registro
export function linhas(tabela, registros, aoClicar) {
  const corpo = tabela && (tabela.tBodies[0] || tabela);
  if (!corpo) return;
  if (!corpo._molde) { const m = corpo.querySelector("tr"); corpo._molde = m ? m.cloneNode(true) : null; }
  if (!corpo._molde) return;
  corpo.innerHTML = "";
  if (!registros || !registros.length) {
    const tr = document.createElement("tr"); const td = document.createElement("td");
    td.colSpan = corpo._molde.children.length || 1; td.className = "py-6 text-center text-slate-400";
    td.textContent = "Nenhum registro."; tr.appendChild(td); corpo.appendChild(tr); return;
  }
  registros.forEach((r) => {
    const tr = corpo._molde.cloneNode(true); preencher(tr, r);
    tr.querySelectorAll("[data-acao]").forEach((b) => (b._registro = r));
    if (aoClicar) tr.addEventListener("click", (ev) => { if (!ev.target.closest("[data-acao]")) aoClicar(r, ev); });
    corpo.appendChild(tr);
  });
}

// opções: lista de vínculo/lista fechada num <select>, com rótulo legível (nunca id cru)
export async function opcoes(select, tabela, coluna) {
  if (!select) return;
  const ops = await api.get(`/api/opcoes/${tabela}/${coluna}`);
  const atual = select.value;
  select.innerHTML = '<option value="">Selecione…</option>' + ops.map((o) => `<option value="${o.valor}">${o.rotulo}</option>`).join("");
  if (atual) select.value = atual;
}

// mensagem: a do fluxo (data-mensagem="<passo>") ou um aviso com o texto dado
export function mensagem(raiz, passoOuTexto, tipo) {
  (raiz || document).querySelectorAll("[data-mensagem]").forEach((m) => (m.style.display = "none"));
  const alvo = (raiz || document).querySelector(`[data-mensagem="${passoOuTexto}"]`);
  if (alvo) { alvo.style.display = ""; alvo.scrollIntoView({ block: "nearest" }); return; }
  let av = (raiz || document).querySelector(".lnx-aviso");
  if (!av) { av = document.createElement("div"); av.className = "lnx-aviso"; (raiz.querySelector("main") || raiz).prepend(av); }
  av.textContent = passoOuTexto; av.setAttribute("data-tipo", tipo || "erro"); av.style.display = "";
}

// ação: liga um botão marcado com data-acao a uma função; erro nunca vira sucesso
export function acao(raiz, id, fn) {
  (raiz || document).querySelectorAll(`[data-acao="${id}"]`).forEach((b) => {
    if (b._ligado) return; b._ligado = true;
    b.addEventListener("click", async (ev) => {
      ev.preventDefault();
      if (b.disabled) return; b.disabled = true; b.classList.add("opacity-60");
      try { await fn(b._registro, ev); }
      catch (e) { mensagem(raiz, e.message || String(e), "erro"); }
      finally { b.disabled = false; b.classList.remove("opacity-60"); }
    });
  });
}

export function confirmar(texto) { return window.confirm(texto); }
export function navegar(tela) { window.dispatchEvent(new CustomEvent("lnx:navegar", { detail: tela })); }
"""


def corpo_da_tela(mockup_html: str) -> str:
    """O conteúdo da tela, sem cabeçalho de página nem menu lateral próprio (o aplicativo tem o seu)."""
    m = re.search(r"<body[^>]*>(.*)</body>", mockup_html or "", re.S | re.I)
    corpo = m.group(1) if m else (mockup_html or "")
    corpo = re.sub(r"<script\b.*?</script>", "", corpo, flags=re.S | re.I)
    corpo = re.sub(r"<aside\b.*?</aside>", "", corpo, count=1, flags=re.S | re.I)
    # o invólucro "flex min-h-screen" do mockup ficava com o menu; sem menu, ocupa a largura toda
    return corpo.strip()


def recursos_da_tela(mockup_html: str) -> List[str]:
    """Bibliotecas de desenho que o mockup usa (gráfico, mapa), para o index.html carregar."""
    out = []
    for m in re.finditer(r'<(?:script|link)[^>]+(?:src|href)="(https://cdn\.jsdelivr\.net/npm/[^"]+)"', mockup_html or ""):
        out.append(m.group(1))
    return out


def componente_jsx(nome: str, screen: Dict) -> str:
    """Componente React da tela: põe o desenho aprovado e chama o controlador."""
    corpo = json.dumps(corpo_da_tela(screen.get("mockup_html") or ""), ensure_ascii=False)
    return f"""// {screen.get('name')} — {', '.join(screen.get('uc') or [])} (desenho aprovado no protótipo; gerado pelo LangNet)
import React, {{ useEffect, useRef }} from "react";
import * as lnx from "../lnx";
import montar from "../controladores/{nome}";

const DESENHO = {corpo};

export default function {nome}() {{
  const raiz = useRef(null);
  useEffect(() => {{
    let desmontar;
    try {{ desmontar = montar(raiz.current, lnx); }}
    catch (e) {{ lnx.mensagem(raiz.current, "Falha ao abrir a tela: " + (e.message || e)); }}
    return () => {{ if (typeof desmontar === "function") desmontar(); }};
  }}, []);
  return <div ref={{raiz}} className="lnx-tela" dangerouslySetInnerHTML={{{{ __html: DESENHO }}}} />;
}}
"""


# ── o controlador de cada tela: escrito pelo modelo, conferido pelo programa ──

def marcas_do_desenho(html: str) -> Dict[str, List[str]]:
    def todos(attr):
        return sorted(set(re.findall(rf'{attr}="([^"]+)"', html or "")))
    return {"acoes": todos("data-acao"), "campos": todos("data-campo"),
            "agentes": todos("data-agente"), "mensagens": todos("data-mensagem"),
            "tabelas": len(re.findall(r"<table\b", html or "", re.I)),
            "selects": re.findall(r'<select[^>]*data-campo="([^"]+)"', html or "")}


_PEDIDO = """Você escreve o CONTROLADOR de UMA tela de um aplicativo já desenhado. O desenho (HTML) foi aprovado
pelo cliente e NÃO pode mudar. Seu código liga as marcas do desenho aos executores declarados na
Especificação. Responda SÓ com um objeto JSON: {{"controlador_js": "...", "regras_py": "..."}}.

## A TELA
Nome: {nome} · Casos de uso: {ucs}

### Ações (cada botão tem data-acao="<id>"; o EXECUTOR já foi decidido — obedeça)
{acoes}

### Blocos de agente (data-agente="<passo>")
{agentes}

### Mensagens dos fluxos (data-mensagem="<passo>" ou aviso): mostre quando o caso acontecer
{mensagens}

### Passos do caso de uso (o que o sistema faz em cada um)
{passos}

### Tarefa do agente deste caso de uso (framework)
{tarefa}

### Cadastros do modelo de dados (tabela: colunas) — só estes existem
{tabelas}

### Marcas presentes no desenho
{marcas}

### DESENHO (HTML aprovado — só para você saber onde estão as marcas)
{html}

## A BIBLIOTECA `lnx` (única forma de agir; nada de fetch direto)
- lnx.acao(raiz, "<id>", async (registro) => {{...}}) — liga o botão; erro lançado vira mensagem na tela
- lnx.api.get/post/put/del(caminho, corpo) — API do aplicativo. Moldes `pronto`:
  GET /api/dados/<tabela>?q=&<coluna>=<valor> → {{rows, total}} · GET /api/dados/<tabela>/<id> ·
  POST /api/dados/<tabela> · PUT /api/dados/<tabela>/<id> · DELETE /api/dados/<tabela>/<id> ·
  GET /api/opcoes/<tabela>/<coluna> (vínculo/lista fechada) · GET /api/relatorio/<tabela>?agrupar=<col>
  · lnx.api.login(email, senha) (tela de login; depois window.location.reload())
- lnx.agente("<nome_da_tarefa>", entradas, blocoEl) — passo `agente`: roda a tarefa no framework; o
  programa busca no banco as entradas de origem `banco`; devolve o resultado ou {{recusado:true,...}}
- lnx.preencher(el, dados) · lnx.colher(el) → {{campo: valor}} · lnx.linhas(tabelaEl, rows, aoClicar)
  (repete a 1ª linha do <tbody> do desenho) · lnx.opcoes(selectEl, tabela, coluna) ·
  lnx.mensagem(raiz, "<passo>" ou "texto", "erro"|"ok") · lnx.contexto("caso_id"[, valor]) ·
  lnx.confirmar(texto) · lnx.navegar("<id-da-tela>") · lnx.sessao()

## REGRAS
1. `controlador_js`: `export default function montar(raiz, lnx) {{ ... }}` (JavaScript, sem import). Ao
   montar: carregue os dados reais (lista, registro do contexto, opções dos <select>) e preencha o
   desenho; troque TODO valor de exemplo pelo real ou por "—". Ligue CADA ação da lista com lnx.acao.
2. Executor `pronto` → moldes da API acima. `código gerado` → rota que VOCÊ escreve em `regras_py`
   (POST/GET /api/uc/<UC>/<nome>), chamada por lnx.api. `agente` → lnx.agente com o nome EXATO da
   tarefa acima, mostrando o resultado no bloco do agente (preencher os data-campo do bloco) e a
   justificativa sempre visível. `navegação` → lnx.navegar.
3. Antes de gravar decisão clínica ou enviar algo para fora: lnx.confirmar.
4. Recusa e erro NUNCA aparecem como sucesso: use a mensagem do caso de uso (data-mensagem do passo).
5. `regras_py`: só as regras `código gerado` que precisam do banco ou de cálculo. Formato EXATO:
   def rotas(app, ctx):
       @app.post("/api/uc/{uc0}/<nome>")
       def _x(corpo: dict, u=ctx["Depends"](ctx["usuario"])):
           c = ctx["conexao"](); cur = c.cursor(dictionary=True)
           try: ...  # SQL com %s, só tabelas/colunas do modelo
           finally: cur.close(); c.close()
           return {{...}}  # erro de negócio: raise ctx["HTTPException"](422, {{"erro": "<mensagem do caso de uso>"}})
   Use ctx["limpo"](linha) ao devolver linhas (tira dado sensível). Se não precisar, "regras_py": "".
6. Nunca leia, mostre ou guarde senha/hash/token em tela.
7. Texto de exemplo do desenho que mostra número, contagem, nome ou data SEM data-campo (ex.: "58
   usuários", "▲ 3 vs. mês anterior", "Hospital São Lucas"): substitua pelo valor real calculado dos
   dados carregados ou apague o texto. Nenhum dado inventado pode sobrar na tela.
8. lnx.navegar só para estas telas: {telas}.
"""


def pedido_controlador(screen: Dict, uc_raw: str, tarefa: Optional[Dict], tabelas: Dict[str, List[str]],
                       telas_ids: Optional[List[str]] = None) -> str:
    from agents.langnetfichatela import passos_para_prompt
    html = screen.get("mockup_html") or ""
    corpo = corpo_da_tela(html)
    acoes = "\n".join(f"- {a.get('id')}: \"{a.get('label')}\" → {a.get('executado_por') or 'SEM EXECUTOR'}"
                      + (f" · passo {a.get('passo')}: {a.get('resposta','')[:220]}" if a.get('passo') else "")
                      + (f" · abre {a.get('navegar_para')}" if a.get('navegar_para') else "")
                      for a in screen.get("actions") or []) or "(nenhuma)"
    agentes = "\n".join(f"- {b['passo']} · forma {b.get('forma')} · {b.get('rotulo')}"
                        + (f" · variantes {b.get('variantes')}" if b.get('variantes') else "")
                        for b in screen.get("agentes") or []) or "(nenhum)"
    msgs = "\n".join(f"- {m['passo']} ({m.get('quando','')[:120]}): \"{m['texto']}\"" for m in screen.get("mensagens") or []) or "(nenhuma)"
    usadas = {re.split(r"[.\[]", str(c.get("bindTo") or ""))[0] for c in screen.get("components") or [] if c.get("bindTo")}
    usadas |= {screen.get("entity")} if screen.get("entity") else set()
    tabs = "\n".join(f"- {t}: {', '.join(cs)}" for t, cs in tabelas.items() if t in usadas) or \
        "\n".join(f"- {t}: {', '.join(cs)}" for t, cs in list(tabelas.items())[:12])
    tar = "(nenhuma)"
    if tarefa:
        tar = (f"nome: {tarefa.get('name')}\nentradas: {tarefa.get('input_schema','')[:600]}\n"
               f"origem das entradas: {tarefa.get('origens_txt') or json.dumps(tarefa.get('origens') or {}, ensure_ascii=False)}\n"
               f"saída: {tarefa.get('output_schema','')[:600]}")
    ucs = screen.get("uc") or []
    return _PEDIDO.format(nome=screen.get("name"), ucs=", ".join(ucs), acoes=acoes, agentes=agentes,
                          mensagens=msgs, passos=passos_para_prompt(uc_raw)[:9000], tarefa=tar, tabelas=tabs,
                          marcas=json.dumps(marcas_do_desenho(corpo), ensure_ascii=False),
                          html=corpo[:40000], uc0=(ucs[0] if ucs else "UC"),
                          telas=", ".join(telas_ids or []) or "(nenhuma outra)")


def conferir_controlador(js: str, py: str, screen: Dict, tarefa_nome: Optional[str],
                         tabelas: Dict[str, List[str]], telas_ids: Optional[List[str]] = None) -> List[str]:
    """Problemas do controlador (programa). Lista vazia = aprovado."""
    p = []
    sid = screen.get("id")
    if "export default function montar" not in (js or ""):
        return [f"{sid}: controlador sem `export default function montar(raiz, lnx)`"]
    for a in screen.get("actions") or []:
        if not re.search(rf"""lnx\.acao\(\s*raiz\s*,\s*["'`]{re.escape(str(a.get('id')))}["'`]""", js):
            p.append(f"{sid}: ação {a.get('id')} (\"{a.get('label')}\") não está ligada no controlador")
    if any(a.get("executado_por") == "agente" for a in screen.get("actions") or []):
        if not tarefa_nome:
            p.append(f"{sid}: ação de agente sem tarefa no documento de Agentes e Tarefas")
        elif not re.search(rf"""lnx\.agente\(\s*["'`]{re.escape(tarefa_nome)}["'`]""", js):
            p.append(f"{sid}: a ação de agente não chama a tarefa {tarefa_nome}")
    if re.search(r"\bfetch\s*\(|XMLHttpRequest", js):
        p.append(f"{sid}: controlador chama a rede por fora da biblioteca")
    if re.search(r"senha_hash|password_hash|senha_sal", js):
        p.append(f"{sid}: controlador toca em dado sensível")
    for t in set(re.findall(r"/api/(?:dados|opcoes|relatorio)/([a-z_]\w*)", js)):
        if t not in tabelas:
            p.append(f"{sid}: controlador usa o cadastro {t}, que não existe no modelo de dados")
    if telas_ids:
        for destino in set(re.findall(r"""lnx\.navegar\(\s*["'`]([^"'`]+)["'`]""", js)):
            if destino not in telas_ids:
                p.append(f"{sid}: navega para a tela \"{destino}\", que não existe no aplicativo")
    rotas_py = set(re.findall(r"""@app\.(?:get|post|put|delete)\(\s*["']([^"']+)["']""", py or ""))
    for r in set(re.findall(r"""["'`](/api/uc/[^"'`?$]+)""", js)):
        if r not in rotas_py:
            p.append(f"{sid}: controlador chama {r}, rota que as regras não definem")
    if py and py.strip():
        try:
            compile(py, f"regras_{sid}", "exec")
        except SyntaxError as e:
            p.append(f"{sid}: regras com erro de sintaxe: {e.msg} (linha {e.lineno})")
        if "def rotas(app, ctx)" not in py:
            p.append(f"{sid}: regras sem `def rotas(app, ctx)`")
    return p


def montar_regras_py(por_tela: Dict[str, str]) -> str:
    """regras.py do aplicativo: as regras `código gerado` de cada tela, cada uma no seu módulo."""
    partes = ['"""Regras `código gerado` dos casos de uso (escritas pelo modelo, conferidas pelo LangNet)."""',
              "from fastapi import Depends, HTTPException", "", "_ROTAS = []", ""]
    for sid, py in por_tela.items():
        if not (py or "").strip():
            continue
        nome = re.sub(r"\W", "_", sid)
        corpo = py.replace("def rotas(app, ctx)", f"def rotas_{nome}(app, ctx)", 1)
        partes += [f"# ── {sid} ──", corpo.rstrip(), f"_ROTAS.append(rotas_{nome})", ""]
    partes += ["", "def instalar(app, **ctx):",
               "    ctx.setdefault('Depends', Depends); ctx.setdefault('HTTPException', HTTPException)",
               "    for r in _ROTAS:",
               "        r(app, ctx)", ""]
    return "\n".join(partes)


# ── casca do aplicativo: menu, login, Assistente ─────────────────────────────

def _eh_login(screen: Dict) -> bool:
    t = f"{screen.get('id')} {screen.get('name')}".lower()
    return bool(re.search(r"login|entrar|autentica", t))


def app_jsx(telas: List[Dict], project_name: str) -> str:
    """telas: [{comp, id, nome, modulo, agente(bool), login(bool)}]"""
    imports = "\n".join(f'import {t["comp"]} from "./screens/{t["comp"]}";' for t in telas)
    lista = ",\n  ".join(
        json.dumps({"id": t["id"], "nome": t["nome"], "modulo": t.get("modulo") or "Telas",
                    "agente": bool(t.get("agente")), "login": bool(t.get("login"))}, ensure_ascii=False)[:-1]
        + f', "Comp": {t["comp"]}}}' for t in telas)
    nome = json.dumps(project_name or "Aplicativo", ensure_ascii=False)
    return f"""// Aplicativo gerado pelo LangNet — telas = desenho aprovado no protótipo
import React, {{ useEffect, useState }} from "react";
import * as lnx from "./lnx";
import Assistente from "./Assistente";
{imports}

const TELAS = [
  {lista}
];
const NOME = {nome};

export default function App() {{
  const sessao = lnx.sessao();
  const login = TELAS.find((t) => t.login);
  window.LNX_TEM_LOGIN = !!login;
  const inicial = TELAS.find((t) => !t.login) || TELAS[0];
  const [atual, setAtual] = useState(() => {{ try {{ return localStorage.getItem("lnx.tela") || inicial.id; }} catch (e) {{ return inicial.id; }} }});
  const [assistente, setAssistente] = useState(false);
  useEffect(() => {{
    const ir = (ev) => {{ setAtual(ev.detail); try {{ localStorage.setItem("lnx.tela", ev.detail); }} catch (e) {{}} }};
    window.addEventListener("lnx:navegar", ir);
    return () => window.removeEventListener("lnx:navegar", ir);
  }}, []);
  if (!sessao && login) {{ const L = login.Comp; return <L />; }}
  const tela = TELAS.find((t) => t.id === atual && !t.login) || inicial;
  const grupos = {{}};
  TELAS.filter((t) => !t.login).forEach((t) => {{ (grupos[t.modulo] = grupos[t.modulo] || []).push(t); }});
  const C = tela.Comp;
  return (
    <div className="flex min-h-screen bg-slate-100">
      <aside className="w-64 shrink-0 bg-slate-900 text-slate-300 flex flex-col">
        <div className="px-5 py-4 border-b border-slate-800">
          <div className="text-white font-semibold">{{NOME}}</div>
          {{sessao && sessao.usuario && <div className="text-[11px] text-slate-400 mt-0.5">{{sessao.usuario.nome}} · {{sessao.usuario.papel}}</div>}}
        </div>
        <button onClick={{() => setAssistente(true)}} className="mx-3 mt-3 mb-1 px-3 py-2 rounded-lg bg-violet-600 text-white text-sm font-medium text-left hover:bg-violet-700">✦ Assistente</button>
        <nav className="flex-1 overflow-y-auto py-2">
          {{Object.entries(grupos).map(([g, itens]) => (
            <div key={{g}}>
              <div className="px-5 pt-3 pb-1 text-[10px] uppercase tracking-wider text-slate-500">{{g}}</div>
              {{itens.map((t) => (
                <a key={{t.id}} href="#" onClick={{(e) => {{ e.preventDefault(); lnx.navegar(t.id); }}}}
                   className={{"block px-5 py-2 text-sm " + (t.id === tela.id ? "bg-indigo-600 text-white font-medium" : "hover:bg-slate-800 hover:text-white")}}>
                  {{t.nome}}{{t.agente ? <span className="ml-1 text-violet-300" title="tela com agente de IA">✦</span> : null}}
                </a>
              ))}}
            </div>
          ))}}
        </nav>
        {{sessao && <button onClick={{lnx.sair}} className="m-3 px-3 py-2 rounded-lg border border-slate-700 text-xs text-slate-400 hover:text-white">Sair</button>}}
      </aside>
      <main className="flex-1 min-w-0"><C key={{tela.id}} /></main>
      {{assistente && <Assistente fechar={{() => setAssistente(false)}} />}}
    </div>
  );
}}
"""


ASSISTENTE_JSX = r"""// Assistente único (Modo B): aciona os MESMOS agentes das telas, em conversa (gerado pelo LangNet)
import React, { useEffect, useState } from "react";
import * as lnx from "./lnx";
import { AGENTES } from "./agentes";

export default function Assistente({ fechar }) {
  const [msgs, setMsgs] = useState([{ de: "sis", texto: "O que você quer fazer? Escolha uma das ações dos agentes do sistema." }]);
  const [fluxo, setFluxo] = useState(null);
  const [opcoes, setOpcoes] = useState([]);
  const [ocupado, setOcupado] = useState(false);
  const diz = (de, texto, cartao) => setMsgs((m) => [...m, { de, texto, cartao }]);

  async function escolher(a) {
    setFluxo(a); diz("eu", a.rotulo);
    if (a.contexto && a.contexto.tabela) {
      const atual = lnx.contexto(a.contexto.campo);
      const r = await lnx.api.get(`/api/dados/${a.contexto.tabela}?limite=50`);
      setOpcoes(r.rows || []);
      diz("sis", atual ? `Uso o registro aberto (${atual}) ou escolha outro:` : (a.contexto.pergunta || "Para qual registro?"));
    } else { rodar(a, {}); }
  }
  async function rodar(a, entradas) {
    setOcupado(true); setOpcoes([]);
    diz("sis", "Executando: " + (a.passos || []).join(" → "));
    try {
      const r = await lnx.agente(a.tarefa, entradas);
      if (r && r.recusado) diz("sis", "O agente não pôde decidir: " + (r.motivo || r.justificativa || "faltam dados."), r);
      else diz("sis", "Concluído.", r);
      diz("sis", "Abrir a tela para conferir ou continuar?", null);
    } catch (e) { diz("sis", "Erro: " + (e.message || e)); }
    setOcupado(false);
  }
  return (
    <div className="fixed inset-y-0 right-0 w-[420px] bg-white border-l border-slate-200 shadow-2xl flex flex-col z-50">
      <div className="px-4 py-3 border-b flex items-center justify-between"><b>✦ Assistente</b><button onClick={fechar} className="text-slate-500">✕</button></div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 text-sm">
        {msgs.map((m, i) => (
          <div key={i} className={m.de === "eu" ? "text-right" : ""}>
            <div className={"inline-block px-3 py-2 rounded-xl " + (m.de === "eu" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-800")}>{m.texto}</div>
            {m.cartao && typeof m.cartao === "object" && (
              <div className="mt-2 rounded-xl border border-violet-200 bg-violet-50 p-3 text-left">
                {Object.entries(m.cartao).filter(([k]) => !k.startsWith("_") && k !== "recusado").map(([k, v]) => (
                  <div key={k} className="py-0.5"><span className="text-xs text-slate-500">{k.replace(/_/g, " ")}: </span>
                    <span className={/justificativa|motivo/.test(k) ? "text-slate-800" : "font-medium"}>{typeof v === "object" ? JSON.stringify(v) : String(v)}</span></div>
                ))}
              </div>
            )}
          </div>
        ))}
        {!fluxo && AGENTES.map((a) => (
          <button key={a.tarefa} onClick={() => escolher(a)} className="block w-full text-left px-3 py-2 rounded-lg border border-violet-200 hover:bg-violet-50">
            <div className="font-medium">✦ {a.rotulo}</div><div className="text-xs text-slate-500">{a.uc} · tela {a.tela_nome}</div>
          </button>
        ))}
        {opcoes.length > 0 && opcoes.map((o) => (
          <button key={o.id} disabled={ocupado} onClick={() => { lnx.contexto(fluxo.contexto.campo, o.id); diz("eu", o[fluxo.contexto.rotulo] || o.id); rodar(fluxo, { [fluxo.contexto.campo]: o.id }); }}
                  className="block w-full text-left px-3 py-2 rounded-lg border border-slate-200 hover:bg-slate-50">{o[fluxo.contexto.rotulo] || o.id}</button>
        ))}
        {fluxo && !ocupado && (
          <div className="flex gap-2 pt-2">
            <button onClick={() => { lnx.navegar(fluxo.tela); fechar(); }} className="px-3 py-1.5 rounded-lg border text-xs">Abrir a tela</button>
            <button onClick={() => { setFluxo(null); setOpcoes([]); }} className="px-3 py-1.5 rounded-lg border text-xs">Outra ação</button>
          </div>
        )}
      </div>
    </div>
  );
}
"""


def agentes_js(itens: List[Dict]) -> str:
    return "// Ações de agente do sistema, para o Assistente (gerado pelo LangNet)\nexport const AGENTES = " + \
        json.dumps(itens, ensure_ascii=False, indent=1) + ";\n"


INDEX_HTML = """<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITULO__</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
__RECURSOS__
<style>body{font-family:'Inter',sans-serif}.lnx-tela>div.flex.min-h-screen{min-height:auto}
.lnx-aviso{margin:12px 32px;padding:10px 14px;border-radius:10px;background:#fef2f2;border:1px solid #fecaca;color:#991b1b;font-size:14px}
.lnx-aviso[data-tipo=ok]{background:#ecfdf5;border-color:#a7f3d0;color:#065f46}
[data-mensagem]{display:none}[data-estado=executando]{opacity:.75}
[data-agente][data-estado]::before{content:"✦ " attr(data-estado);display:inline-block;margin-bottom:6px;font:600 11px Inter,sans-serif;color:#6d28d9}</style>
</head><body><div id="root"></div></body></html>
"""


def index_html(titulo: str, recursos: List[str]) -> str:
    tags = []
    for r in sorted(set(recursos)):
        tags.append(f'<link rel="stylesheet" href="{r}">' if r.endswith(".css") else f'<script src="{r}"></script>')
    return INDEX_HTML.replace("__TITULO__", titulo or "Aplicativo").replace("__RECURSOS__", "\n".join(tags))


# ── montagem do aplicativo ───────────────────────────────────────────────────

def _pascal(s: str) -> str:
    p = re.sub(r"[^0-9A-Za-z]+", " ", s or "Tela").title().replace(" ", "")
    return ("Tela" + p) if not p or p[0].isdigit() else p


def _chamar_modelo(pedido: str) -> str:
    from agents.langnetagents import _direct_llm_complete
    return _direct_llm_complete(pedido)


def _ler_json(txt: str) -> Dict:
    from prompts.generate_ui_spec import extract_json_object
    try:
        return json.loads(extract_json_object(txt or "") or "{}")
    except Exception:
        return {}


def emitir_aplicativo(ui_spec: Dict, spec_doc: str, ats_doc: str, schema_sql: str, project_name: str,
                      chamar=None, paralelo: int = 4, ajustes: Optional[List[Dict]] = None) -> Tuple[List[Dict], Dict]:
    """Arquivos do aplicativo (frontend + backend) a partir das telas APROVADAS.
    Devolve (arquivos, relatório). O relatório nomeia cada pendência — nada passa calado."""
    import os
    from concurrent.futures import ThreadPoolExecutor
    from prompts.generate_ui_spec import find_uc_block
    from agents.langnettarefas import _tarefas
    from agents.langnetappapi import emitir_backend_main, meta_do_modelo
    chamar = chamar or _chamar_modelo
    meta = meta_do_modelo(schema_sql)
    tabelas = meta["tabelas"]
    tarefas = _tarefas(ats_doc or "")
    tarefa_do_uc: Dict[str, Dict] = {}
    for t in tarefas:
        for u in t.get("uc_related") or []:
            tarefa_do_uc.setdefault(u, t)
    telas = [s for s in (ui_spec.get("screens") or []) if (s.get("mockup_html") or "").strip()]
    nomes, usados = {}, set()
    for s in telas:
        n = _pascal(s.get("id") or s.get("name"))
        while n in usados:
            n += "2"
        usados.add(n); nomes[s.get("id")] = n

    def uma(s):
        ucs = s.get("uc") or []
        raw = ""
        for u in ucs:
            b = find_uc_block(spec_doc or "", u)
            if b:
                raw = b["uc"].get("raw", ""); break
        tarefa = next((tarefa_do_uc[u] for u in ucs if u in tarefa_do_uc), None)
        pedido = pedido_controlador(s, raw, tarefa, tabelas, [t.get("id") for t in telas])
        meus = [a["pedido"] for a in (ajustes or []) if a.get("tela_id") == s.get("id")]
        if meus:
            # ajustes que o usuário pediu pela conversa do código: valem em toda geração
            pedido += "\n\n## AJUSTES PEDIDOS PELO USUÁRIO (obrigatórios, nesta ordem)\n- " + "\n- ".join(meus)
        melhor, probs = {"controlador_js": "", "regras_py": ""}, ["sem resposta do modelo"]
        obs = ""
        for _ in range(2):
            try:
                r = _ler_json(chamar(pedido + obs))
            except Exception as e:
                r = {}; probs = [f"falha ao chamar o modelo: {e}"]
            js, py = r.get("controlador_js") or "", r.get("regras_py") or ""
            if js:
                p = conferir_controlador(js, py, s, tarefa.get("name") if tarefa else None, tabelas,
                                         [t.get("id") for t in telas])
                if len(p) < len(probs) or not melhor["controlador_js"]:
                    melhor, probs = {"controlador_js": js, "regras_py": py}, p
                if not p:
                    break
            obs = ("\n\n⚠️ Sua resposta anterior foi REPROVADA pela conferência:\n- " + "\n- ".join(probs[:20])
                   + "\nCorrija e devolva o JSON completo.")
        return s, melhor, probs, tarefa

    with ThreadPoolExecutor(max_workers=max(1, paralelo)) as ex:
        resultados = list(ex.map(uma, telas))

    arquivos: List[Dict] = []
    def add(caminho, conteudo, ling="javascript"):
        arquivos.append({"path": caminho, "content": conteudo, "language": ling})

    rel = {"telas": len(telas), "aprovadas": 0, "pendencias": {}, "controladores_vazios": []}
    regras_por_tela, telas_app, agentes, recursos = {}, [], [], []
    for s, r, probs, tarefa in resultados:
        comp = nomes[s.get("id")]
        js = r["controlador_js"] or ("export default function montar(raiz, lnx) {\n"
                                     "  lnx.mensagem(raiz, \"Esta tela ainda não tem comportamento gerado.\", \"erro\");\n}\n")
        if not r["controlador_js"]:
            rel["controladores_vazios"].append(s.get("id"))
        add(f"frontend/src/controladores/{comp}.js", "// Controlador da tela (escrito pelo modelo, conferido pelo LangNet)\n" + js)
        add(f"frontend/src/screens/{comp}.jsx", componente_jsx(comp, s))
        if r["regras_py"] and not any("regras" in p for p in probs):
            regras_por_tela[s.get("id")] = r["regras_py"]
        if probs:
            rel["pendencias"][s.get("id")] = probs
        else:
            rel["aprovadas"] += 1
        recursos += recursos_da_tela(s.get("mockup_html"))
        tem_agente = bool(s.get("agentes"))
        telas_app.append({"comp": comp, "id": s.get("id"), "nome": s.get("name"), "modulo": s.get("module") or s.get("group") or "Telas",
                          "agente": tem_agente, "login": _eh_login(s)})
        if tem_agente and tarefa:
            ctx_campo = next((c for c, o in (tarefa.get("origens") or {}).items() if str(o).lower().startswith("contexto")), None)
            ref = None
            for _t, fk in meta["fks"].items():
                if ctx_campo in fk:
                    ref = fk[ctx_campo]; break
            from agents.langnetappapi import _MOLDE  # noqa (garante import do módulo)
            rot = None
            if ref:
                cols = tabelas.get(ref, [])
                rot = next((c for c in ("nome", "titulo", "codigo", "numero_prontuario", "descricao") if c in cols), "id")
            agentes.append({"tarefa": tarefa["name"], "rotulo": (s.get("agentes") or [{}])[0].get("rotulo") or tarefa.get("title"),
                            "uc": ", ".join(s.get("uc") or []), "tela": s.get("id"), "tela_nome": s.get("name"),
                            "passos": [b.get("passo") for b in s.get("agentes") or []],
                            "contexto": {"campo": ctx_campo, "tabela": ref, "rotulo": rot,
                                         "pergunta": f"Para qual {ref.replace('_', ' ')}?" if ref else None} if ctx_campo else None})
    # um agente por tarefa no Assistente
    vistos, ag_unicos = set(), []
    for a in agentes:
        if a["tarefa"] not in vistos:
            vistos.add(a["tarefa"]); ag_unicos.append(a)

    add("frontend/src/lnx.js", LNX_JS)
    add("frontend/src/App.jsx", app_jsx(telas_app, project_name))
    add("frontend/src/Assistente.jsx", ASSISTENTE_JSX)
    add("frontend/src/agentes.js", agentes_js(ag_unicos))
    add("frontend/public/index.html", index_html(project_name, recursos), "html")
    origens = {t["name"]: t.get("origens") or {} for t in tarefas}
    add("backend/main.py", emitir_backend_main(schema_sql, project_name, True, origens), "python")
    if regras_por_tela:
        add("backend/regras.py", montar_regras_py(regras_por_tela), "python")
    add("backend/requirements.txt", "fastapi>=0.110\nuvicorn>=0.27\npyjwt>=2.8\nbcrypt>=4.0\nmysql-connector-python>=8.0\n", "text")
    rel["agentes_no_assistente"] = len(ag_unicos)
    rel["regras"] = len(regras_por_tela)
    rel["reprovado"] = bool(rel["pendencias"]) or bool(rel["controladores_vazios"])
    return arquivos, rel


# o que sai do aplicativo no modo novo: console Admin/Petri e as telas do molde antigo
ARQUIVOS_QUE_SAEM = ("frontend/src/screens/", "frontend/src/components/", "frontend/src/petri-engine/",
                     "frontend/src/hooks/usePetriNetExecution", "backend/project.json")
ARQUIVOS_QUE_FICAM = ("frontend/src/screens/wsClient.js",)

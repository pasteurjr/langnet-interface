"""Etapa PROTÓTIPO — Fase 1 e 2.

Emite um protótipo React NAVEGÁVEL a partir da Especificação de Interface aprovada, com dados
fictícios derivados do Modelo de Dados.

Princípio (do plano): **o protótipo é o aplicativo com a fonte de dados trocada.** As telas são
emitidas pelo MESMO emissor que gera o aplicativo; a única diferença é o módulo de acesso a
dados — no aplicativo fala com o servidor de agentes, aqui responde de uma semente fictícia.

Isso mata a divergência que produziu o pior defeito do projeto: a Especificação de Interface
declarava painel com indicadores e gráficos, o mockup mostrava, e o aplicativo nascia vazio
porque o emissor descartava calado o que não sabia desenhar. Com emissor único, o que falta no
aplicativo falta também no protótipo — e aparece na hora de aprovar a etapa.
"""
from typing import Any, Dict, List, Optional
import json
import re


# ── Semente de dados fictícios, derivada do Modelo de Dados ────────────────────

_EXEMPLOS_POR_NOME = [
    (r"(?i)nome|paciente", ["Ana Ribeiro", "Carlos Menezes", "Beatriz Lima", "João Álvaro"]),
    (r"(?i)email", ["ana.ribeiro@hospital.br", "carlos.menezes@hospital.br"]),
    (r"(?i)cpf|documento", ["123.456.789-00", "987.654.321-00"]),
    (r"(?i)telefone|fone", ["(31) 98888-1234", "(31) 97777-4321"]),
    (r"(?i)justificativ|descricao|descrição|observ", ["Registro gerado para demonstração da tela."]),
    (r"(?i)ip_origem|endereco_ip", ["10.0.4.21", "10.0.4.87"]),
]


def _valor_exemplo(coluna: str, tipo: str, dominio: Optional[List[str]], i: int):
    """Valor fictício plausível para uma coluna, a partir do TIPO e do NOME."""
    t = (tipo or "").lower()
    if dominio:
        return dominio[i % len(dominio)]
    for padrao, valores in _EXEMPLOS_POR_NOME:
        if re.search(padrao, coluna or ""):
            return valores[i % len(valores)]
    # TINYINT(1) é o booleano do MySQL — precisa vir antes do teste de inteiro, senão a
    # semente gera 10, 17… e a tela mostra "taxa de multirresistência: 0".
    if "bool" in t or t.replace(" ", "").startswith("tinyint(1)"):
        return i % 2 == 0
    if "int" in t or "decimal" in t or "float" in t or "double" in t or "numeric" in t:
        base = 10 + i * 7
        if re.search(r"(?i)idade", coluna or ""):
            return 34 + (i * 11) % 50
        if re.search(r"(?i)escore|score|taxa|percent", coluna or ""):
            return round(0.12 + (i % 7) * 0.11, 4)
        return base
    if "date" in t or "time" in t:
        dia = 1 + (i % 27)
        return f"2026-09-{dia:02d}" + (" 08:30:00" if "time" in t else "")
    if "json" in t:
        return {"oxacilina": "R", "vancomicina": "S"}
    return f"{(coluna or 'valor').replace('_', ' ').capitalize()} {i + 1}"


def semente_do_modelo(schema_sql: str, linhas_por_tabela: int = 6) -> Dict[str, List[dict]]:
    """Lê o DDL aprovado e monta linhas fictícias por tabela, com as chaves estrangeiras
    apontando para linhas que existem — senão o protótipo mostra tabela vazia onde deveria
    haver relacionamento."""
    if not schema_sql:
        return {}
    tabelas: Dict[str, List[dict]] = {}
    colunas_por_tabela: Dict[str, List[tuple]] = {}
    fks: Dict[str, Dict[str, str]] = {}
    # O corpo do CREATE TABLE termina no parêntese que FECHA o de abertura — não no primeiro
    # ")" nem antes de ENGINE: o gerador emite `) COMMENT='...'` e a leitura por regex simples
    # não achava tabela nenhuma.
    blocos = []
    for m in re.finditer(r"(?is)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\(", schema_sql):
        tabela = m.group(1)
        i, nivel = m.end(), 1
        while i < len(schema_sql) and nivel:
            if schema_sql[i] == "(":
                nivel += 1
            elif schema_sql[i] == ")":
                nivel -= 1
            i += 1
        blocos.append((tabela, schema_sql[m.end():i - 1]))
    for tabela, corpo in blocos:
        cols: List[tuple] = []
        for linha in corpo.split("\n"):
            l = linha.strip().rstrip(",")
            mf = re.search(r"(?i)FOREIGN\s+KEY\s*\(`?(\w+)`?\)\s*REFERENCES\s+`?(\w+)`?", l)
            if mf:
                fks.setdefault(tabela, {})[mf.group(1)] = mf.group(2)
                continue
            if re.match(r"(?i)^(PRIMARY|UNIQUE|KEY|INDEX|CONSTRAINT|FOREIGN)", l):
                continue
            mc = re.match(r"^`?(\w+)`?\s+([A-Za-z]+(?:\([^)]*\))?)", l)
            if not mc:
                continue
            nome, tipo = mc.group(1), mc.group(2)
            dominio = None
            me = re.match(r"(?i)^enum\((.*)\)$", tipo)
            if me:
                dominio = [x.strip().strip("'\"") for x in me.group(1).split(",")]
            cols.append((nome, tipo, dominio))
        colunas_por_tabela[tabela] = cols
    for tabela, cols in colunas_por_tabela.items():
        linhas = []
        for i in range(linhas_por_tabela):
            linha = {}
            for nome, tipo, dominio in cols:
                if nome == "id":
                    linha["id"] = f"{tabela[:3].upper()}-{i + 1:03d}"
                elif nome.endswith("_hash"):
                    linha[nome] = "(protegido)"
                else:
                    linha[nome] = _valor_exemplo(nome, tipo, dominio, i)
            linhas.append(linha)
        tabelas[tabela] = linhas
    # chaves estrangeiras apontam para linhas que existem
    for tabela, mapa in fks.items():
        for coluna, alvo in mapa.items():
            alvo_linhas = tabelas.get(alvo) or []
            if not alvo_linhas:
                continue
            for i, linha in enumerate(tabelas.get(tabela, [])):
                linha[coluna] = alvo_linhas[i % len(alvo_linhas)]["id"]
    return tabelas


def _resposta_por_task(tasks_yaml: str) -> Dict[str, List[str]]:
    """Campos que cada tarefa devolve (do output_schema do tasks.yaml), para o provedor
    fictício responder com as MESMAS chaves que o aplicativo real responderia."""
    saidas: Dict[str, List[str]] = {}
    try:
        import yaml as _yaml
        tarefas = _yaml.safe_load(tasks_yaml) or {}
    except Exception:
        return saidas
    for nome, cfg in (tarefas.items() if isinstance(tarefas, dict) else []):
        if not isinstance(cfg, dict):
            continue
        esquema = cfg.get("output_schema") or {}
        campos = list((esquema.get("properties") or {}).keys()) if isinstance(esquema, dict) else []
        if not campos and isinstance(esquema, dict):
            campos = [k for k in esquema.keys() if k not in ("type", "required", "properties")]
        if campos:
            saidas[nome] = campos
    return saidas


def emitir_provedor_ficticio(semente: Dict[str, List[dict]], saidas: Dict[str, List[str]]) -> str:
    """Módulo com a MESMA assinatura do cliente do servidor de agentes (`runTask`), respondendo
    da semente. É o único arquivo que difere entre o protótipo e o aplicativo."""
    return (
        '/**\n'
        ' * Provedor de dados do PROTÓTIPO — mesma assinatura do cliente do servidor de agentes.\n'
        ' *\n'
        ' * O aplicativo real fala por WebSocket com o servidor de agentes; aqui as respostas vêm\n'
        ' * da semente fictícia, derivada do Modelo de Dados aprovado. As TELAS são idênticas nos\n'
        ' * dois casos: só este arquivo muda. Nenhum valor daqui pode chegar ao aplicativo.\n'
        ' */\n'
        'export const SEMENTE = ' + json.dumps(semente, ensure_ascii=False, indent=2) + ';\n\n'
        'export const SAIDAS = ' + json.dumps(saidas, ensure_ascii=False, indent=2) + ';\n\n'
        'const atraso = (ms) => new Promise((r) => setTimeout(r, ms));\n\n'
        'function tabelaDe(nome) {\n'
        '  const chaves = Object.keys(SEMENTE);\n'
        '  const alvo = String(nome || "").toLowerCase();\n'
        '  return chaves.find((t) => alvo.includes(t)) || chaves.find((t) => t.includes(alvo.split("_").pop() || "")) || "";\n'
        '}\n\n'
        'export function runTask(taskName, inputData) {\n'
        '  const nome = String(taskName || "");\n'
        '  return atraso(350).then(() => {\n'
        '    const tabela = tabelaDe(nome);\n'
        '    const linhas = (tabela && SEMENTE[tabela]) || [];\n'
        '    // Mesmo formato do adapter real: {rows, total}. O protótipo tem de responder no\n'
        '    // contrato do aplicativo, senão a tela mostra vazio onde teria dados.\n'
        '    if (/^listar_/.test(nome)) return { rows: linhas, total: linhas.length };\n'
        '    if (/^(criar|atualizar)_/.test(nome)) return { status: "sucesso", ...(inputData || {}), id: (linhas[0] || {}).id || "NOV-001" };\n'
        '    if (/^excluir_/.test(nome)) return { status: "sucesso" };\n'
        '    if (/^obter_/.test(nome)) return linhas[0] || {};\n'
        '    // Tarefa de negócio: devolve os campos que o contrato de saída declara, preenchidos\n'
        '    // com a semente — para a tela mostrar o que mostraria em uso real.\n'
        '    const campos = SAIDAS[nome] || [];\n'
        '    const base = linhas[0] || {};\n'
        '    const saida = { status: "sucesso" };\n'
        '    campos.forEach((c, i) => {\n'
        '      if (base[c] !== undefined) { saida[c] = base[c]; return; }\n'
        '      const daSemente = Object.values(SEMENTE).flat().find((l) => l && l[c] !== undefined);\n'
        '      saida[c] = daSemente ? daSemente[c] : `${c.replace(/_/g, " ")} (exemplo)`;\n'
        '    });\n'
        '    if (!campos.length) {\n'
        '      // Tarefa sem contrato de saída declarado (ex.: painel): devolve agregados da\n'
        '      // semente, para os indicadores e gráficos da tela terem o que mostrar.\n'
        '      Object.assign(saida, base);\n'
        '      Object.entries(SEMENTE).forEach(([t, ls]) => { saida[`total_${t}`] = ls.length; });\n'
        '      const micro = SEMENTE.microbiologias || [];\n'
        '      if (micro.length) {\n'
        '        const mdr = micro.filter((l) => l.multirresistente === true || l.multirresistente === 1).length;\n'
        '        saida.taxa_mdr = Math.round((mdr * 1000) / micro.length) / 10;\n'
        '        saida.distribuicao_microrganismos = micro.map((l) => ({ microrganismo: l.microrganismo, total: 1 }));\n'
        '      }\n'
        '      const esc = SEMENTE.escores_risco || [];\n'
        '      if (esc.length) saida.media_escore = esc[0].valor_escore;\n'
        '      const casos = SEMENTE.casos || [];\n'
        '      if (casos.length) saida.casos_icsac = casos.length;\n'
        '    }\n'
        '    if (linhas.length > 1) saida.itens = linhas;\n'
        '    return saida;\n'
        '  });\n'
        '}\n\n'
        '// Mesma superfície do cliente real: as telas importam os dois nomes.\n'
        'export function splitList(v) {\n'
        '  if (Array.isArray(v)) return v;\n'
        '  if (!v) return [];\n'
        '  return String(v).split(",").map((x) => x.trim()).filter(Boolean);\n'
        '}\n\n'
        'export default { runTask, splitList, SEMENTE, SAIDAS };\n'
    )


# ── Projeto React do protótipo ────────────────────────────────────────────────

def gerar_prototipo(ui_spec: dict, schema_sql: str, tasks_yaml: str,
                    project_name: str = "Protótipo") -> List[Dict[str, str]]:
    """Monta o projeto React do protótipo: MESMAS telas do aplicativo, provedor fictício no
    lugar do cliente do servidor de agentes.

    Devolve a lista de arquivos [{path, content}] — a etapa grava/serve como preferir.
    """
    from agents.langnetagents import _generate_business_screens, _parse_task_input_fields

    arquivos = _generate_business_screens(ui_spec, 5002, project_name, tasks_yaml,
                                          schema_sql=schema_sql)
    semente = semente_do_modelo(schema_sql)
    saidas = _resposta_por_task(tasks_yaml)
    provedor = emitir_provedor_ficticio(semente, saidas)

    saida: List[Dict[str, str]] = []
    trocou = False
    for arq in arquivos:
        caminho = arq.get("path") if isinstance(arq, dict) else arq[0]
        conteudo = arq.get("content") if isinstance(arq, dict) else arq[1]
        if caminho.endswith("screens/wsClient.js"):
            conteudo = provedor          # <- a ÚNICA diferença para o aplicativo real
            trocou = True
        saida.append({"path": caminho, "content": conteudo})
    if not trocou:
        saida.append({"path": "frontend/src/screens/wsClient.js", "content": provedor})

    # O executor da Rede de Petri é peça do APLICATIVO (administração), não do protótipo de
    # interface. Sem removê-lo, o protótipo nem compila: o arquivo dele não é emitido aqui.
    for arq in saida:
        if arq["path"].endswith("frontend/src/App.jsx"):
            c = arq["content"]
            c = re.sub(r'(?m)^import MainExecutor from "\./components/MainExecutor";\n', "", c)
            c = re.sub(r'\{view === "admin" && \([^\n]*\)\}',
                       '{view === "admin" && (\n'
                       '          <p className="text-slate-400">Administração não faz parte do '
                       'protótipo de interface.</p>\n        )}', c)
            arq["content"] = c

    saida.append({"path": "frontend/package.json", "content": json.dumps({
        "name": "prototipo", "version": "1.0.0", "private": True,
        "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0",
                         "react-router-dom": "^6.20.0", "react-scripts": "5.0.1",
                         "recharts": "^2.10.0"},
        "scripts": {"start": "react-scripts start", "build": "react-scripts build"},
        # Sem isto o compilador reclama das regras de hooks que as telas trazem em comentário
        # e o protótipo não compila.
        "eslintConfig": {"extends": ["react-app"]},
        "browserslist": {"production": [">0.2%"], "development": ["last 1 chrome version"]},
    }, ensure_ascii=False, indent=2)})
    saida.append({"path": "frontend/public/index.html", "content":
        '<!doctype html><html lang="pt-br"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{project_name} — protótipo</title>'
        '<script src="https://cdn.tailwindcss.com"></script>'
        '</head><body><div id="root"></div></body></html>'})
    # PONTE COM A ETAPA (Fase 4): o protótipo avisa a página qual tela está aberta e, no modo
    # de apontar, qual componente o usuário clicou. É o que permite refinar conversando com o
    # agente SOBRE a tela aberta, em vez de descrever de memória.
    saida.append({"path": "frontend/src/ponte.js", "content":
        '/**\n'
        ' * Ponte entre o protótipo e a etapa que o embute.\n'
        ' *\n'
        ' * Envia à página: a tela aberta e, quando o modo de apontar está ligado, o componente\n'
        ' * clicado (rótulo e campo). Recebe da página: ligar/desligar o modo de apontar.\n'
        ' */\n'
        'const alvo = () => (window.parent && window.parent !== window ? window.parent : null);\n'
        'let apontando = false;\n\n'
        'function avisar(tipo, dados) {\n'
        '  const p = alvo();\n'
        '  if (p) p.postMessage({ origem: "prototipo-langnet", tipo, ...dados }, "*");\n'
        '}\n\n'
        'function telaAberta() {\n'
        '  const h = document.querySelector("main h1, main h2");\n'
        '  const raiz = document.querySelector("[data-uc]");\n'
        '  return { tela: (h && h.textContent.trim()) || "", uc: (raiz && raiz.getAttribute("data-uc")) || "" };\n'
        '}\n\n'
        'function descreveComponente(el) {\n'
        '  let n = el, campo = "", rotulo = "", tipo = "";\n'
        '  for (let i = 0; i < 6 && n; i++) {\n'
        '    if (!campo && (n.name || n.id)) campo = n.name || n.id;\n'
        '    if (!tipo && /^(INPUT|SELECT|TEXTAREA|TABLE|BUTTON|OL|UL)$/.test(n.tagName)) tipo = n.tagName.toLowerCase();\n'
        '    const lab = n.previousElementSibling;\n'
        '    if (!rotulo && lab && /^(LABEL|SPAN|DIV|B)$/.test(lab.tagName) && lab.textContent.trim().length < 60)\n'
        '      rotulo = lab.textContent.trim();\n'
        '    n = n.parentElement;\n'
        '  }\n'
        '  if (!rotulo) rotulo = (el.textContent || "").trim().slice(0, 60);\n'
        '  return { campo, rotulo, tipoElemento: tipo };\n'
        '}\n\n'
        'window.addEventListener("message", (ev) => {\n'
        '  const m = ev.data || {};\n'
        '  if (m.origem !== "etapa-langnet") return;\n'
        '  if (m.tipo === "apontar") {\n'
        '    apontando = !!m.ligado;\n'
        '    document.body.style.cursor = apontando ? "crosshair" : "";\n'
        '  }\n'
        '  if (m.tipo === "qual-tela") avisar("tela", telaAberta());\n'
        '});\n\n'
        'document.addEventListener("click", (ev) => {\n'
        '  if (apontando) {\n'
        '    ev.preventDefault(); ev.stopPropagation();\n'
        '    avisar("componente", { ...telaAberta(), ...descreveComponente(ev.target) });\n'
        '    return;\n'
        '  }\n'
        '  setTimeout(() => avisar("tela", telaAberta()), 250);\n'
        '}, true);\n\n'
        'setTimeout(() => avisar("tela", telaAberta()), 800);\n'})

    saida.append({"path": "frontend/src/index.js", "content":
        'import React from "react";\n'
        'import { createRoot } from "react-dom/client";\n'
        'import App from "./App";\n'
        'import "./ponte";   // avisa a etapa qual tela está aberta e o componente apontado\n\n'
        'createRoot(document.getElementById("root")).render(<App />);\n'})
    saida.append({"path": "LEIA-ME.md", "content":
        f"# {project_name} — protótipo\n\n"
        "Protótipo navegável gerado da Especificação de Interface aprovada.\n\n"
        "As telas são **as mesmas** que o aplicativo terá; a única diferença é o arquivo\n"
        "`frontend/src/screens/wsClient.js`, que aqui responde de uma semente fictícia\n"
        "derivada do Modelo de Dados, e no aplicativo fala com o servidor de agentes.\n\n"
        "Nenhum valor da semente pode chegar ao aplicativo gerado.\n\n"
        "Para rodar: `cd frontend && npm install && npm start`.\n"})
    return saida


def resumo_prototipo(arquivos: List[Dict[str, str]]) -> dict:
    telas = [a["path"].rsplit("/", 1)[-1][:-4] for a in arquivos
             if "/screens/" in a["path"] and a["path"].endswith(".jsx")]
    return {"arquivos": len(arquivos), "telas": len(telas), "nomes": sorted(telas)}


# ── Montagem: grava, empacota e deixa pronto para servir ──────────────────────

import os
import shutil
import subprocess
from pathlib import Path

RAIZ_PROTOTIPOS = Path(os.environ.get("LANGNET_PROTOTIPOS", "/tmp/langnet-prototipos"))
CACHE_FRONTEND = Path(os.environ.get("LANGNET_FRONTEND_CACHE",
                                     str(Path.home() / ".langnet-cache" / "frontend")))


def _achar_esbuild() -> Optional[str]:
    """esbuild empacota o protótipo em milissegundos, sem instalar nada e sem servidor de
    desenvolvimento — que aqui não funciona (o limite de observação de arquivos do sistema já
    está esgotado pelos aplicativos implantados)."""
    candidatos = [
        Path(__file__).resolve().parents[2] / "node_modules" / ".bin" / "esbuild",
        CACHE_FRONTEND / "node_modules" / ".bin" / "esbuild",
    ]
    candidatos += sorted(Path.home().glob(".npm/_npx/*/node_modules/.bin/esbuild"))
    for c in candidatos:
        if c and Path(c).exists():
            return str(c)
    return shutil.which("esbuild")


def montar_prototipo(arquivos: List[Dict[str, str]], destino: Path,
                     project_name: str = "Protótipo") -> dict:
    """Grava os arquivos, empacota e deixa `destino` pronto para ser servido estaticamente.

    Devolve {ok, erro, arquivos, telas, bytes}. As dependências (React, Recharts) vêm do cache
    que o motor de implantação já mantém — o protótipo não instala nada.
    """
    destino = Path(destino)
    fonte = destino / "src_"
    if fonte.exists():
        shutil.rmtree(fonte, ignore_errors=True)
    for a in arquivos:
        caminho = a["path"]
        if not caminho.startswith("frontend/"):
            continue
        alvo = fonte / caminho[len("frontend/"):]
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(a["content"], encoding="utf-8")

    modulos = CACHE_FRONTEND / "node_modules"
    if modulos.exists():
        link = fonte / "node_modules"
        if not link.exists():
            try:
                link.symlink_to(modulos, target_is_directory=True)
            except OSError:
                pass

    esbuild = _achar_esbuild()
    if not esbuild:
        return {"ok": False, "erro": "esbuild não encontrado — não é possível empacotar o protótipo"}

    destino.mkdir(parents=True, exist_ok=True)
    saida_js = destino / "bundle.js"
    cmd = [esbuild, str(fonte / "src" / "index.js"), "--bundle", "--loader:.js=jsx",
           "--loader:.jsx=jsx", f"--outfile={saida_js}",
           # O App gerado lê process.env.REACT_APP_BACKEND_URL; sem definir o objeto inteiro,
           # o pacote quebra no navegador com "process is not defined" e a tela fica em branco.
           '--define:process={"env":{"NODE_ENV":"production"}}', "--minify"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd=str(fonte))
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "erro": f"falha ao empacotar: {e}"}
    if r.returncode != 0:
        return {"ok": False, "erro": (r.stderr or r.stdout or "erro ao empacotar")[-1200:]}

    (destino / "index.html").write_text(
        '<!doctype html><html lang="pt-br"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{project_name} — protótipo</title>'
        '<script src="https://cdn.tailwindcss.com"></script>'
        '<style>body{margin:0}</style></head><body><div id="root"></div>'
        '<script src="./bundle.js"></script></body></html>', encoding="utf-8")

    resumo = resumo_prototipo(arquivos)
    resumo.update({"ok": True, "erro": "", "bytes": saida_js.stat().st_size})
    return resumo


# ── Fase 5: contrato de tela ──────────────────────────────────────────────────

_MARCAS_POR_TIPO = {
    "metric-card": ("flex:1,minWidth:170", "cartão de indicador"),
    "kpi": ("flex:1,minWidth:170", "cartão de indicador"),
    "metric": ("flex:1,minWidth:170", "cartão de indicador"),
    "chart": ("ResponsiveContainer", "gráfico"),
    "table": ("<table", "tabela"),
    "grid": ("<table", "tabela"),
    "datagrid": ("<table", "tabela"),
    "kanban": ("<ol", "lista de itens"),
    "list": ("<ol", "lista de itens"),
    "checklist": ("<ol", "lista de itens"),
    "checkbox": ('type="checkbox"', "caixa de marcação"),
    "readonly": ('dado("', "valor de leitura"),
    "label": ('dado("', "valor de leitura"),
    "static": ('dado("', "valor de leitura"),
    "text": ("<input", "campo"),
    "number": ("<input", "campo"),
    "date": ("<input", "campo"),
    "textarea": ("<input", "campo"),
    "password": ("<input", "campo"),
    "email": ("<input", "campo"),
    "select": ("<select", "seleção"),
}


def conferir_contrato_de_tela(ui_spec: dict, arquivos: List[Dict[str, str]]) -> dict:
    """Compara o que a Especificação de Interface DECLARA com o que o código EMITIU.

    Foi por falta desta conferência que sete telas de negócio nasceram com um título e um
    botão: o emissor descartava calado o que não sabia desenhar, e ninguém comparava o
    aprovado com o entregue. Aqui toda diferença é NOMEADA — nunca some.

    Devolve {ok, divergencias:[{tela, tipo, campo, o_que}], conferidas, componentes}.
    """
    import re as _re

    # Usa a MESMA nomeação do emissor — inventar outra fazia a conferência não achar 10 das 12
    # telas e acusar divergência onde não havia.
    from agents.langnetagents import _pascal_case

    def _sem_vocabulario(codigo: str) -> str:
        """Remove os blocos que LISTAM nomes de campo sem renderizá-los.

        O renderizador de desfecho injeta `CAMPOS_NA_TELA` e `MENSAGENS_UC` com todos os nomes
        declarados. Procurar o campo no arquivo inteiro achava o nome nessas listas e a
        conferência dizia "todos emitidos" mesmo com componente faltando — falso negativo que
        anula o portão inteiro.
        """
        c = _re.sub(r"(?s)const CAMPOS_NA_TELA = new Set\(\[.*?\]\);", "", codigo)
        c = _re.sub(r"(?s)const MENSAGENS_UC = \[.*?\];", "", c)
        return c

    fontes = {a["path"].rsplit("/", 1)[-1][:-4]: _sem_vocabulario(a["content"])
              for a in arquivos if "/screens/" in a["path"] and a["path"].endswith(".jsx")}
    telas = (ui_spec or {}).get("screens") or ui_spec or []
    divergencias: List[dict] = []
    conferidas = componentes = 0

    for tela in telas if isinstance(telas, list) else []:
        nome = tela.get("name") or ""
        alvo = _pascal_case(tela.get("id") or nome or "Screen")
        src = fontes.get(alvo, "")
        if not src:
            for chave, conteudo in fontes.items():
                if chave.lower().startswith(alvo.lower()[:12]) or alvo.lower().startswith(chave.lower()[:12]):
                    src = conteudo
                    break
        if not src:
            divergencias.append({"tela": nome, "tipo": "-", "campo": "-",
                                 "o_que": "tela declarada não tem código emitido"})
            continue
        conferidas += 1
        for c in (tela.get("components") or []):
            componentes += 1
            tipo = (c.get("type") or "").lower()
            campo = c.get("field") or ""
            marca, rotulo = _MARCAS_POR_TIPO.get(tipo, ("", tipo or "componente"))
            # Duas perguntas, nesta ordem: o CAMPO declarado chegou ao código? E a ESTRUTURA
            # que o tipo exige (gráfico, tabela, lista, marcação, indicador) está lá? Marca de
            # um molde só dava falso positivo nas telas emitidas pelo outro molde — por isso a
            # estrutura só é cobrada dos tipos que têm forma própria.
            estruturais = ("chart", "table", "grid", "datagrid", "kanban", "list",
                           "checklist", "checkbox", "metric-card", "kpi", "metric", "select")
            if campo and campo not in src:
                divergencias.append({"tela": nome, "tipo": tipo, "campo": campo,
                                     "o_que": f"campo declarado ({rotulo}) não aparece no código"})
            elif tipo in estruturais and marca and marca not in src:
                divergencias.append({"tela": nome, "tipo": tipo, "campo": campo,
                                     "o_que": f"{rotulo} declarado não foi emitido"})
    return {"ok": not divergencias, "divergencias": divergencias,
            "conferidas": conferidas, "componentes": componentes}

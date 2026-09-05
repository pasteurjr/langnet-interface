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
    saida.append({"path": "frontend/src/index.js", "content":
        'import React from "react";\n'
        'import { createRoot } from "react-dom/client";\n'
        'import App from "./App";\n\n'
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

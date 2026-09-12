"""Etapa FERRAMENTAS do pipeline LangNet.

A etapa de Agentes e Tarefas (ATS) apenas NOMEIA as ferramentas numa coluna de texto.
Ninguém, depois dela, dizia quem implementa cada nome — e a Geração de Código acabava
pedindo o corpo ao modelo, que devolvia implementação de mentira (valor fixo). Esta etapa
fecha esse buraco: pega a lista de nomes do ATS e obriga cada uma a ter ORIGEM declarada.

Origens possíveis:
  - biblioteca   : implementação real já existente no gerador (PDF, CSV, e-mail, vetorial…)
  - mcp          : ferramenta externa registrada e atribuída na etapa MCP
  - deterministica: função gerada a partir de um CONTRATO declarado aqui (entrada/saída/regra)
  - pendente     : ninguém implementa — BLOQUEIA a geração em vez de virar valor inventado

O resultado é um documento versionado, refinável por chat e aprovável, como as demais etapas.
"""
from typing import Any, Dict, List, Optional
import json
import re


# Nomes que o gerador já implementa de verdade (ws-server/tools_std.py + tools_ext.py).
BIBLIOTECA_REAL = {
    "pdf_generator_tool": "gera PDF com reportlab e grava o arquivo",
    "csv_exporter_tool": "grava CSV real com csv.DictWriter",
    "embedding_tool": "gera embeddings (requer modelo configurado)",
    "vector_search_tool": "busca vetorial (requer índice configurado)",
    "email_sender_tool": "envia e-mail por SMTP; sem SMTP configurado falha explícito",
    "pdf_reader": "lê texto de PDF",
    "docx_reader": "lê texto de documento",
    "document_parser_tool": "extrai texto de documento",
    "file_reader_tool": "lê arquivo do disco",
    "database_tool": "executa SQL parametrizado no banco do app",
    "jwt_tool": "emite token de sessão assinado (HS256) com segredo do ambiente",
}

# Sinônimos comuns que o ATS costuma usar para as ferramentas da biblioteca.
SINONIMOS = {
    "pdf_writer": "pdf_generator_tool",
    "pdf_generator": "pdf_generator_tool",
    "report_generator": "pdf_generator_tool",
    "csv_writer": "csv_exporter_tool",
    "csv_exporter": "csv_exporter_tool",
    "email_tool": "email_sender_tool",
    "email_sender": "email_sender_tool",
    "notification_tool": "email_sender_tool",
    "file_reader": "file_reader_tool",
    "db_tool": "database_tool",
    "gerar_jwt": "jwt_tool",
    "jwt_generator": "jwt_tool",
    "gerar_relatorio": "pdf_generator_tool",
    "report_generator_tool": "pdf_generator_tool",
}


def _nomes_do_ats(binding: Dict[str, Dict[str, List[str]]]) -> Dict[str, List[str]]:
    """Nome da ferramenta -> lista de agentes/tarefas que a citam."""
    usos: Dict[str, List[str]] = {}
    for escopo in ("agents", "tasks"):
        for dono, ferramentas in (binding.get(escopo) or {}).items():
            for f in ferramentas or []:
                usos.setdefault(f, []).append(f"{'agente' if escopo == 'agents' else 'tarefa'}:{dono}")
    return usos


def resolver_ferramentas(binding: Dict[str, Dict[str, List[str]]],
                         mcp_assign: Optional[List[dict]] = None) -> Dict[str, Any]:
    """Classifica cada ferramenta citada no ATS pela sua ORIGEM de implementação."""
    usos = _nomes_do_ats(binding or {})
    mcp_nomes = {a.get("tool_name"): a for a in (mcp_assign or []) if a.get("tool_name")}
    itens: List[Dict[str, Any]] = []
    for nome in sorted(usos):
        canon = SINONIMOS.get(nome, nome)
        if nome in mcp_nomes or canon in mcp_nomes:
            a = mcp_nomes.get(nome) or mcp_nomes.get(canon)
            itens.append({
                "nome": nome, "origem": "mcp", "resolvida": True,
                "implementacao": f"servidor MCP — {a.get('server_name') or a.get('server_id') or 'externo'}",
                "descricao": (a.get("description") or "").strip(),
                "entrada": list(a.get("input_args") or []),
                "saida": list(a.get("output_args") or []), "regra": "", "usada_por": usos[nome],
            })
        elif canon in BIBLIOTECA_REAL:
            itens.append({
                "nome": nome, "origem": "biblioteca", "resolvida": True,
                "implementacao": f"biblioteca do gerador ({canon})",
                "descricao": BIBLIOTECA_REAL[canon],
                "entrada": [], "saida": [], "regra": "", "usada_por": usos[nome],
            })
        else:
            itens.append({
                "nome": nome, "origem": "pendente", "resolvida": False,
                "implementacao": "",
                "descricao": "", "entrada": [], "saida": [], "regra": "",
                "usada_por": usos[nome],
            })
    # Ferramentas atribuídas na etapa MCP que o ATS não citou também fazem parte do sistema:
    # aparecem aqui como resolvidas, para o inventário ficar completo.
    for nome, a in mcp_nomes.items():
        if any(i["nome"] == nome for i in itens):
            continue
        itens.append({
            "nome": nome, "origem": "mcp", "resolvida": True,
            "implementacao": f"servidor MCP — {a.get('server_name') or a.get('server_id') or 'externo'}",
            "descricao": (a.get("description") or "").strip(),
            "entrada": list(a.get("input_args") or []), "saida": list(a.get("output_args") or []),
            "regra": "", "usada_por": ["atribuída na etapa MCP"],
        })
    itens.sort(key=lambda i: i["nome"])
    return {
        "tools": itens,
        "resumo": {
            "total": len(itens),
            "resolvidas": sum(1 for i in itens if i["resolvida"]),
            "pendentes": sum(1 for i in itens if not i["resolvida"]),
        },
    }


def _e_banco(nome: str) -> bool:
    """Ferramenta que é, na verdade, acesso ao banco (a lista vive no tradutor de regras)."""
    try:
        from agents.langnetregras import e_ferramenta_de_banco
        return e_ferramenta_de_banco(nome)
    except Exception:  # noqa: BLE001
        return False


def _e_chamador_generico(nome: str) -> bool:
    """Nome genérico de chamada externa — o alvo real vai no argumento (idem)."""
    try:
        from agents.langnetregras import CHAMADORES_GENERICOS
        alvo = (nome or "").strip().lower()
        return any(c in alvo for c in CHAMADORES_GENERICOS)
    except Exception:  # noqa: BLE001
        return False


def propor_contratos(doc: Dict[str, Any], ats_md: str, completar) -> Dict[str, Any]:
    """Para cada ferramenta PENDENTE, propõe contrato e forma de implementação.

    `completar(prompt, expected_output, system)` é a chamada ao modelo (injetada pelo router
    para não acoplar esta etapa ao provedor). Uma falha do modelo deixa a ferramenta pendente —
    nunca inventa implementação.
    """
    pendentes = [t for t in doc.get("tools", []) if not t.get("resolvida")]
    if not pendentes:
        return doc
    nomes = [t["nome"] for t in pendentes]
    trecho = (ats_md or "")[:12000]
    prompt = (
        "Você recebe a especificação de agentes e tarefas de um sistema e a lista de "
        "FERRAMENTAS citadas nela que ainda não têm implementação definida.\n\n"
        f"FERRAMENTAS PENDENTES: {', '.join(nomes)}\n\n"
        f"ESPECIFICAÇÃO (trecho):\n{trecho}\n\n"
        "Para CADA ferramenta pendente, responda com:\n"
        "  nome, descricao (1 frase do que ela faz),\n"
        "  entrada (lista de nomes de parâmetro),\n"
        "  saida (lista de nomes de campo devolvidos),\n"
        "  origem: 'deterministica' quando a ferramenta é uma REGRA/CÁLCULO que pode ser "
        "escrito em código (ex.: conferir hash de senha, contar classes de resistência, "
        "validar formato); ou 'externa' quando depende de um sistema de fora (API, serviço, "
        "laboratório) — nesse caso ela terá de ser registrada na etapa MCP.\n"
        "  regra: quando origem='deterministica', descreva a regra em UMA frase imperativa, "
        "sem código.\n"
        "  passos: quando origem='deterministica', TAMBÉM declare o cálculo em passos — é o que "
        "vira código. Sem passos a ferramenta nasce recusando quando chamada. Tipos permitidos "
        "(regra é CÁLCULO PURO: não lê banco, não aciona sistema externo, não consulta modelo):\n"
        '    {"tipo":"calculo","atribui":"nome","expressao":"expr"}\n'
        '    {"tipo":"condicao","se":"expr booleana","passos":[...]}\n'
        '    {"tipo":"laco","para_cada":"item","em":"expr de lista","passos":[...]}\n'
        '    {"tipo":"verificacao","recusa_se":"expr","mensagem":"frase de recusa"}\n'
        '    {"tipo":"retorno","campos":["nome1","nome2"]}   (obrigatório, no fim)\n'
        "  Nas expressões use os nomes da `entrada` e as funções: conta_valor(json,'R'), "
        "tamanho(x), existe(x), vazio(x), entre(x,a,b), em(x,[...]), arredonda(x,n), soma(lista,campo), "
        "media(lista,campo), primeiro(lista), texto(x), numero(x), maiusculas(x), minusculas(x), "
        "contem(texto,parte), hoje(), dias_entre(a,b), codigo_valido(codigo,tamanho), "
        "json_valido(texto), de_json(texto), "
        "confere_senha(senha,hash). Operadores: + - * /, == != < <= > >=, e / ou / nao.\n\n"
        "NUNCA proponha valores de exemplo como resultado. Responda JSON puro: "
        '{"tools": [{"nome": ..., "descricao": ..., "entrada": [...], "saida": [...], '
        '"origem": "deterministica"|"externa", "regra": ..., "passos": [...]}]}'
    )
    try:
        bruto = completar(prompt, "JSON puro com a chave tools",
                          "Você é um arquiteto de software. Responda só JSON.")
        m = re.search(r"\{.*\}", bruto or "", re.S)
        dados = json.loads(m.group(0)) if m else {}
    except Exception as e:  # noqa: BLE001
        doc.setdefault("log", []).append(f"proposta de contratos falhou: {e}")
        return doc
    por_nome = {t.get("nome"): t for t in (dados.get("tools") or []) if isinstance(t, dict)}
    for item in doc.get("tools", []):
        p = por_nome.get(item["nome"])
        if not p:
            continue
        origem = (p.get("origem") or "").strip().lower()
        item["descricao"] = (p.get("descricao") or "").strip()
        item["entrada"] = [str(x) for x in (p.get("entrada") or [])]
        item["saida"] = [str(x) for x in (p.get("saida") or [])]
        item["regra"] = (p.get("regra") or "").strip()
        if origem == "deterministica" and item["regra"]:
            # A regra vira CÓDIGO quando vem declarada em passos e o contrato valida — o mesmo
            # tradutor das tarefas a emite. Só a frase, sem passos, continua pendente: a ferramenta
            # nasce recusando e o portão barra, em vez de fingir que existe.
            item["origem"] = "deterministica"
            passos = p.get("passos") if isinstance(p.get("passos"), list) else []
            item["passos"] = passos
            if passos:
                from agents.langnetregras import validar_regra as _vr
                probs = _vr(passos, item["entrada"])
                item["problemas_regra"] = probs
                item["resolvida"] = not probs
                item["implementacao"] = (
                    f"regra em {len(passos)} passo(s) — vira código na geração"
                    if not probs else
                    "contrato da regra com problema: " + "; ".join(x["motivo"] for x in probs[:2]))
            else:
                item["resolvida"] = False
                item["implementacao"] = ("regra descrita só em texto — declare os passos do cálculo "
                                         "para ela virar código")
        elif _e_banco(item["nome"]):
            # Banco de dados NÃO é ferramenta externa: no contrato da tarefa, ler e gravar são
            # passos de `consulta` e `escrita`, feitos pelo programa. Ficava como pendência falsa
            # ("registre na etapa MCP"), poluindo o inventário e o portão com algo que nunca vai
            # ter servidor externo nenhum.
            item["origem"] = "banco"
            item["resolvida"] = True
            item["implementacao"] = ("acesso a banco — vira passo de consulta/escrita na tarefa, "
                                     "não precisa de ferramenta")
        elif _e_chamador_generico(item["nome"]):
            # Nome genérico de chamada ("api_call_tool"): o alvo REAL está no argumento da
            # chamada, e costuma já estar resolvido (consultar_microbiologia, escore_risco_cox).
            # Marcá-lo como externo criava uma pendência que ninguém consegue resolver.
            item["origem"] = "chamador"
            item["resolvida"] = True
            item["implementacao"] = ("chamador genérico — o alvo real é a ferramenta citada no "
                                     "argumento; confira se ela está resolvida acima")
        else:
            item["origem"] = "externa"
            item["resolvida"] = False
            item["implementacao"] = "precisa ser registrada na etapa MCP (sistema externo)"
    doc["resumo"] = {
        "total": len(doc.get("tools", [])),
        "resolvidas": sum(1 for i in doc["tools"] if i.get("resolvida")),
        "pendentes": sum(1 for i in doc["tools"] if not i.get("resolvida")),
    }
    return doc


def aplicar_refino(doc: Dict[str, Any], instrucao: str, completar) -> Dict[str, Any]:
    """Aplica uma instrução em linguagem natural sobre o documento de ferramentas."""
    atual = json.dumps(doc.get("tools", []), ensure_ascii=False)[:12000]
    prompt = (
        "Documento de FERRAMENTAS de um sistema (JSON):\n" + atual +
        "\n\nINSTRUÇÃO DO USUÁRIO:\n" + (instrucao or "") +
        "\n\nAplique a instrução e devolva a LISTA COMPLETA de ferramentas no mesmo formato "
        "(nome, origem, resolvida, implementacao, descricao, entrada, saida, regra, usada_por). "
        "Origem válida: biblioteca | mcp | deterministica | externa | pendente. "
        "Não invente ferramenta que ninguém citou; não marque como resolvida sem regra ou "
        "implementação declarada. Responda JSON puro: {\"tools\": [...]}"
    )
    try:
        bruto = completar(prompt, "JSON puro com a chave tools",
                          "Você é um arquiteto de software. Responda só JSON.")
        m = re.search(r"\{.*\}", bruto or "", re.S)
        novos = (json.loads(m.group(0)) if m else {}).get("tools")
    except Exception as e:  # noqa: BLE001
        doc.setdefault("log", []).append(f"refino falhou: {e}")
        return doc
    if isinstance(novos, list) and novos:
        antigos = {t.get("nome"): t for t in doc.get("tools", [])}
        saida = []
        for t in novos:
            if not isinstance(t, dict) or not t.get("nome"):
                continue
            base = dict(antigos.get(t["nome"], {}))
            base.update(t)
            base["resolvida"] = base.get("origem") in ("biblioteca", "mcp")
            if base.get("origem") == "deterministica" and not base.get("passos"):
                base["implementacao"] = ("regra descrita só em texto — declare os passos do cálculo "
                                         "para ela virar código")
            saida.append(base)
        doc["tools"] = saida
        doc["resumo"] = {
            "total": len(saida),
            "resolvidas": sum(1 for i in saida if i.get("resolvida")),
            "pendentes": sum(1 for i in saida if not i.get("resolvida")),
        }
    return doc


def portao(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Portão da etapa: geração de código não deve rodar com ferramenta pendente."""
    pend = [t["nome"] for t in doc.get("tools", []) if not t.get("resolvida")]
    return {"aprovado": not pend, "pendentes": pend,
            "mensagem": ("todas as ferramentas têm implementação declarada" if not pend
                         else "ferramentas sem implementação: " + ", ".join(pend))}

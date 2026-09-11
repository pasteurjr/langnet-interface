"""Geração da Especificação Funcional em FASES.

POR QUE ISTO EXISTE
-------------------
A etapa fazia UMA chamada só ao modelo, com um prompt de ~60 mil caracteres pedindo as catorze
seções de uma vez, incluindo "no mínimo dez casos de uso completamente detalhados". Medido em
09/09/2026 no BioByte: o modelo devolveu catorze seções com os nomes DELE, sem nenhuma seção de
Casos de Uso e sem um único caso de uso escrito. O guardião da matriz então amarrou os catorze
requisitos a um "UC-001" que não existia em lugar nenhum do documento.

Isso não é defeito de um modelo específico: é o pedido que depende da boa vontade de quem
responde. Um pedido de catorze seções numa tacada é atendido "por cima" por qualquer modelo — o
que varia é o quanto.

COMO PASSA A SER
----------------
1. PLANO — uma chamada curta devolve a LISTA de casos de uso (id, título, ator, requisitos que
   cada um realiza), conferida contra os requisitos: requisito sem caso de uso é cobrado de volta.
2. CASOS DE USO — escritos em LOTES pequenos, um pedido por lote, com o molde canônico. Cada caso
   de uso volta conferido (cabeçalho, fluxo principal, alternativos, exceções, croqui); lote que
   volta incompleto é refeito uma vez.
3. DEMAIS SEÇÕES — um pedido separado, já sabendo a lista de casos de uso, para as referências
   cruzadas apontarem para casos que existem.
4. MONTAGEM — o documento é montado AQUI, em Python, na ordem fixa das catorze seções, e a matriz
   de rastreabilidade é construída do plano (nunca inventada).
5. CONFERÊNCIA — o que faltar é DITO, com nome: seção ausente, caso de uso faltando, requisito sem
   caso de uso, caso de uso citado que não existe.

O texto das instruções NÃO é duplicado aqui: ele é recortado do prompt canônico
(`app/templates/specification_prompt.py`), para as duas gerações continuarem falando a mesma língua.
"""
from __future__ import annotations

import json
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

# Cabeçalhos das catorze seções, na ordem em que o documento tem de sair. É esta lista que a
# montagem usa — não a que o modelo resolver inventar.
SECOES = [
    "1. Introdução",
    "2. Visão Geral do Sistema",
    "3. Requisitos Cobertos por Esta Especificação",
    "4. Detalhamentos Técnicos de RNFs (complementares ao requirements)",
    "5. Casos de Uso",
    "6. Modelo de Dados Conceitual",
    "7. Interfaces do Sistema",
    "8. Regras de Negócio",
    "9. Fluxos de Trabalho",
    "10. Análise de Arquitetura Preliminar",
    "11. Controle de Qualidade",
    "12. Glossário",
    "13. Rastreabilidade",
    "14. Apêndices",
]

# Partes que todo caso de uso tem de trazer. Falta de qualquer uma faz o lote ser refeito.
PARTES_DO_CASO = {
    "cabeçalho": r"\|\s*\*\*Ator Principal\*\*\s*\|",
    "fluxo principal": r"####\s*Fluxo Principal",
    "fluxos alternativos": r"####\s*Fluxos Alternativos",
    "fluxos de exceção": r"####\s*Fluxos de Exceç",
    "croqui da tela": r"####\s*Wireframe",
}

# O MESMO cabeçalho em todas as chamadas: o cache de contexto do provedor casa pelo começo
# EXATO do texto — um cabeçalho diferente já quebra o aproveitamento.
CABECALHO_REQUISITOS = "=== DOCUMENTO DE REQUISITOS (use os nomes REAIS daqui) ===\n"

Completar = Callable[..., Awaitable[str]]


# ─────────────────────────── recorte do prompt canônico ───────────────────────────

def fatiar_prompt(prompt_completo: str) -> Tuple[str, str, str]:
    """Recorta o prompt canônico em (contexto, instruções dos casos de uso, instruções do resto).

    Os cortes usam os próprios cabeçalhos do documento — que são a estrutura pedida, não detalhe
    de implementação. Se algum corte falhar, devolve o prompt inteiro como contexto e as outras
    partes vazias: o chamador percebe e diz o motivo, em vez de gerar torto em silêncio.
    """
    i5 = prompt_completo.find("## 5. Casos de Uso")
    i6 = prompt_completo.find("## 6. Modelo de Dados Conceitual")
    if i5 < 0 or i6 < 0 or i6 <= i5:
        return prompt_completo, "", ""
    return prompt_completo[:i5], prompt_completo[i5:i6], prompt_completo[i6:]


def _so_json(texto: str) -> Any:
    """Lê o primeiro objeto/lista JSON da resposta, ignorando texto em volta e cercas de código."""
    t = (texto or "").strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1]
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    for abre, fecha in (("[", "]"), ("{", "}")):
        i = t.find(abre)
        if i >= 0:
            try:
                obj, _ = json.JSONDecoder().raw_decode(t[i:])
                return obj
            except Exception:
                continue
    raise ValueError("resposta sem JSON legível")


def requisitos_funcionais(requisitos_md: str) -> List[str]:
    """Identificadores de requisito funcional presentes no documento de requisitos."""
    achados = re.findall(r"\b(?:FR|RF)-(\d{2,3})\b", requisitos_md or "")
    return sorted({f"FR-{n.zfill(3)}" for n in achados})


def _titulo_do_requisito(requisitos_md: str, fr: str) -> str:
    """Título do requisito na tabela de requisitos (para a matriz sair legível)."""
    alt = fr.replace("FR-", "RF-")
    for ident in (fr, alt):
        m = re.search(re.escape(ident) + r"\s*\|[^|]*\|\s*([^|]+)\|", requisitos_md or "")
        if m:
            return m.group(1).strip()[:60]
        m = re.search(re.escape(ident) + r"\s*[:\-–]\s*([^\n|]{4,80})", requisitos_md or "")
        if m:
            return m.group(1).strip()[:60]
    return fr


# ─────────────────────────────── fase 1: o plano ───────────────────────────────

async def planejar_casos_de_uso(requisitos_md: str, completar: Completar,
                                minimo: int = 10) -> Tuple[List[dict], List[str]]:
    """Lista de casos de uso conferida contra os requisitos.

    Devolve (plano, avisos). Cada item: {id, titulo, ator, frs}. Requisito que ninguém realiza é
    cobrado de volta numa segunda chamada, focada só nos que faltaram — em vez de ficar órfão e
    ser remendado depois por semelhança de palavras.
    """
    avisos: List[str] = []
    frs = requisitos_funcionais(requisitos_md)
    # ORDEM IMPORTA PARA O CUSTO: o DeepSeek cobra bem menos pelo trecho INICIAL que ele já viu
    # (cache de contexto, medido em 11/09/2026: 1.536 de 1.708 tokens vieram do cache na segunda
    # chamada com o mesmo começo). Por isso o material GRANDE E ESTÁVEL — o documento de requisitos —
    # vem PRIMEIRO e igual em todas as chamadas; o pedido, que muda a cada uma, vem por último.
    pedido = (
        CABECALHO_REQUISITOS + requisitos_md + "\n\n"
        "Você recebe o documento de requisitos acima e devolve a LISTA dos casos de uso do sistema.\n\n"
        f"REQUISITOS FUNCIONAIS A COBRIR ({len(frs)}): {', '.join(frs)}\n\n"
        "Regras:\n"
        f"- pelo menos {minimo} casos de uso, numerados UC-001, UC-002, … em sequência;\n"
        "- TODO requisito funcional da lista acima tem de aparecer em pelo menos um caso de uso;\n"
        "- o título é a AÇÃO do usuário no vocabulário do domínio (ex.: 'Autenticar Usuário com "
        "MFA', 'Calcular Escore de Risco'), nunca um nome genérico como 'Caso de Uso Central';\n"
        "- o ator é o perfil real citado nos requisitos;\n"
        "- não invente requisito que não está na lista.\n\n"
        "Responda SOMENTE um JSON, sem texto antes ou depois:\n"
        '[{"id":"UC-001","titulo":"…","ator":"…","frs":["FR-001"]}, …]'
    )
    bruto = await completar(pedido, max_tokens=8000)
    try:
        plano = [p for p in _so_json(bruto) if isinstance(p, dict) and p.get("titulo")]
    except Exception as e:  # noqa: BLE001
        return [], [f"o plano de casos de uso não veio legível: {e}"]

    plano = _renumerar(plano)
    faltando = [f for f in frs if f not in _frs_do_plano(plano)]
    if faltando:
        avisos.append(f"na primeira volta ficaram sem caso de uso: {', '.join(faltando)}")
        complemento = (
            CABECALHO_REQUISITOS + requisitos_md + "\n\n"
            "Estes requisitos funcionais ficaram SEM caso de uso na lista anterior: "
            + ", ".join(faltando) + ".\n\n"
            "Devolva SOMENTE os casos de uso que faltam para cobri-los, no mesmo formato JSON, "
            f"continuando a numeração a partir de UC-{len(plano) + 1:03d}. Não repita os que já existem.\n\n"
            "JÁ EXISTEM: " + ", ".join(f"{p['id']} {p['titulo']}" for p in plano)
        )
        try:
            extras = [p for p in _so_json(await completar(complemento, max_tokens=6000))
                      if isinstance(p, dict) and p.get("titulo")]
            plano = _renumerar(plano + extras)
        except Exception as e:  # noqa: BLE001
            avisos.append(f"a complementação do plano falhou: {e}")

    ainda = [f for f in frs if f not in _frs_do_plano(plano)]
    if ainda:
        avisos.append(f"requisito(s) sem caso de uso mesmo após a complementação: {', '.join(ainda)}")
    if len(plano) < minimo:
        avisos.append(f"o plano tem {len(plano)} caso(s) de uso — o pedido era pelo menos {minimo}")
    return plano, avisos


def _renumerar(plano: List[dict]) -> List[dict]:
    """Numeração em sequência e sem repetição — o resto do pipeline casa telas e tarefas por ela."""
    saida, vistos = [], set()
    for i, p in enumerate(plano, 1):
        titulo = str(p.get("titulo") or "").strip()
        if not titulo or titulo.lower() in vistos:
            continue
        vistos.add(titulo.lower())
        frs = [str(f).strip().upper().replace("RF-", "FR-") for f in (p.get("frs") or [])]
        saida.append({"id": f"UC-{len(saida) + 1:03d}", "titulo": titulo,
                      "ator": str(p.get("ator") or "").strip() or "Usuário",
                      "frs": [f for f in frs if re.match(r"^FR-\d{3}$", f)]})
    return saida


def _frs_do_plano(plano: List[dict]) -> set:
    return {f for p in plano for f in (p.get("frs") or [])}


# ──────────────────────── fase 2: escrever os casos de uso ────────────────────────

async def escrever_casos_de_uso(plano: List[dict], requisitos_md: str, instrucoes_uc: str,
                                completar: Completar, por_lote: int = 3
                                ) -> Tuple[Dict[str, str], List[str]]:
    """Escreve os casos de uso em lotes pequenos. Devolve ({id: markdown}, avisos).

    Lote pequeno é o ponto: pedido curto e específico é atendido por inteiro; pedido de "dez casos
    completos" é atendido por cima. Lote que volta sem alguma parte obrigatória é refeito UMA vez,
    dizendo o que faltou; o que continuar faltando entra nos avisos com nome.
    """
    escritos: Dict[str, str] = {}
    avisos: List[str] = []
    for inicio in range(0, len(plano), por_lote):
        lote = plano[inicio:inicio + por_lote]
        alvo = ", ".join(f"{p['id']} ({p['titulo']})" for p in lote)
        # O começo (requisitos + molde) é IGUAL em todos os lotes — é o que o cache aproveita.
        # A lista do lote, que muda, fica no fim.
        base = (
            CABECALHO_REQUISITOS + requisitos_md
            + "\n\n=== MOLDE DO CASO DE USO (siga fielmente) ===\n" + instrucoes_uc + "\n\n"
            "Escreva a especificação detalhada APENAS dos casos de uso listados abaixo, no formato "
            "do molde. Nada além deles: sem introdução, sem conclusão, sem outras seções.\n\n"
            "CASOS DE USO DESTE PEDIDO:\n"
            + "\n".join(f"- **{p['id']}: {p['titulo']}** — ator {p['ator']}; "
                        f"realiza {', '.join(p['frs']) or '(ver requisitos)'}" for p in lote)
            + "\n\nCada um começa exatamente com uma linha `#### UC-XXX: Título` e traz TODAS as "
              "partes do molde: tabela de cabeçalho, Fluxo Principal, Fluxos Alternativos, "
              "Fluxos de Exceção e Wireframe da Interface."
        )
        texto = await completar(base, max_tokens=16000)
        partes, faltas = _separar_casos(texto, [p["id"] for p in lote])

        if faltas:
            cobranca = (
                base + "\n\n=== O QUE FALTOU NA SUA RESPOSTA ANTERIOR ===\n"
                + "\n".join(f"- {k}: {v}" for k, v in faltas.items())
                + "\nRefaça o pedido inteiro, agora completo."
            )
            texto2 = await completar(cobranca, max_tokens=16000)
            partes2, faltas2 = _separar_casos(texto2, [p["id"] for p in lote])
            # fica a volta com MENOS faltas — não a que trouxe mais blocos pela metade
            if len(faltas2) <= len(faltas):
                partes, faltas = partes2, faltas2
            for k, v in (faltas or {}).items():
                avisos.append(f"{k}: {v}")
        escritos.update(partes)

    nao_escritos = [p["id"] for p in plano if p["id"] not in escritos]
    if nao_escritos:
        avisos.append("caso(s) de uso planejados que não foram escritos: " + ", ".join(nao_escritos))
    return escritos, avisos


def _separar_casos(texto: str, esperados: List[str]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Separa a resposta por caso de uso e confere as partes obrigatórias de cada um."""
    texto = texto or ""
    # aceita `#### UC-001: …` e `**UC-001: …**` (os dois formatos que o molde já produziu)
    marcas = list(re.finditer(r"(?m)^\s*(?:#{2,5}\s*|\*\*)(UC-\d{3})\s*[::]\s*(.+?)(?:\*\*)?\s*$", texto))
    blocos: Dict[str, str] = {}
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        corpo = texto[m.start():fim].strip()
        titulo = m.group(2).strip().rstrip("*").strip()
        blocos[m.group(1)] = f"#### {m.group(1)}: {titulo}\n\n" + corpo[m.end() - m.start():].strip()
    bons, faltas = {}, {}
    for uc in esperados:
        corpo = blocos.get(uc)
        if not corpo:
            faltas[uc] = "não veio na resposta"
            continue
        ausentes = [nome for nome, padrao in PARTES_DO_CASO.items()
                    if not re.search(padrao, corpo, re.I)]
        if ausentes:
            faltas[uc] = "sem " + ", ".join(ausentes)
        bons[uc] = corpo
    return bons, faltas


# ──────────────────────── fase 3: as demais seções ────────────────────────

async def escrever_demais_secoes(plano: List[dict], contexto: str, instrucoes_resto: str,
                                 completar: Completar) -> Tuple[Dict[str, str], List[str]]:
    """Seções 1–4 e 6–14 (a 13 é montada aqui, determinística). Devolve ({numero: markdown}, avisos)."""
    lista = "\n".join(f"- {p['id']}: {p['titulo']} (ator {p['ator']}; "
                      f"realiza {', '.join(p['frs']) or '—'})" for p in plano)
    pedido = (
        contexto
        + "\n\n=== ATENÇÃO: OS CASOS DE USO JÁ ESTÃO ESCRITOS ===\n"
          "A seção 5 (Casos de Uso) já foi produzida à parte e NÃO deve ser escrita agora. "
          "Ela contém exatamente estes casos de uso — cite-os pelo identificador quando precisar:\n"
        + lista
        + "\n\nEscreva AGORA as demais seções, com estes cabeçalhos exatos e nesta ordem:\n"
        + "\n".join(f"## {s}" for s in SECOES if not s.startswith(("5.", "13.")))
        + "\n\nNão escreva a seção 5 nem a seção 13 (a rastreabilidade é montada pelo sistema).\n"
          "Não renomeie, não renumere e não acrescente seções.\n\n"
        + instrucoes_resto
    )
    texto = await completar(pedido, max_tokens=24000)
    secoes = _separar_secoes(texto)
    avisos = [f"seção ausente na resposta: {s}" for s in SECOES
              if not s.startswith(("5.", "13.")) and _numero(s) not in secoes]
    return secoes, avisos


def _numero(cabecalho: str) -> str:
    return cabecalho.split(".", 1)[0].strip()


def _separar_secoes(texto: str) -> Dict[str, str]:
    """Separa a resposta por seção numerada de primeiro nível."""
    marcas = list(re.finditer(r"(?m)^##\s*(\d{1,2})\.\s*(.+?)\s*$", texto or ""))
    saida: Dict[str, str] = {}
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        saida[m.group(1)] = texto[m.start():fim].strip()
    return saida


# ──────────────────────── fase 4: montagem e conferência ────────────────────────

def montar_matriz(plano: List[dict], requisitos_md: str) -> str:
    """Seção 13 construída do PLANO — nunca de semelhança de palavras, nunca com caso inventado."""
    frs = requisitos_funcionais(requisitos_md)
    por_fr: Dict[str, List[str]] = {}
    for p in plano:
        for f in p.get("frs") or []:
            por_fr.setdefault(f, []).append(p["id"])
    linhas = ["## 13. Rastreabilidade", "",
              "Matriz Requisito → Caso de Uso, construída da lista de casos de uso desta "
              "especificação. Requisito sem caso de uso aparece como lacuna — não é preenchido "
              "por aproximação.", "",
              "| Requisito | Título | Caso(s) de uso que o realizam |",
              "|---|---|---|"]
    lacunas = []
    for f in frs:
        ucs = por_fr.get(f) or []
        if not ucs:
            lacunas.append(f)
        linhas.append(f"| {f} | {_titulo_do_requisito(requisitos_md, f)} | "
                      f"{', '.join(ucs) if ucs else '⚠️ SEM CASO DE USO'} |")
    if lacunas:
        linhas += ["", f"⚠️ **Lacuna de rastreabilidade:** {len(lacunas)} requisito(s) sem caso de "
                       f"uso — {', '.join(lacunas)}. Refine a especificação antes de seguir."]
    return "\n".join(linhas)


def montar_documento(titulo: str, secoes: Dict[str, str], casos: Dict[str, str],
                     plano: List[dict], requisitos_md: str) -> str:
    """Documento final na ordem fixa das catorze seções. Seção que faltar aparece dita, não some."""
    partes = [f"# {titulo}", ""]
    for cab in SECOES:
        n = _numero(cab)
        if n == "5":
            partes.append("## 5. Casos de Uso")
            partes.append("")
            partes.append("### 5.1 Atores do Sistema")
            atores = sorted({p["ator"] for p in plano if p.get("ator")})
            partes += [f"- **{a}**" for a in atores] or ["- (não identificados)"]
            partes += ["", "### 5.2 Especificação Detalhada de Casos de Uso", ""]
            for p in plano:
                corpo = casos.get(p["id"])
                if corpo:
                    partes += [corpo, "", "---", ""]
                else:
                    partes += [f"#### {p['id']}: {p['titulo']}", "",
                               "⚠️ **LACUNA — caso de uso planejado que não foi escrito.** Refine a "
                               "especificação para completá-lo — nada foi inventado aqui.", "",
                               "---", ""]
        elif n == "13":
            partes += [montar_matriz(plano, requisitos_md), ""]
        else:
            corpo = secoes.get(n)
            partes += [corpo, ""] if corpo else [
                f"## {cab}", "",
                "⚠️ **LACUNA — seção não produzida nesta geração.** Refine a especificação para completá-la.",
                ""]
    return "\n".join(partes).rstrip() + "\n"


def _corpo_da_secao(documento: str, numero: str) -> str:
    m = re.search(rf"(?m)^##\s*{re.escape(numero)}\.[^\n]*\n(.*?)(?=^##\s*\d{{1,2}}\.|\Z)",
                  documento, re.S)
    return m.group(1) if m else ""


def _corpo_do_caso(documento: str, uc: str) -> str:
    m = re.search(rf"(?m)^####\s*{re.escape(uc)}\s*:[^\n]*\n(.*?)(?=^####\s*UC-\d{{3}}\s*:|^##\s*\d{{1,2}}\.|\Z)",
                  documento, re.S)
    return m.group(1) if m else ""


def conferir(documento: str, requisitos_md: str, plano: List[dict]) -> List[dict]:
    """O que faltou, com nome. Lista vazia = documento íntegro."""
    problemas: List[dict] = []
    for cab in SECOES:
        if not re.search(rf"(?m)^##\s*{re.escape(_numero(cab))}\.", documento):
            problemas.append({"o_que": "seção", "item": cab, "motivo": "não está no documento"})
    # Seção que saiu só com o marcador de lacuna NÃO conta como escrita — senão o documento
    # "passa" na conferência exibindo o próprio aviso de que está faltando.
    for cab in SECOES:
        corpo = _corpo_da_secao(documento, _numero(cab))
        if corpo and "**LACUNA —" in corpo:
            problemas.append({"o_que": "seção", "item": cab, "motivo": "saiu vazia (marcador de lacuna)"})
    presentes = {uc for uc in re.findall(r"(?m)^####\s*(UC-\d{3})\s*:", documento)
                 if "**LACUNA —" not in _corpo_do_caso(documento, uc)}
    for p in plano:
        if p["id"] not in presentes:
            problemas.append({"o_que": "caso de uso", "item": f"{p['id']} {p['titulo']}",
                              "motivo": "planejado mas não escrito"})
    citados = set(re.findall(r"\bUC-\d{3}\b", documento))
    for uc in sorted(citados - presentes - {p["id"] for p in plano}):
        problemas.append({"o_que": "caso de uso", "item": uc,
                          "motivo": "citado no documento mas não existe"})
    cobertos = _frs_do_plano(plano)
    for f in requisitos_funcionais(requisitos_md):
        if f not in cobertos:
            problemas.append({"o_que": "requisito", "item": f, "motivo": "nenhum caso de uso o realiza"})
    return problemas


# ─────────────────────────────── orquestração ───────────────────────────────

async def gerar_em_fases(prompt_canonico: str, requisitos_md: str, completar: Completar,
                         titulo: str = "Especificação Funcional",
                         minimo_casos: int = 10, por_lote: int = 3) -> Tuple[str, dict]:
    """Gera a especificação em fases e devolve (documento, relatório).

    O relatório é o que a etapa mostra e o que fica registrado: quantas chamadas, quantos casos de
    uso planejados e escritos, e a lista do que faltou. Nada é dado por bom sem conferência.
    """
    contexto, instrucoes_uc, instrucoes_resto = fatiar_prompt(prompt_canonico)
    relatorio: Dict[str, Any] = {"avisos": [], "chamadas": 0}
    if not instrucoes_uc:
        relatorio["avisos"].append("não consegui recortar as instruções dos casos de uso do prompt "
                                   "canônico — os cabeçalhos do documento mudaram?")

    contador = {"n": 0}

    async def _completar(prompt: str, **kw) -> str:
        contador["n"] += 1
        return await completar(prompt, **kw)

    plano, avisos_plano = await planejar_casos_de_uso(requisitos_md, _completar, minimo=minimo_casos)
    relatorio["avisos"] += avisos_plano
    relatorio["plano"] = plano
    if not plano:
        relatorio["chamadas"] = contador["n"]
        relatorio["problemas"] = [{"o_que": "plano", "item": "casos de uso",
                                   "motivo": "o modelo não devolveu uma lista utilizável"}]
        return "", relatorio

    casos, avisos_casos = await escrever_casos_de_uso(
        plano, requisitos_md, instrucoes_uc, _completar, por_lote=por_lote)
    relatorio["avisos"] += avisos_casos

    secoes, avisos_secoes = await escrever_demais_secoes(
        plano, contexto, instrucoes_resto, _completar)
    relatorio["avisos"] += avisos_secoes

    documento = montar_documento(titulo, secoes, casos, plano, requisitos_md)
    relatorio["chamadas"] = contador["n"]
    relatorio["casos_planejados"] = len(plano)
    relatorio["casos_escritos"] = len(casos)
    relatorio["problemas"] = conferir(documento, requisitos_md, plano)
    return documento, relatorio

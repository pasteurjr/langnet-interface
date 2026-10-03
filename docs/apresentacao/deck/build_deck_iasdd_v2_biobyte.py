# -*- coding: utf-8 -*-
"""Versao 2 do deck completo, preservando o conteudo original e adicionando BioByte real."""
import os
import re
import sys
from pathlib import Path
from pptx import Presentation

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_deck as base

D = base.D
PP_ALIGN = base.PP_ALIGN
MSO_ANCHOR = base.MSO_ANCHOR
TOTAL = 70


def slide(prs, block, kicker, title):
    s = D._blank(prs)
    D.header(s, block, kicker, title)
    return s


def code(s, text, x, y, w, size=11.5):
    D.code_block(s, text, x=x, y=y, w=w, size=size)


def register(n, block, title, minutes, script):
    base.reg(n, block, title, minutes, 0, script)


def s2(prs):
    """Agenda completa, sem o corte herdado da versao anterior."""
    s = D._blank(prs)
    D.header(s, 0, "Bloco 0 · Abertura", "Agenda completa: tecnologia, BioByte e prova")
    rows = [
        ["0", "Abertura e tese", "3"],
        ["1", "Linha do tempo e IA na saude", "5"],
        ["2", "Modelos de linguagem", "11"],
        ["3", "O que mudou para quem escreve software", "2"],
        ["4", "Contexto e RAG", "8"],
        ["5", "Agentes", "11"],
        ["6", "Protocolos e formatos", "9"],
        ["—", "INTERVALO", "5"],
        ["7", "Frameworks e SDKs", "11"],
        ["8", "Ambientes agenticos", "3"],
        ["9", "SDD", "16"],
        ["10", "Adaptacao de modelos", "5"],
        ["11", "BioByte, LangNet, demo, Co-Scientist e Petri", "31"],
        ["12", "Fechamento e perguntas", "5"],
    ]
    D.table(s, 0, ["Bloco", "Tema", "min"], rows, x=.6, y=1.98, w=8.75, h=4.65, fsize=10.4, header_fs=10.8)
    for i, (num, name, desc, col) in enumerate([
        ("①", "LLMs", "o motor: modelos e contexto", "indigo"),
        ("②", "SDD", "o metodo: especificar e verificar", "violet"),
        ("③", "BioByte", "a prova: sistema real rodando", "sky")]):
        c1, c2, c3 = D.FAM[col]; yy = 2.0 + i*1.45
        D._rect(s, 9.65, yy, 3.1, 1.3, fill=c3, rounded=True, radius=.09)
        D._rect(s, 9.65, yy, .12, 1.3, fill=c1)
        D._txt(s, 9.85, yy+.12, 2.8, .5, [[(num+"  ", {"size": 22, "bold": True, "color": c1}), (name, {"size": 19, "bold": True, "color": c1})]])
        D._txt(s, 9.85, yy+.68, 2.8, .55, [[(desc, {"size": 12.5, "color": D.INK})]], line_spacing=1.05)
    D.footer(s, 0, 2, TOTAL)
    register(2, 0, "Agenda completa", 1.5,
             "Mostre a agenda inteira. Diga que a palestra faz tres movimentos: primeiro os fundamentos e as tecnologias; "
             "depois o BioByte como caso concreto; por fim o SDD e o LangNet como prova executavel. Aponte que o video "
             "tem quinze minutos e esta incluido no bloco 11 e no total de 120 minutos. (~1,5 min)")


def fit_timing():
    """Encurta a fala, preservando os 70 slides e reservando 15 min para o video."""
    targets = {0: 3.0, 1: 5.0, 2: 11.0, 3: 2.0, 4: 8.0, 5: 11.0,
               6: 9.0, 7: 11.0, 8: 3.0, 9: 16.0, 10: 5.0,
               11: 31.0, 12: 5.0}
    for block, target in targets.items():
        rows = [x for x in base.META if x["block"] == block]
        if block == 11:
            video = [x for x in rows if x["title"].startswith("DEMO")]
            other = [x for x in rows if not x["title"].startswith("DEMO")]
            if video:
                video[0]["minutes"] = 15.0
            total_other = sum(x["minutes"] for x in other)
            factor = (target - 15.0) / total_other if total_other else 1.0
            for x in other:
                x["minutes"] *= factor
        else:
            total = sum(x["minutes"] for x in rows)
            factor = target / total if total else 1.0
            for x in rows:
                x["minutes"] *= factor
    acum = 0.0
    for x in base.META:
        acum += x["minutes"]
        x["acum"] = acum


def fix_visible_slide_numbers(path):
    """Corrige rodapes herdados que ficaram defasados apos os slides de IA medica."""
    prs = Presentation(path)
    for index, slide in enumerate(prs.slides, start=1):
        wanted = f"{index:02d} / {len(prs.slides):02d}"
        for shape in slide.shapes:
            if not hasattr(shape, "text") or not re.fullmatch(r"\d{1,2} / \d{1,2}", shape.text.strip()):
                continue
            for paragraph in shape.text_frame.paragraphs:
                if paragraph.runs:
                    paragraph.runs[0].text = wanted
                    for run in paragraph.runs[1:]:
                        run.text = ""
                else:
                    paragraph.text = wanted
    prs.save(path)


def s38(prs):
    s = slide(prs, 7, "Bloco 7 · Frameworks", "CrewAI aplicado ao BioByte")
    D.cards(s, 7, [
        ("AGENTE DO DOMINIO", "diagnostico_agent recebe microbiologia e aplica criterios NHSN/ICSAC."),
        ("TAREFA DO DOMINIO", "classificar o caso, identificar MDR e devolver evidencias."),
        ("TOOL ATRIBUIDA", "consultar_microbiologia(paciente_id), via MCP, com status e antibiograma."),
    ], x=.6, y=2.0, size=15.5)
    code(s, '''diagnostico_agent:
  role: Especialista em diagnostico e vigilancia de IRAS
  goal: >
    Consultar a microbiologia, aplicar os criterios
    NHSN para ICSAC e justificar a classificacao.
  tools:
    - consultar_microbiologia

classify_case_nhsn:
  agent: diagnostico_agent
  traceability: {uc: UC-001, fr: [FR-003, FR-004]}
  expected_output: >
    Classificacao confirmada, descartada ou pendente;
    criterios atendidos; evidencias; MDR; justificativa.''',
         7.15, 2.0, 5.55, 10.8)
    D.callout(s, 7, [("TRECHO BASEADO NO CONTRATO DO BIOBYTE — ", {"size": 12.5, "bold": True, "color": D.WARN}),
                     ("nao e uma descricao generica de agente.", {"size": 12.5, "color": D.INK})],
              y=6.35, h=.55)
    D.footer(s, 7, 41, TOTAL)
    register(41, 7, "CrewAI aplicado ao BioByte", 2.5,
             "Mostre diagnostico_agent, consultar_microbiologia e classify_case_nhsn. Explique role, goal, tools, "
             "traceability e expected_output a partir do contrato do BioByte. O trecho e didatico, mas os nomes e "
             "contratos vem dos artefatos do dominio. (~2,5 min)")


def s39(prs):
    s = slide(prs, 7, "Bloco 7 · Frameworks", "LangGraph e AutoGen no mesmo UC-001")
    D._txt(s, .65, 1.95, 5.9, .45, [[("LangGraph — estado explicito", {"size": 16, "bold": True, "color": D.FAM['indigo'][0]})]])
    code(s, '''state = {
  "caso_id": "CAS-2023-001",
  "microbiologia": None,
  "classificacao": None,
  "evidencias": []
}
graph.add_node("consultar_microbiologia", fetch)
graph.add_node("classificar_nhsn", classify)
graph.add_node("revisar_ccih", human_review)
graph.add_edge("consultar_microbiologia", "classificar_nhsn")
graph.add_edge("classificar_nhsn", "revisar_ccih")''',
         .65, 2.45, 5.9, 10.0)
    D._txt(s, 6.8, 1.95, 5.9, .45, [[("AutoGen/AG2 — debate controlado", {"size": 16, "bold": True, "color": D.FAM['violet'][0]})]])
    code(s, '''classifier = AssistantAgent(
  name="nhsn_classifier",
  system_message="Classifique e cite evidencias."
)
reviewer = AssistantAgent(
  name="evidence_reviewer",
  system_message="Recuse conclusao sem evidencia."
)
team = GroupChat([classifier, reviewer, human])
# maximo de 2 turnos + aprovacao CCIH''',
         6.8, 2.45, 5.9, 10.2)
    D.callout(s, 7, [("MESMO CASO, CONTROLES DIFERENTES: ", {"size": 13, "bold": True, "color": D.FAM['violet'][0]}),
                     ("LangGraph explicita estado; AutoGen explicita conversa. Ambos precisam de contrato e gate.", {"size": 13, "color": D.INK})],
              y=6.35, h=.55)
    D.footer(s, 7, 42, TOTAL)
    register(42, 7, "LangGraph e AutoGen no UC-001", 2.0,
             "Compare o mesmo caso BioByte. LangGraph explicita estado, transicoes e retomada; AutoGen mostra "
             "classificador, revisor e humano, mas com limite de turnos. Sao exemplos comparativos baseados no contrato "
             "real, nao afirmacao de que todos foram usados no runtime. (~2 min)")


def s58(prs):
    s = slide(prs, 11, "Bloco 11 · Sistemas", "BioByte: a especificacao que vamos executar")
    D.cards(s, 11, [
        ("DOMINIO", "BioByte Sentinela — vigilancia de IRAS, com foco em ICSAC."),
        ("UC CENTRAL", "UC-001 Avaliar paciente sentinela: cadastro → risco → microbiologia/classificacao → conduta → laudo."),
        ("TRES AGENTES", "vigilancia_agent (Cox), diagnostico_agent (NHSN/MDR), conduta_agent (bundle/RRA)."),
        ("DUAS TOOLS MCP", "consultar_microbiologia e escore_risco_cox, registradas e atribuidas pela interface."),
    ], x=.6, y=2.0, size=14.2)
    code(s, '''FR-02  Calcular o escore de risco de ICSAC
      entrada: idade, apache_ii, tipo_cateter
      saida: escore_cox, nivel_risco, fatores_de_risco

FR-03  Importar microbiologia do LIS
      consultar_microbiologia(caso_id)
      status: liberado | pendente

FR-04  Classificar NHSN e detectar MDR
      evidencias + classificacao + justificativa

NFR: LGPD · auditabilidade · rastreabilidade''',
         7.15, 2.0, 5.55, 11.0)
    D.footer(s, 11, 61, TOTAL)
    register(61, 11, "BioByte: especificacao", 2.5,
             "Antes do sistema, leia a fonte. A especificacao do BioByte define vigilancia de ICSAC, UC-001, "
             "tres agentes, requisitos de risco, microbiologia, NHSN/MDR e conduta, alem de duas integracoes MCP. "
             "Mostre FR-02, FR-03 e FR-04; os proximos slides mostram como esses contratos atravessam o pipeline. (~2,5 min)")


def s59(prs):
    s = slide(prs, 11, "Bloco 11 · Sistemas", "LangNet: da especificacao ao BioByte")
    pipe = ["Requisitos", "Spec", "Dados + UI", "Agents/Tasks", "Petri", "Codigo", "Testes"]
    x, y, cw, gap = .45, 2.0, 1.62, .16
    for i, st in enumerate(pipe):
        col = D.FAM['emerald'] if st in ("Testes", "Codigo") else D.FAM['violet']
        D._rect(s, x, y, cw, .95, fill=col[2], rounded=True, radius=.08)
        D._rect(s, x, y, cw, .11, fill=col[0])
        D._txt(s, x+.04, y+.22, cw-.08, .5, [[(st, {"size": 11.5, "bold": True, "color": col[0]})]],
               align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        x += cw
        if i < len(pipe)-1:
            D._txt(s, x, y+.25, gap, .4, [[("→", {"size": 16, "bold": True, "color": D.MUTED})]], align=PP_ALIGN.CENTER)
            x += gap
    D.cards(s, 11, [
        ("Agents/tasks", "agents.yaml/tasks.yaml carregam role, goal, tools, traceability e expected_output."),
        ("Rede de Petri", "places/transitions sincronizam tarefas; a logica do lugar chama o backend via WebSocket."),
        ("Codigo", "o gerador emite adapters e wrappers das tools MCP; o app e validado antes do deploy."),
    ], x=.6, y=3.45, size=15.7)
    D.callout(s, 11, [("Modelo e endpoint: ", {"size": 14, "bold": True, "color": D.WARN}),
                     ("preencher com a configuracao efetivamente usada no ensaio.", {"size": 14, "color": D.INK})],
              y=6.35, h=.55)
    D.footer(s, 11, 62, TOTAL)
    register(62, 11, "LangNet: arquitetura BioByte", 3.0,
             "Mostre a cadeia real: especificacao, modelo de dados, UI, agents/tasks, Petri, codigo e testes. "
             "Explique que a logica JavaScript do lugar aciona o backend Python pelo WebSocket e que a geracao emite "
             "wrappers MCP. Este e o ponto que liga SDD, CrewAI, Petri e aplicacao real. (~3 min)")


def s60(prs):
    s = slide(prs, 11, "Bloco 11 · Sistemas", "BioByte: evidencia e falhas reais")
    D.table(s, 11, ["Etapa", "Evidencia concreta"], [
        ["Microbiologia", "CAS-2023-001 → Staphylococcus aureus; antibiograma; multirresistente=true"],
        ["Cox", "escore_cox, nivel de risco e fatores retornados pela tool"],
        ["NHSN", "classificacao com criterios: cateter, hemocultura e correlacao clinica"],
        ["MDR", "alerta registrado; notificacoes externas ainda sao lacuna declarada"],
        ["Relatorio", "PDF/CSV gerado; dashboard mostra dados ou declara ausencia de serie"],
        ["Execucao", "12/13 tarefas OK no fluxo documentado; a 13a depende de dados proprios de usuario"],
    ], x=.6, y=2.0, w=12.1, fsize=12.4, header_fs=12.5, h=3.8)
    D.callout(s, 11, [("Honestidade operacional: ", {"size": 14, "bold": True, "color": D.FAM['rose'][0]}),
                     ("o sistema registra tambem o que ainda nao esta implementado.", {"size": 14, "color": D.INK})],
              y=6.1, h=.75)
    D.footer(s, 11, 63, TOTAL)
    register(63, 11, "BioByte: evidencia medida", 1.5,
             "Mostre CAS-2023-001, microbiologia, flag MDR, Cox, criterios NHSN e relatorio. Diga tambem o que "
             "permanece aberto. A validacao documenta 12 de 13 tarefas OK no fluxo clinico encadeado; a excecao "
             "depende de dados proprios de administracao. (~1,5 min)")


def s61(prs):
    s = slide(prs, 11, "Bloco 11 · Sistemas", "DEMONSTRACAO BIOBYTE — 15 minutos")
    c1, c2, c3 = D.FAM['violet']
    D._rect(s, .6, 2.05, 5.6, 4.0, fill=c3, rounded=True, radius=.06)
    D._rect(s, .6, 2.05, 5.6, .5, fill=c1)
    D._txt(s, .6, 2.09, 5.6, .45, [[("▶ VIDEO — 15 min · BioByte real", {"size": 14, "bold": True, "color": D.WHITE})]],
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    D._dot(s, 2.95, 3.55, 1.0, c1)
    D._txt(s, .8, 5.45, 5.2, .45, [[("Inserir gravacao final do pipeline", {"size": 13, "italic": True, "color": D.MUTED})]],
           align=PP_ALIGN.CENTER)
    D.bullets(s, [
        (0, [("1. requisito e especificacao BioByte", "n")]),
        (0, [("2. modelo de dados e UI Spec", "n")]),
        (0, [("3. agents.yaml/tasks.yaml rastreaveis", "n")]),
        (0, [("4. registro/atribuicao das 2 tools MCP", "n")]),
        (0, [("5. sequencia e Rede de Petri", "n")]),
        (0, [("6. codigo, testes, app e falha", "n")]),
        (0, [("7. gate de rastreabilidade", "n")]),
    ], x=6.55, y=2.05, w=D.SW-7.15, size=14.7, block=11)
    D.footer(s, 11, 64, TOTAL)
    register(64, 11, "DEMO BioByte: 15 minutos", 15.0,
             "O video ocupa quinze minutos do total. Deve percorrer documento, requisitos, especificacao, dados, "
             "UI, agentes/tarefas, YAML, registro e atribuicao das duas tools MCP, sequencia, Petri, geracao, "
             "testes, aplicacao e gate. Mostrar pelo menos uma falha ou lacuna registrada e nao esconder o que "
             "continua em desenvolvimento. A especificacao aparece no inicio e o rastro no fim. (~15 min)")


def build_v2():
    base.META = []
    prs = D.new_prs()
    funcs = [base.s1, s2, base.s3, base.s4, base.s5, base.s5b, base.s5c, base.s6, base.s7, base.s8, base.s9, base.s10, base.s11, base.s12, base.s13,
             base.s14, base.s15, base.s16, base.s17, base.s18, base.s19, base.s20, base.s21, base.s22b, base.s23, base.s24, base.s25, base.s26, base.s27, base.s28,
             base.s29, base.s30, base.s31, base.s32, base.s33, base.s_intervalo, base.s34, base.s35, base.s36, base.s37, s38, s39, base.s40,
             base.s41, base.s42, base.s43, base.s44, base.s45, base.s46, base.s47, base.s48, base.s49, base.s50, base.s51, base.s52,
             base.s53, base.s54, base.s55, base.s56, base.s57, s58, s59, s60, s61, base.s62, base.s63, base.s64, base.s65, base.s66, base.s67]
    for fn in funcs:
        fn(prs)
    fit_timing()
    out = os.path.join("output", "apresentacao_iasdd_v2_biobyte.pptx")
    prs.save(out)
    fix_visible_slide_numbers(out)
    print("PPTX:", out, "slides:", len(prs.slides), "tempo:", sum(x["minutes"] for x in base.META), "min")
    try:
        pdf, pages = D.render_companion_pdf(out, base.META,
            os.path.join("output", "apresentacao_iasdd_v2_biobyte_roteiro.pdf"),
            os.path.join("output", "_work_iasdd_v2_biobyte"))
        print("PDF roteiro:", pdf, "paginas:", pages)
    except Exception as exc:
        print("PDF roteiro nao gerado:", exc)


if __name__ == "__main__":
    build_v2()

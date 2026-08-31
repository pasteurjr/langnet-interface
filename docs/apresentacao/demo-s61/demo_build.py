# -*- coding: utf-8 -*-
"""SCRIPT DE VÍDEO — passeio guiado pelo menu lateral do pipeline (LangNet / Uso do Solo).
Ordem = navegação real: Projetos -> Menu lateral -> cada etapa (a TELA + o DOCUMENTO) -> Rastreabilidade -> App.
Por cena: NARRAÇÃO (fala EXATA p/ locução, siglas soletradas) + PRODUÇÃO (menu/funções/o que mostrar)
+ TRECHO real do documento quando houver. Estilo demonstrativo. Gera MD e PDF."""
import os, html, weasyprint

HERE = os.path.dirname(__file__)
RS = os.path.join(HERE, "real_shots")
APP = os.path.join(HERE, "..", "..", "uso-do-solo", "validacao-final", "shots")
def im(*p): return os.path.abspath(os.path.join(*p))
def rs(n): return im(RS, n)

SC = [
 dict(n=1, cena="O sistema e os projetos", dur=13, imgs=[rs("A0_projetos.png")],
   narr="Esta é uma demonstração de Desenvolvimento Orientado a Especificação — o S D D — na ferramenta "
        "LangNet. Aqui estão os projetos: cada projeto percorre um pipeline completo, do requisito ao código "
        "rastreável. Vamos abrir o projeto de gestão do uso do solo.",
   prod="Tela Projetos (11 projetos). Um clique curto no card “Uso do Solo v3 / Abrir Projeto”. Não se demore.",
   trecho=None),

 dict(n=2, cena="O menu lateral — as etapas do pipeline", dur=22, imgs=[rs("sidebar.png")],
   narr="Ao abrir o projeto, o menu lateral revela o pipeline inteiro. Cada item é uma etapa, na ordem: "
        "Documentos, onde tudo começa; Especificação; Modelo de Dados; Interface e Protótipo; Agentes e Tarefas; "
        "o YAML de Agentes e Tarefas; a Sequência de Tarefas; a Rede de Petri; a Geração de Código; e os Casos "
        "de Teste e Validação. As etapas de Deploy e Monitoramento fecham a operação. Vamos entrar em cada uma.",
   prod="Barra lateral do projeto em foco, mostrando a seção PIPELINE (Documentos … Casos de Teste) e a seção "
        "OPERAÇÃO (Deploy, Monitoramento). Percorra os itens de cima a baixo com um leve destaque.",
   trecho=None),

 dict(n=3, cena="Documentos — a origem e o documento de Requisitos", dur=30,
   imgs=[rs("doc_stage.png"), rs("req_fr.png"), rs("req_nfr.png")],
   narr="A primeira etapa é Documentos. Aqui você traz os arquivos de origem — inclusive a legislação municipal — "
        "escreve instruções de análise no painel e inicia a geração. O resultado é o documento de Requisitos. "
        "Ele traz os requisitos funcionais, o que o sistema deve fazer, cada um com prioridade; e os "
        "não-funcionais, as metas de qualidade. Repare no requisito F R zero dezesseis, o cálculo do coeficiente "
        "de aproveitamento: é ele que vamos seguir até o código.",
   prod="Tela Documentos: lista de arquivos-fonte, campo “Instruções para Análise”, “Pesquisa Web” e “🚀 Iniciar "
        "Análise”. Depois, abra o documento de Requisitos e role pela tabela de Requisitos Funcionais (destaque "
        "FR-016 “Cálculo de CA”) e pela de Requisitos Não-Funcionais.",
   trecho="REQUISITOS FUNCIONAIS (trecho real do documento)\n"
          "  FR-014  Parâmetros urbanísticos por zona                 Alta\n"
          "  FR-015  Zoneamento poligonal                             Alta\n"
          "  FR-016  Cálculo de CA (Coeficiente de Aproveitamento)    Alta   <= nosso fio condutor\n"
          "  FR-017  Cálculo de TO (Taxa de Ocupação)                 Alta\n"
          "  FR-018  Cálculo e Validação de Recuos                    Alta\n\n"
          "REQUISITOS NÃO-FUNCIONAIS (trecho real)\n"
          "  NFR-001  Escalabilidade   100 municípios simultâneos\n"
          "  NFR-002  Performance      Latência do mapa < 5 s\n"
          "  NFR-003  Usabilidade      Tarefa principal ≤ 3 min\n"
          "  NFR-005  Confiabilidade   Uptime 99,5%"),

 dict(n=4, cena="Especificação — casos de uso e fluxos", dur=30,
   imgs=[rs("spec_stage.png"), rs("S_uc.png"), rs("S_flux.png")],
   narr="Dos requisitos deriva a Especificação Funcional — o documento primário do S D D. Ela detalha os casos "
        "de uso. Cada caso de uso traz o ator, o objetivo, os requisitos relacionados e três fluxos: o principal, "
        "o passo a passo normal; os alternativos, os caminhos válidos diferentes; e os de exceção, o tratamento "
        "de erros. Veja o caso de uso zero zero um: no fluxo principal o sistema calcula o coeficiente, dá dois "
        "vírgula cinco contra o limite de dois, e conclui não conforme. E ele está ligado, explicitamente, ao "
        "requisito F R zero dezesseis.",
   prod="Tela Especificação (painel de config com Gerar/Revisar). Depois o documento, no UC-001: a tabela com "
        "Ator, Objetivo e “RFs Relacionados: FR-016…”, e então os Fluxos Alternativos e de Exceção.",
   trecho="UC-001 — Consulta de Conformidade Consolidada (trecho real)\n"
          "  RFs Relacionados: FR-016, FR-017, FR-018, FR-019, FR-020…\n"
          "  Fluxo Principal (passo 2): CA = 500 m² / 200 m² = 2,5 · limite 2,0 → NÃO CONFORME\n"
          "  Fluxos Alternativos:  A1 sobreposição com APP (12,5 m²)   A2 “Simular” → 400 m² → CA 2,0 → CONFORME\n"
          "  Fluxos de Exceção:    E1 geometria inválida → Editor de Mapas   E2 zona sem parâmetros → Notificar"),

 dict(n=5, cena="Modelo de Dados", dur=20, imgs=[rs("dm_stage.png")],
   narr="Da especificação deriva o Modelo de Dados. A ferramenta gera as entidades, o esquema, os modelos e as "
        "migrações — aqui, um banco geográfico. Repare na tabela de parâmetros urbanísticos por zona, com o "
        "coeficiente máximo e a taxa de ocupação: é dela que o cálculo do requisito F R zero dezesseis vai ler "
        "os limites. E o sistema ainda valida o esquema automaticamente.",
   prod="Tela Modelo de Dados: à esquerda o painel (DBMS PostgreSQL, Regenerar/Revisar/Refinar); à direita as "
        "entidades — destaque “parametros_urbanisticos” com ca_maximo e to_maxima, e a coluna geometria.",
   trecho="Entidade parametros_urbanisticos (trecho real)\n"
          "  ca_maximo        DECIMAL(10,2)      -- limite de CA por zona (FR-016)\n"
          "  to_maxima        DECIMAL(10,2)      -- limite de TO por zona (FR-017)\n"
          "  zoneamentos.geometria  geometry(Geometry, 4674)   -- PostGIS · SIRGAS 2000"),

 dict(n=6, cena="Interface & Protótipo", dur=16, imgs=[rs("ui_stage.png"), rs("03_ui_spec.png")],
   narr="Antes do código, a ferramenta gera o protótipo de interface — uma tela para cada caso de uso. Cada tela "
        "nasce amarrada ao seu caso de uso; esta, de resultado de conformidade, é o mesmo caso de uso zero zero "
        "um que acabamos de ver.",
   prod="Tela Interface e Protótipo: à esquerda a lista de telas e o painel “Gerar UI Spec”; à direita o mockup "
        "da tela de conformidade (mapa + resumo de CA/TO/APP).",
   trecho=None),

 dict(n=7, cena="Agentes & Tarefas", dur=17, imgs=[rs("at_stage.png"), rs("05_agent_task.png")],
   narr="Agora a ferramenta define a arquitetura de execução: quais agentes existem e quais tarefas cada um "
        "realiza, e sob qual framework. É a ponte entre o que o sistema deve fazer e como ele fará — cada tarefa "
        "já apontando para o caso de uso e os requisitos que atende.",
   prod="Tela Agentes e Tarefas: o painel (Nível de Detalhamento, framework CrewAI, “Gerar Agentes & Tarefas”) e "
        "o documento de especificação de agentes e tarefas com a lista de agentes.",
   trecho=None),

 dict(n=8, cena="YAML de Agentes e Tarefas — a rastreabilidade impressa", dur=20,
   imgs=[rs("yaml_stage.png"), rs("06_yaml_tasks.png")],
   narr="A especificação de agentes e tarefas vira arquivos executáveis: o agents ponto yaml e o tasks ponto "
        "yaml. Aqui está o coração do S D D: cada tarefa carrega a própria rastreabilidade. A tarefa que calcula "
        "a conformidade traz, escrito no arquivo, o caso de uso zero zero um e os requisitos F R zero dezesseis "
        "a dezenove. O requisito não se perdeu — está impresso dentro da tarefa que o executa.",
   prod="Tela YAML (painel “Gerar agents.yaml/tasks.yaml”). No tasks.yaml, enquadre a task "
        "calculate_urban_compliance e destaque a linha de traceability e o campo execution.",
   trecho="calculate_urban_compliance:\n"
          "  traceability: { uc: UC-001, fr: [FR-016, FR-017, FR-018, FR-019] }\n"
          "  execution: deterministic\n"
          "  agent: calculo_urbano_agent"),

 dict(n=9, cena="Sequência de Tarefas", dur=13, imgs=[rs("seq_stage.png")],
   narr="Com os agentes e tarefas prontos, a ferramenta organiza a Sequência de Tarefas: a ordem em que elas "
        "são executadas para cumprir cada caso de uso, ligando entradas e saídas de uma tarefa à seguinte.",
   prod="Tela Sequência de Tarefas: o painel de geração e a origem “Specs & Docs”. Mostre rapidamente que ela "
        "encadeia as tarefas do fluxo.",
   trecho=None),

 dict(n=10, cena="Rede de Petri", dur=15, imgs=[rs("petri_stage.png")],
   narr="Essa sequência é formalizada como uma Rede de Petri. Cada transição é uma tarefa; os tokens percorrem a "
        "rede do início ao fim. É uma orquestração que pode ser verificada formalmente, e não apenas testada.",
   prod="Editor da Rede de Petri: o lugar “Início do Fluxo” com o token, as transições (as tarefas) e o “Fim do "
        "Fluxo”. Opcional: um clique em Simular para o token avançar.",
   trecho=None),

 dict(n=11, cena="Geração de Código", dur=18, imgs=[rs("code_stage.png"), rs("12_code_real.png")],
   narr="Só então vem o código — o artefato derivado. A ferramenta gera o projeto inteiro, dezenas de arquivos. "
        "E aqui está a função que calcula a conformidade: a consulta espacial e a classificação em conforme ou "
        "não conforme. É o requisito F R zero dezesseis, que vimos no começo, agora rodando.",
   prod="Tela Geração de Código: a árvore de arquivos à esquerda e o editor à direita. Depois, enquadre a função "
        "calculate_urban_compliance, com o JOIN espacial e a linha do status conforme / não conforme.",
   trecho=None),

 dict(n=12, cena="Casos de Teste & Validação", dur=18, imgs=[rs("tests_stage.png")],
   narr="Os casos de teste nascem dos casos de uso, pela técnica do grafo de causa e efeito. As causas são as "
        "ações do usuário; os efeitos, as respostas do sistema. No S D D isto é essencial: o teste deriva do "
        "critério, não do código — por isso não herda os defeitos da implementação.",
   prod="Tela Casos de Teste: a lista de casos de uso à esquerda e, à direita, o Grafo de Causa-Efeito do UC-001, "
        "com as causas e efeitos ligados.",
   trecho=None),

 dict(n=13, cena="Rastreabilidade verificada", dur=16, imgs=[rs("gate_verde.png")],
   narr="E a ferramenta prova essa cadeia. A matriz de rastreabilidade liga cada requisito ao caso de uso que o "
        "realiza; e o portão de rastreabilidade verifica automaticamente que todos os trinta e sete requisitos "
        "atravessam a especificação, o modelo de dados e a implementação. Nenhum requisito órfão.",
   prod="Mostre o portão de rastreabilidade em VERDE — 37 de 37, todos os saltos OK. Congele por 3 segundos.",
   trecho="Matriz de Rastreabilidade (trecho real)\n"
          "  FR-016 → Especificação 5.2 / UC-001 → realizado por UC-001 → task calculate_urban_compliance\n"
          "  FR-015 → UC-005 (Zoneamento)   ·   FR-005 / FR-007 → UC-004 (Legislação com IA)\n"
          "  Portão: 37/37 · Req→Spec, Matriz FR→UC, FR→Implementação, Task→código: OK"),

 dict(n=14, cena="A aplicação gerada", dur=16, imgs=[im(APP, "01-app-home.png")],
   narr="E este é o resultado: a aplicação gerada, rodando. O mesmo cálculo de conformidade que rastreamos desde "
        "o requisito — área, coeficiente, veredito — agora funcionando sobre um mapa real. Da especificação ao "
        "software, rastreável de ponta a ponta. Isto é o S D D, na ferramenta LangNet.",
   prod="Aplicação gerada no navegador: a tela inicial e o resultado de conformidade. Se der, um cálculo rápido "
        "resultando em “conforme”. Encerre com o título.",
   trecho=None),
]

TOTAL = sum(s["dur"] for s in SC)
def fmt(t): return "%d:%02d" % (t // 60, t % 60)
CUM = []; acc = 0
for s in SC: CUM.append(acc); acc += s["dur"]

def build_md():
    L = ["# Script de Vídeo — Passeio pelo pipeline SDD na ferramenta LangNet (projeto Uso do Solo)\n",
         "**Formato:** script para locução automática. **NARRAÇÃO** = fala EXATA a ser lida (siglas soletradas). "
         "**PRODUÇÃO** = o que mostrar (menu lateral, funções, onde se escreve). **TRECHO DO DOCUMENTO** = parte "
         "real a exibir. Estilo demonstrativo. **Ordem = navegação real.** **Duração:** ~%s (14 cenas).\n"
         % fmt(TOTAL),
         "\n| Cena | Etapa do pipeline | Entra | Dura |\n|---|---|---|---|"]
    for i, s in enumerate(SC):
        L.append("| %d | %s | %s | %ds |" % (s["n"], s["cena"], fmt(CUM[i]), s["dur"]))
    L.append("\n---\n")
    for i, s in enumerate(SC):
        L.append("## Cena %d · %s   (%s → %s · %ds)\n" % (s["n"], s["cena"], fmt(CUM[i]), fmt(CUM[i] + s["dur"]), s["dur"]))
        if s["imgs"]: L.append("**Telas:** %s\n" % ", ".join("`%s`" % os.path.basename(x) for x in s["imgs"]))
        L.append("**🎙 NARRAÇÃO (fala exata):**\n\n> %s\n" % s["narr"])
        L.append("**🎬 PRODUÇÃO:** %s\n" % s["prod"])
        if s["trecho"]:
            L.append("**📄 TRECHO DO DOCUMENTO (exibir na tela):**\n\n```\n%s\n```\n" % s["trecho"])
        L.append("\n---\n")
    L.append("## Locução corrida (só as falas, para colar no gerador de voz)\n")
    L.append("\n".join(s["narr"] for s in SC))
    open(os.path.join(HERE, "script_video_sdd_langnet.md"), "w", encoding="utf-8").write("\n".join(L))

def build_pdf():
    def esc(s): return html.escape(s)
    css = """
    @page { size: A4; margin: 1.0cm 1.2cm; }
    body { font-family:'Liberation Sans',sans-serif; color:#161e33; font-size:11px; }
    .cover { text-align:center; padding-top:14px; }
    .cover h1 { font-size:20px; color:#4f46e5; margin-bottom:4px; }
    .cover p { color:#5a667e; margin:2px; font-size:11px; }
    .tl { width:100%; border-collapse:collapse; margin:10px 0; font-size:10px; }
    .tl th { background:#4f46e5; color:#fff; padding:5px 6px; text-align:left; }
    .tl td { border-bottom:1px solid #e2e7f0; padding:4px 6px; }
    .tl tr:nth-child(even) td { background:#f4f6fb; }
    .sc { page-break-inside: avoid; margin-bottom: 14px; border:1px solid #e2e7f0; border-radius:10px; overflow:hidden; }
    .hd { background:#4f46e5; color:#fff; padding:7px 12px; display:flex; justify-content:space-between; align-items:center; }
    .ti { font-size:14px; font-weight:bold; }
    .tm { background:rgba(255,255,255,.22); border-radius:10px; padding:2px 9px; font-weight:bold; font-size:11px; }
    .in { padding:10px 13px; }
    .im { width:100%; border-radius:6px; box-shadow:0 1px 5px rgba(20,26,50,.14); margin-bottom:7px; }
    .narlab,.prodlab,.exlab { font-weight:bold; font-size:10px; letter-spacing:.3px; margin:8px 0 3px; }
    .narlab { color:#7c3aed; } .prodlab { color:#0d9488; } .exlab { color:#c76a00; }
    .nar { background:#f2eafe; border-left:4px solid #7c3aed; padding:10px 13px; border-radius:0 7px 7px 0;
           font-size:13px; line-height:1.55; color:#1a1030; }
    .prod { font-size:11px; line-height:1.45; color:#334; }
    .ex { background:#12182f; color:#e8edfa; font-family:'DejaVu Sans Mono',monospace; font-size:9px;
          padding:9px 12px; border-radius:6px; white-space:pre-wrap; line-height:1.4; }
    """
    rows = "".join("<tr><td><b>%d</b></td><td>%s</td><td>%s</td><td>%ds</td></tr>"
                   % (s["n"], esc(s["cena"]), fmt(CUM[i]), s["dur"]) for i, s in enumerate(SC))
    body = ['<div class="cover"><h1>Script de Vídeo — Pipeline SDD na ferramenta LangNet</h1>'
            '<p>Passeio guiado pelo menu lateral · projeto de exemplo <b>Uso do Solo</b> · telas reais do sistema</p>'
            '<p><b>NARRAÇÃO</b> = fala exata (locução automática) · <b>PRODUÇÃO</b> = o que mostrar / menu / funções '
            '· <b>TRECHO</b> = parte real do documento a exibir.</p>'
            '<p style="color:#c76a00"><b>Duração:</b> ~%s · 14 cenas · ordem = navegação real</p>'
            '<table class="tl"><tr><th>Cena</th><th>Etapa do pipeline</th><th>Entra</th><th>Dura</th></tr>%s</table>'
            '<div style="page-break-after:always"></div>' % (fmt(TOTAL), rows)]
    for i, s in enumerate(SC):
        imgs = "".join('<img class="im" src="file://%s"/>' % x for x in s["imgs"])
        ex = ('<div class="exlab">📄 TRECHO DO DOCUMENTO (exibir na tela)</div><div class="ex">%s</div>'
              % esc(s["trecho"])) if s["trecho"] else ""
        body.append(
            '<div class="sc"><div class="hd">'
            '<span class="ti">Cena %d · %s</span>'
            '<span class="tm">%s → %s · %ds</span></div>'
            '<div class="in">%s'
            '<div class="narlab">🎙 NARRAÇÃO — fala exata</div><div class="nar">%s</div>'
            '<div class="prodlab">🎬 PRODUÇÃO — o que mostrar (menu lateral, funções, onde se escreve)</div>'
            '<div class="prod">%s</div>%s'
            '</div></div>' % (s["n"], esc(s["cena"]), fmt(CUM[i]), fmt(CUM[i] + s["dur"]), s["dur"],
                              imgs, esc(s["narr"]), esc(s["prod"]), ex))
    doc = "<html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>" % (css, "".join(body))
    weasyprint.HTML(string=doc, base_url=HERE).write_pdf(os.path.join(HERE, "script_video_sdd_langnet.pdf"))

build_md(); build_pdf()
print("OK:", fmt(TOTAL), "· 14 cenas")

# -*- coding: utf-8 -*-
"""SCRIPT DE VÍDEO (didático) — passeio pelo pipeline SDD na ferramenta LangNet (projeto Uso do Solo).
Ordem = navegação real: Projetos -> Configurações (Framework+Protocolo) -> Menu lateral ->
cada etapa (a TELA + PARTES do DOCUMENTO, explicadas) -> Rastreabilidade -> App.
Por cena: NARRAÇÃO (fala EXATA p/ locução, siglas soletradas) + PRODUÇÃO (menu/funções/o que mostrar)
+ TRECHO real do documento (as partes mais importantes). Gera MD e PDF."""
import os, html, weasyprint

HERE = os.path.dirname(__file__)
RS = os.path.join(HERE, "real_shots")
APP = os.path.join(HERE, "..", "..", "uso-do-solo", "validacao-final", "shots")
def im(*p): return os.path.abspath(os.path.join(*p))
def rs(n): return im(RS, n)

SC = [
 dict(n=1, cena="O sistema e os projetos", dur=12, imgs=[rs("A0_projetos.png")],
   narr="Esta é uma demonstração de Desenvolvimento Orientado a Especificação — o S D D — na ferramenta "
        "LangNet. Aqui estão os projetos: cada um percorre um pipeline completo, do requisito ao código "
        "rastreável. Vamos abrir o projeto de gestão do uso do solo.",
   prod="Tela Projetos (11 projetos). Um clique curto no card “Uso do Solo v3”. Não se demore.",
   trecho=None),

 dict(n=2, cena="Configurações do Projeto — Framework e Protocolo", dur=22, imgs=[rs("config_create.png")],
   narr="Antes de tudo, cada projeto define sua arquitetura. Nas configurações você escolhe o framework de "
        "agentes: o nosso padrão é o CrewAI, mas também há LangChain, LangGraph, AutoGen e os S D Ks da OpenAI "
        "e da Anthropic. E escolhe o protocolo de interoperabilidade entre agentes: o nosso padrão é o O K F, "
        "com opções para M C P, A dois A, A C P e A N P. É aqui que se decide sobre qual base o sistema será "
        "gerado.",
   prod="Modal “Criar Novo Projeto” (o mesmo abre em “Editar”, nas Configurações do Projeto). Em Opções "
        "Avançadas, destaque os dois seletores: Framework (CrewAI — padrão) e Protocolo (OKF — padrão). "
        "Abra rapidamente cada um para mostrar as opções.",
   trecho="Framework (padrão CrewAI):  CrewAI · LangChain · LangGraph · AutoGen · OpenAI SDK · Anthropic SDK\n"
          "Protocolo (padrão OKF):     OKF (nosso) · MCP · A2A · ACP · ANP"),

 dict(n=3, cena="O menu lateral — as etapas do pipeline", dur=20, imgs=[rs("sidebar.png")],
   narr="Ao abrir o projeto, o menu lateral revela o pipeline inteiro. Cada item é uma etapa, na ordem: "
        "Documentos, onde tudo começa; Especificação; Modelo de Dados; Interface e Protótipo; Agentes e Tarefas; "
        "o YAML de Agentes e Tarefas; a Sequência de Tarefas; a Rede de Petri; a Geração de Código; e os Casos "
        "de Teste e Validação. Deploy e Monitoramento fecham a operação. Vamos entrar em cada uma e ver o que "
        "cada documento contém.",
   prod="Barra lateral do projeto, seção PIPELINE (Documentos … Casos de Teste) + OPERAÇÃO. Percorra de cima a "
        "baixo com leve destaque.",
   trecho=None),

 dict(n=4, cena="Documentos — o documento de Requisitos", dur=36,
   imgs=[rs("doc_stage.png"), rs("req_fr.png"), rs("req_nfr.png")],
   narr="A primeira etapa é Documentos. Você traz os arquivos de origem — inclusive a legislação municipal — e "
        "a ferramenta gera o documento de Requisitos. Ele tem três partes que importam. Primeiro, os requisitos "
        "funcionais: o que o sistema deve fazer, cada um com identificador e prioridade — repare no F R zero "
        "dezesseis, o cálculo do coeficiente de aproveitamento, que vamos seguir até o código. Segundo, os "
        "não-funcionais: as metas de qualidade, como escalar para cem municípios, mapa em menos de cinco "
        "segundos e precisão geométrica. E terceiro, algo que costuma passar batido: a ferramenta detecta "
        "conflitos e ambiguidades entre os documentos de origem, e propõe a resolução — aqui, por exemplo, "
        "unificar o sistema de coordenadas.",
   prod="Tela Documentos: arquivos-fonte + “🚀 Iniciar Análise”. Depois abra o documento de Requisitos: role "
        "pela tabela de Requisitos Funcionais (destaque FR-016), pela de Não-Funcionais, e pela seção "
        "“Verificações Complementares” (conflitos e ambiguidades detectados).",
   trecho="REQUISITOS FUNCIONAIS (trecho real)          |  NÃO-FUNCIONAIS (trecho real)\n"
          "  FR-015  Zoneamento poligonal        Alta   |   NFR-001  Escalabilidade  100 municípios\n"
          "  FR-016  Cálculo de CA (Coef. Aprov.) Alta  |   NFR-002  Performance     mapa < 5 s\n"
          "  FR-017  Cálculo de TO               Alta   |   NFR-003  Usabilidade     tarefa ≤ 3 min\n"
          "  FR-018  Cálculo e Validação de Recuos Alta |   NFR-013  Precisão geom.  < 0,01 m (SRID 4674)\n\n"
          "VERIFICAÇÕES COMPLEMENTARES (a ferramenta detecta e resolve):\n"
          "  CON-002  Diferença de SRID entre v2 e v3  → Resolução: adotar SRID 4674 (SIRGAS 2000)\n"
          "  AMB-001  “Agentes de IA” (FR-005) é vago  → Pergunta: qual tecnologia de IA será usada?"),

 dict(n=5, cena="Especificação — casos de uso, fluxos e matriz", dur=40,
   imgs=[rs("S_uc.png"), rs("S_flux.png"), rs("spec_matriz.png")],
   narr="Dos requisitos deriva a Especificação Funcional — o documento primário do S D D. Ela detalha os casos "
        "de uso. Cada caso de uso traz o ator, o objetivo, os requisitos relacionados e três fluxos: o "
        "principal, o passo a passo normal; os alternativos, os caminhos válidos diferentes; e os de exceção, o "
        "tratamento de erros. No caso de uso zero zero um, o fluxo principal calcula o coeficiente, dá dois "
        "vírgula cinco contra o limite de dois, e conclui não conforme; um fluxo alternativo permite simular um "
        "ajuste e voltar a conforme. E, ao final, a especificação traz a matriz de rastreabilidade, que liga "
        "cada requisito ao caso de uso que o realiza. É esta matriz que garante que nada se perde.",
   prod="Documento de Especificação. Mostre o UC-001: tabela com Ator, Objetivo e “RFs Relacionados: FR-016…”; "
        "depois os Fluxos Alternativos e de Exceção; e por fim role até a seção 13, a Matriz de Rastreabilidade "
        "(Requisito → UC que o realiza).",
   trecho="UC-001 — Consulta de Conformidade Consolidada (trecho real)\n"
          "  RFs Relacionados: FR-016, FR-017, FR-018, FR-019…    RNs: BR-006, BR-007\n"
          "  Fluxo Principal (passo 2): CA = 500 m² / 200 m² = 2,5 · limite 2,0 → NÃO CONFORME\n"
          "  Alternativos: A2 “Simular” → 400 m² → CA 2,0 → CONFORME   |  Exceção: E1 geometria inválida\n\n"
          "MATRIZ DE RASTREABILIDADE (seção 13, trecho real)\n"
          "  Requisito | Seção Espec. | UC que o realiza | RN\n"
          "  FR-001    | 5.2, UC-001  | UC-001           | RN-002\n"
          "  FR-016    | 5.2, UC-001  | UC-001           | (cálculo de CA)"),

 dict(n=6, cena="Modelo de Dados", dur=22, imgs=[rs("dm_stage.png")],
   narr="Da especificação deriva o Modelo de Dados: as entidades, o esquema, os modelos e as migrações — aqui, "
        "um banco geográfico. Três tabelas contam a história: municípios, a raiz; zoneamentos, com a coluna de "
        "geometria em coordenadas oficiais; e parâmetros urbanísticos, que guarda, por zona, o coeficiente "
        "máximo e a taxa de ocupação. É desta última que o cálculo do F R zero dezesseis lê os limites. E o "
        "sistema valida o esquema automaticamente.",
   prod="Tela Modelo de Dados: à esquerda o painel (DBMS PostgreSQL, Regenerar/Revisar); à direita as entidades. "
        "Destaque “zoneamentos.geometria” e “parametros_urbanisticos” (ca_maximo, to_maxima). Se der, abra a aba "
        "“Schema SQL”.",
   trecho="Modelo de Dados (trecho real)\n"
          "  zoneamentos.geometria        geometry(Geometry, 4674)   -- PostGIS · SIRGAS 2000\n"
          "  parametros_urbanisticos.ca_maximo   DECIMAL(10,2)       -- limite de CA por zona (FR-016)\n"
          "  parametros_urbanisticos.to_maxima   DECIMAL(10,2)       -- limite de TO por zona (FR-017)\n"
          "  (o cálculo faz JOIN zoneamentos × parametros × imoveis via ST_Contains da geometria)"),

 dict(n=7, cena="Interface & Protótipo", dur=16, imgs=[rs("ui_stage.png"), rs("03_ui_spec.png")],
   narr="Antes do código, a ferramenta gera o protótipo de interface — uma tela para cada caso de uso. Cada "
        "tela nasce amarrada ao seu caso de uso; esta, de resultado de conformidade, é o mesmo caso de uso "
        "zero zero um, com o mapa e o resumo do coeficiente, da ocupação e da preservação.",
   prod="Tela Interface e Protótipo: à esquerda a lista de telas e o painel “Gerar UI Spec”; à direita o mockup "
        "da tela de conformidade (mapa + cards de CA/TO/APP).",
   trecho=None),

 dict(n=8, cena="Agentes & Tarefas", dur=20, imgs=[rs("at_stage.png"), rs("05_agent_task.png")],
   narr="Agora a ferramenta define a arquitetura de execução: quais agentes existem e quais tarefas cada um "
        "realiza. São dez agentes e trinta tarefas. Cada agente é um especialista — por exemplo, o Motor de "
        "Cálculo Urbanístico — e cada tarefa já aponta para o caso de uso e os requisitos que atende. É a ponte "
        "entre o que o sistema deve fazer e como ele fará.",
   prod="Tela Agentes e Tarefas: o painel (Nível de Detalhamento, framework, “Gerar Agentes & Tarefas”) e o "
        "documento com a tabela de agentes (AG-01 a AG-10) e as tarefas com seu UC/RF.",
   trecho="Especificação de Agentes & Tarefas (trecho real)\n"
          "  Agente: calculo_urbano_agent — “Motor de Cálculo Urbanístico”\n"
          "  Tarefa: calculate_urban_compliance → UC-001 · FR-016..FR-019 · execução determinística"),

 dict(n=9, cena="YAML de Agentes e Tarefas — a rastreabilidade impressa", dur=26,
   imgs=[rs("yaml_stage.png"), rs("04_yaml_agents.png"), rs("06_yaml_tasks.png")],
   narr="A especificação vira arquivos executáveis: o agents ponto yaml e o tasks ponto yaml. No agents, cada "
        "agente ganha papel, objetivo e história — veja o Motor de Cálculo, um engenheiro que é determinístico: "
        "se o número não bate, é não conforme. E no tasks está o coração do S D D: cada tarefa carrega a própria "
        "rastreabilidade. A tarefa de conformidade traz, escrito no arquivo, o caso de uso zero zero um e os "
        "requisitos F R zero dezesseis a dezenove — e até a consulta espacial que ela executa. O requisito não "
        "se perdeu: está impresso dentro da tarefa.",
   prod="Tela YAML. Mostre o agents.yaml (agente calculo_urbano_agent: role/goal/backstory) e depois o "
        "tasks.yaml (task calculate_urban_compliance: traceability, execution e a query com o JOIN espacial).",
   trecho="agents.yaml (trecho real)                 |  tasks.yaml (trecho real)\n"
          "calculo_urbano_agent:                     |  calculate_urban_compliance:\n"
          "  role: Motor de Cálculo Urbanístico      |    traceability: { uc: UC-001, fr: [FR-016..FR-019] }\n"
          "  goal: Calcular e validar CA, TO,        |    execution: deterministic\n"
          "        Recuos e Gabarito                 |    agent: calculo_urbano_agent\n"
          "  backstory: engenheiro civil…            |    query: SELECT … FROM zoneamentos z\n"
          "    “se o número não bate, é NÃO CONFORME”|      JOIN parametros_urbanisticos p ON p.zona_id=z.id\n"
          "                                          |      … WHERE ST_Contains(z.geometria, i.geometria)"),

 dict(n=10, cena="Sequência de Tarefas", dur=22, imgs=[rs("seq_stage.png"), rs("seq_doc.png")],
   narr="Antes da Rede de Petri vem uma etapa essencial, que deriva diretamente dos agentes e das tarefas: a "
        "Sequência de Tarefas. Ela define a ordem exata de execução — aqui, quinze tarefas. Começa importando "
        "os geodados do zoneamento e dos imóveis, passa pelo cálculo de conformidade, que é a tarefa seis, o "
        "nosso F R zero dezesseis, e segue até o laudo. A ferramenta identifica o que pode rodar em paralelo e "
        "liga a saída de cada tarefa à entrada da seguinte, num estado compartilhado. É esta sequência — e não "
        "um salto — que alimenta a Rede de Petri.",
   prod="Tela Sequência de Tarefas: o painel (origem “Specs & Docs”, Gerar/Revisar) e, à direita, o fluxo "
        "gerado “task_flow … v1”. Abra o Histórico para mostrar “Concluído · 15 tarefas · Paralelismo: Sim”. "
        "Role o documento do fluxo pela lista ordenada de tarefas.",
   trecho="Fluxo de Execução — Sequência de Tarefas (trecho real · 15 tarefas · com paralelismo)\n"
          "  Task 1  import_zoneamento_geodata      → geodados_import_agent   (importação inicial)\n"
          "  Task 2  import_imoveis_geodata         → geodados_import_agent\n"
          "  Task 4  update_parametros_urbanisticos → parâmetros CA/TO por zona\n"
          "  Task 6  calculate_urban_compliance     → calculo_urbano_agent   (UC-001 · FR-016)\n"
          "  Task 7  calculate_app_overlap          → cálculo espacial de APP\n"
          "  …                                       (a saída de cada tarefa entra no State da seguinte)"),

 dict(n=11, cena="Rede de Petri", dur=14, imgs=[rs("petri_stage.png")],
   narr="Essa sequência é formalizada como uma Rede de Petri. Cada transição é uma tarefa; os tokens percorrem "
        "a rede do início ao fim. É uma orquestração que pode ser verificada formalmente, e não apenas testada.",
   prod="Editor da Rede de Petri: o “Início do Fluxo” com o token, as transições (tarefas) e o “Fim do Fluxo”. "
        "Opcional: um clique em Simular para o token avançar.",
   trecho=None),

 dict(n=12, cena="Geração de Código", dur=20, imgs=[rs("code_stage.png"), rs("12_code_real.png")],
   narr="Só então vem o código — o artefato derivado. A ferramenta gera o projeto inteiro, dezenas de arquivos. "
        "E aqui está a função que calcula a conformidade: a mesma consulta espacial da tarefa, com o JOIN entre "
        "a geometria do lote e a zona, e a classificação em conforme ou não conforme. É o requisito F R zero "
        "dezesseis, que vimos no começo, agora executável.",
   prod="Tela Geração de Código: a árvore de arquivos à esquerda e o editor à direita. Enquadre a função "
        "calculate_urban_compliance, com o JOIN espacial e a linha do status conforme / não conforme.",
   trecho="Código gerado (trecho real)\n"
          "  def calculate_urban_compliance(imovel_id):\n"
          "      SELECT z.nome, p.ca_maximo, p.to_maxima FROM zoneamentos z\n"
          "        JOIN parametros_urbanisticos p ON p.zona_id = z.id\n"
          "        JOIN imoveis i ON i.id = %s WHERE ST_Contains(z.geometria, i.geometria)\n"
          "      ca = area_construida / area_terreno\n"
          "      status = 'conforme' if ca <= ca_maximo else 'nao_conforme'"),

 dict(n=13, cena="Casos de Teste & Validação", dur=18, imgs=[rs("tests_stage.png")],
   narr="Os casos de teste nascem dos casos de uso, pela técnica do grafo de causa e efeito. As causas são as "
        "ações do usuário; os efeitos, as respostas do sistema; e cada combinação vira um caso de teste. No S D "
        "D isto é essencial: o teste deriva do critério, não do código — por isso não herda os defeitos da "
        "implementação. Aqui, do caso de uso zero zero um saem cinco causas, seis efeitos e seis casos de teste.",
   prod="Tela Casos de Teste: a lista de casos de uso à esquerda e, à direita, o Grafo de Causa-Efeito do "
        "UC-001, com as causas e efeitos ligados e a contagem de casos.",
   trecho="Grafo de Causa-Efeito — UC-001 (trecho real)\n"
          "  Causas (ações): c1 selecionar imóvel · c2 geometria válida · c3 zona com parâmetros\n"
          "  Efeitos (respostas): e1 CA calculado · e2 status conforme/não conforme · e3 laudo gerado\n"
          "  → 5 causas · 6 efeitos · 6 casos de teste derivados"),

 dict(n=14, cena="Rastreabilidade verificada", dur=16, imgs=[rs("gate_verde.png")],
   narr="E a ferramenta prova a cadeia inteira. O portão de rastreabilidade verifica automaticamente que todos "
        "os trinta e sete requisitos atravessam a especificação, o modelo de dados e a implementação. Nenhum "
        "requisito órfão, nenhuma tarefa sem origem. É a garantia de que o software é fiel à especificação.",
   prod="Mostre o portão de rastreabilidade em VERDE — 37 de 37, todos os saltos OK. Congele por 3 segundos.",
   trecho="Portão de Rastreabilidade (real)\n"
          "  FR-016 → UC-001 → task calculate_urban_compliance → código\n"
          "  37/37 requisitos · Req→Spec, Matriz FR→UC, FR→Implementação, Task→código: OK"),

 dict(n=15, cena="A aplicação gerada", dur=16, imgs=[im(APP, "01-app-home.png")],
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
    L = ["# Script de Vídeo — Pipeline SDD na ferramenta LangNet (projeto Uso do Solo)\n",
         "**Formato:** script para locução automática. **NARRAÇÃO** = fala EXATA a ser lida (siglas soletradas). "
         "**PRODUÇÃO** = o que mostrar (menu lateral, funções, onde se escreve). **TRECHO DO DOCUMENTO** = partes "
         "reais a exibir. Estilo demonstrativo e didático. **Ordem = navegação real.** **Duração:** ~%s (%d cenas).\n"
         % (fmt(TOTAL), len(SC)),
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
    .ex { background:#12182f; color:#e8edfa; font-family:'DejaVu Sans Mono',monospace; font-size:8.5px;
          padding:9px 12px; border-radius:6px; white-space:pre-wrap; line-height:1.4; }
    """
    rows = "".join("<tr><td><b>%d</b></td><td>%s</td><td>%s</td><td>%ds</td></tr>"
                   % (s["n"], esc(s["cena"]), fmt(CUM[i]), s["dur"]) for i, s in enumerate(SC))
    body = ['<div class="cover"><h1>Script de Vídeo — Pipeline SDD na ferramenta LangNet</h1>'
            '<p>Passeio didático pelo menu lateral · projeto de exemplo <b>Uso do Solo</b> · telas reais do sistema</p>'
            '<p><b>NARRAÇÃO</b> = fala exata (locução automática) · <b>PRODUÇÃO</b> = o que mostrar / menu / funções '
            '· <b>TRECHO</b> = partes reais do documento a exibir.</p>'
            '<p style="color:#c76a00"><b>Duração:</b> ~%s · %d cenas · ordem = navegação real</p>'
            '<table class="tl"><tr><th>Cena</th><th>Etapa do pipeline</th><th>Entra</th><th>Dura</th></tr>%s</table>'
            '<div style="page-break-after:always"></div>' % (fmt(TOTAL), len(SC), rows)]
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
print("OK:", fmt(TOTAL), "·", len(SC), "cenas")

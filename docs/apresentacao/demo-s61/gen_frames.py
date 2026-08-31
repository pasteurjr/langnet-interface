# -*- coding: utf-8 -*-
"""Gera os quadros (frames) do storyboard da DEMO S61 — molduras de navegador/terminal,
spec na tela, trecho de código real e o portão de rastreabilidade VERDE."""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
INK="#161e33"; INDIGO="#4f46e5"; VIO="#7c3aed"; SKY="#0283c9"; EMER="#059669"; AMBER="#c76a00"
MUTED="#5a667e"; PANEL="#eef0f8"; RULE="#d9dff0"; WHITE="#ffffff"; CODEBG="#12182f"; CODEFG="#e8edfa"
GREENBG="#0c2a1a"; GREENFG="#8ef0b8"
FF="Liberation Sans"; MONO="DejaVu Sans Mono"
plt.rcParams.update({"font.family": FF})
DIR=os.path.join(os.path.dirname(__file__),"frames"); os.makedirs(DIR, exist_ok=True)

def _fig(w=12.0,h=7.0):
    fig,ax=plt.subplots(figsize=(w,h),dpi=150); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")
    fig.subplots_adjust(left=0,right=1,top=1,bottom=0); return fig,ax
def _save(fig,name):
    p=os.path.join(DIR,name); fig.savefig(p,dpi=150,facecolor="#f4f6fb",bbox_inches="tight",pad_inches=0.15); plt.close(fig); return p

def browser(name, color, tab, url, title, lines, note):
    fig,ax=_fig()
    ax.add_patch(FancyBboxPatch((2,6),96,90,boxstyle="round,pad=0.2,rounding_size=1.5",fc=WHITE,ec=RULE,lw=1.5))
    ax.add_patch(FancyBboxPatch((2,86),96,10,boxstyle="round,pad=0.2,rounding_size=1.5",fc=color,ec=color,lw=1))
    for i,c in enumerate(["#ff5f57","#febc2e","#28c840"]): ax.add_patch(plt.Circle((6+i*3,91),1.0,color=c))
    ax.text(50,91,tab,ha="center",va="center",fontsize=12,color=WHITE,fontweight="bold")
    ax.add_patch(FancyBboxPatch((6,79),88,4.5,boxstyle="round,pad=0.1,rounding_size=1.0",fc=PANEL,ec=RULE,lw=0.8))
    ax.text(8,81.2,url,ha="left",va="center",fontsize=10,color=MUTED,fontfamily=MONO)
    ax.text(6,73,title,ha="left",va="center",fontsize=15,color=color,fontweight="bold")
    y=67
    for ln,st in lines:
        fs=11.5; col=INK; fw="normal"
        if st=="h": col=color; fw="bold"; fs=12.5
        elif st=="m": col=MUTED
        elif st=="c": col=color; fw="bold"
        ax.text(7,y,ln,ha="left",va="top",fontsize=fs,color=col,fontweight=fw,
                fontfamily=(MONO if st=="code" else FF)); y-=5.4
    ax.add_patch(FancyBboxPatch((6,7.5),88,7,boxstyle="round,pad=0.15,rounding_size=1.0",fc="#fff6e6",ec=AMBER,lw=1.2))
    ax.text(8,11,"CAPTURAR:  "+note,ha="left",va="center",fontsize=10.5,color=AMBER,fontweight="bold")
    return _save(fig,name)

def terminal(name, lines, green=False, note=None):
    fig,ax=_fig()
    bg=GREENBG if green else CODEBG; fg=GREENFG if green else CODEFG
    ax.add_patch(FancyBboxPatch((2,6),96,90,boxstyle="round,pad=0.2,rounding_size=1.5",fc=bg,ec=bg,lw=1))
    for i,c in enumerate(["#ff5f57","#febc2e","#28c840"]): ax.add_patch(plt.Circle((6+i*3,92),1.0,color=c))
    ax.text(50,92,"terminal",ha="center",va="center",fontsize=11,color="#9aa4bf",fontfamily=MONO)
    y=84
    for ln,em in lines:
        col=fg
        if em=="ok": col="#5ef08e"
        elif em=="err": col="#ff7a7a"
        elif em=="dim": col="#8a93ab"
        elif em=="hi": col="#ffd166"
        ax.text(6,y,ln,ha="left",va="top",fontsize=11.5,color=col,fontfamily=MONO,fontweight=("bold" if em in("ok","err","hi") else "normal")); y-=5.0
    if note:
        ax.add_patch(FancyBboxPatch((6,7.5),88,7,boxstyle="round,pad=0.15,rounding_size=1.0",fc="#3a2a10",ec="#febc2e",lw=1.0))
        ax.text(8,11,"CAPTURAR:  "+note,ha="left",va="center",fontsize=10.5,color="#febc2e",fontweight="bold")
    return _save(fig,name)

# ---- 1. Spec na tela ----
browser("spec_tela.png", INDIGO, "spec.md — LangNet",
        "localhost:3000/project/uso-do-solo/requisitos",
        "Especificação — Análise de Conformidade de Uso do Solo",
        [("Objetivo: avaliar a conformidade urbanística de um imóvel.","m"),
         ("FR-016  Calcular o Coeficiente de Aproveitamento","h"),
         ("        CA = área construída / área do terreno","code"),
         ("FR-017  Calcular a Taxa de Ocupação (TO = projeção / terreno)","h"),
         ("FR-018  Comparar CA e TO com os parâmetros da zona e","h"),
         ("        classificar em conforme / não-conforme","code"),
         ("FR-020  Detectar sobreposição com Área de Preservação (APP)","h"),
         ("Critério: CA=1,5 (limite 2,0) → conforme;  CA=2,5 → não-conforme","m"),
         ("Dados: imoveis, zoneamentos, parametros, apps (PostGIS, SRID 4674)","m"),
         ("Interface: mapa + formulário de cálculo + laudo em PDF","m")],
        "a spec inteira na tela, ~15 linhas, tempo de ser LIDA (não acelerar).")

# ---- 2..6, 8, 11 molduras de captura ----
browser("f_reqspec.png", SKY, "Especificação — LangNet",
        "localhost:3000/project/uso-do-solo/especificacao",
        "Etapa: Requisitos → Especificação",
        [("Matriz de rastreabilidade FR / NFR / BR → Casos de Uso","h"),
         ("37 requisitos funcionais mapeados a 10 casos de uso","m"),
         ("Cada FR com critério de aceitação verificável","m"),
         ("O agente compõe a spec; você aprova pela UI","m")],
        "a página de Especificação com a MATRIZ FR→UC visível; role até a matriz.")
browser("f_datamodel.png", TEAL if False else "#0d9488", "Modelo de Dados — LangNet",
        "localhost:3000/project/uso-do-solo/modelo-dados",
        "Etapa: Modelo de Dados (PostGIS)",
        [("Tabelas: imoveis, zoneamentos, parametros_urbanisticos, apps","h"),
         ("Colunas geométricas geometry(Geometry, 4674) — SIRGAS 2000","code"),
         ("Derivado dos requisitos, não desenhado à mão","m")],
        "o diagrama/DDL do Modelo de Dados; destaque as colunas geométricas.")
browser("f_uispec.png", VIO, "UI Spec & Protótipo — LangNet",
        "localhost:3000/project/uso-do-solo/ui-spec",
        "Etapa: UI Spec & Protótipo",
        [("Telas ricas por caso de uso: mapa, dashboard, upload, CRUD","h"),
         ("Wireframe + fluxo por tela, coerentes com o requisito","m"),
         ("Protótipo HTML gerado antes do código","m")],
        "a tela de UI Spec mostrando o wireframe de MAPA do UC de conformidade.")
browser("f_ats_yaml.png", AMBER, "Agent-Task Spec & YAML — LangNet",
        "localhost:3000/project/uso-do-solo/yaml-generation",
        "Etapa: Agent-Task Spec → agents.yaml + tasks.yaml",
        [("tasks.yaml: calculate_urban_compliance (execution: deterministic)","code"),
         ("Cada task com traceability {uc, fr} e output esperado","m"),
         ("agents.yaml ↔ tasks.yaml coerentes (10/10)","h")],
        "a aba Tasks YAML com o bloco da task calculate_urban_compliance aberto.")
browser("f_codegen.png", INDIGO, "Geração de Código — LangNet",
        "localhost:3000/project/uso-do-solo/code",
        "Etapa: Geração de Código",
        [("104 arquivos gerados: backend, ws-server, frontend, db","h"),
         ("adapters.py, tasks.yaml, schema.sql, React + Leaflet","code"),
         ("arquivos surgindo na árvore do projeto","m")],
        "a árvore de arquivos preenchendo (acelerar 3–4× com tempo real na legenda).")
terminal("f_deploy.png",
         [("$ docker compose up  # subindo o app gerado","dim"),
          ("ws-server  ▶ WebSocket em ws://localhost:5030","ok"),
          ("frontend   ▶ http://localhost:3001  (webpack compiled)","ok"),
          ("postgres   ▶ uso_solo_green  (PostGIS 3.4)","ok"),
          ("[ws] 15 tarefas determinísticas carregadas","hi")],
         note="o terminal subindo os serviços; acelerar 3–4×, tempo real na legenda.")
terminal("f_teste.png",
         [("$ pytest  tests/test_conformidade.py","dim"),
          ("test_calc_ca_to ......... FAILED","err"),
          ("  AssertionError: status_ca esperado 'conforme', veio NULL","err"),
          ("→ portão apontou: coluna sem DEFAULT no INSERT","hi"),
          ("$ # corrigido no gerador; regenerado","dim"),
          ("test_calc_ca_to ......... PASSED","ok")],
         note="a suíte: 1 teste FALHA, você mostra o erro, corrige e ele PASSA. NÃO CORTE.")

# ---- 7. Trecho de código gerado (real) ----
def code_frame(name, title, lines):
    fig,ax=_fig()
    ax.add_patch(FancyBboxPatch((2,6),96,90,boxstyle="round,pad=0.2,rounding_size=1.5",fc=CODEBG,ec=CODEBG,lw=1))
    for i,c in enumerate(["#ff5f57","#febc2e","#28c840"]): ax.add_patch(plt.Circle((6+i*3,92),1.0,color=c))
    ax.text(50,92,title,ha="center",va="center",fontsize=11,color="#9aa4bf",fontfamily=MONO)
    y=84
    for ln,em in lines:
        col=CODEFG
        if em=="kw": col="#c792ea"
        elif em=="str": col="#c3e88d"
        elif em=="cm": col="#7a89b8"
        elif em=="hi": col="#82aaff"
        ax.text(6,y,ln,ha="left",va="top",fontsize=11.0,color=col,fontfamily=MONO); y-=4.7
    return _save(fig,name)
code_frame("code_calc.png","adapters.py — gerado pelo LangNet (sem edição manual)",
    [("# calculate_urban_compliance — determinístico, sem LLM","cm"),
     ("def calculate_urban_compliance_deterministic(input_data):","kw"),
     ("    cur.execute('SELECT p.ca_maximo, p.to_maxima ...","hi"),
     ("      FROM zoneamentos z JOIN parametros_urbanisticos p","hi"),
     ("      ON p.zona_id = z.id JOIN imoveis i ...','...')","hi"),
     ("    ca_calc = _safe_div(area_construida, area_terreno)","str"),
     ("    to_calc = _safe_div(area_projecao, area_terreno)","str"),
     ("    status_ca = 'conforme' if ca_calc <= ca_maximo","kw"),
     ("                else 'nao_conforme'","kw"),
     ("    cur.execute('INSERT INTO calculos_conformidade ...')","hi"),
     ("    return {'ca_calculado': 1.5, 'status_ca': 'conforme'}","str")])

# ---- 12. Portão de rastreabilidade VERDE ----
gate=open(os.path.join(os.path.dirname(__file__),"..","..","uso-do-solo","validacao-final","gate_output.txt"),encoding="utf-8").read().splitlines()
terminal("gate_verde.png",
         [(l.replace("══════════════════════════════════════════════════════════════════","──────────────────────────────────────────────"),
           ("ok" if ("PASSOU" in l or " OK" in l) else ("hi" if "Inventário" in l else "dim")))
          for l in gate if l.strip()][:14],
         green=True, note="o painel do portão VERDE — 37/37 · todos os hops OK. Mantenha 2–3 s parado.")

print("frames gerados em", DIR)

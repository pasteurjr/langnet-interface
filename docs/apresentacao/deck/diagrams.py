# -*- coding: utf-8 -*-
"""Geradores de diagrama (matplotlib) no estilo clean/claro corporativo do deck."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager

INK="#161e33"; ACCENT="#4f46e5"; ACC2="#7a74f0"; MUTED="#5a667e"
PANEL="#f4f6fb"; PANEL2="#ecebfd"; RULE="#d9dff0"; GOOD="#0f9d58"; WARN="#e06a00"; WHITE="#ffffff"
# famílias vibrantes por bloco
FAMILY = {"indigo": ("#4f46e5","#7a74f0","#ecebfd"),
          "sky":    ("#0283c9","#38a8e0","#e3f3fc"),
          "violet": ("#7c3aed","#9b66f0","#f2eafe"),
          "teal":   ("#0d9488","#2cb1a6","#e1f5f3"),
          "emerald":("#059669","#2eb085","#e2f6ee"),
          "amber":  ("#c76a00","#ea992e","#fcf1df"),
          "rose":   ("#e11d48","#ec5476","#fce6ec"),
          "slate":  ("#334166","#5a6682","#eaedf4")}
FF="Liberation Sans"
try:
    font_manager.findfont(FF, fallback_to_default=False)
except Exception:
    FF="DejaVu Sans"
plt.rcParams.update({"font.family": FF})
DIR = os.path.join(os.path.dirname(__file__), "diagrams")
os.makedirs(DIR, exist_ok=True)


def _box(ax, x, y, w, h, text, fc=WHITE, ec=RULE, tc=INK, fs=9, bold=False, pad=0.02, r=0.02, lw=1.2, ha="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=%f,rounding_size=%f" % (pad, r),
                                fc=fc, ec=ec, lw=lw, zorder=2))
    ax.text(x+w/2 if ha=="center" else x+0.01, y+h/2, text, ha=ha, va="center",
            fontsize=fs, color=tc, fontweight="bold" if bold else "normal", zorder=3, wrap=True)


def _fig(w=13.2, h=6.7):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return fig, ax


def _save(fig, name):
    p = os.path.join(DIR, name)
    fig.savefig(p, dpi=200, facecolor=WHITE, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig); return p


# ---------- S4 — Linha do tempo (duas raias) ----------
def s4_timeline():
    ACCENT, ACC2, PANEL2 = FAMILY["violet"]   # Bloco 1
    fig, ax = _fig(13.2, 6.9)
    arch = [
        ("1958","Perceptron","neurônio único,\nseparador linear"),
        ("1969","Inverno da IA","XOR não é\nlinearmente separável"),
        ("1986","Backpropagation","MLP treinável,\ncamadas ocultas"),
        ("1997","LSTM","memória em\nsequência, gates"),
        ("1998","CNN / LeNet-5","convolução,\npesos compartilhados"),
        ("2012","AlexNet","GPU + ImageNet"),
        ("2014-15","seq2seq + Atenção","encoder-decoder,\nalinhamento suave"),
        ("2015","U-Net / ResNet","segmentação médica;\nconexões residuais"),
        ("2017","TRANSFORMER","atenção pura,\nparalelizável"),
        ("2018","BERT / GPT","pré-treino +\ntransferência"),
        ("2020","GPT-3 / escala","aprendizado\nno contexto"),
        ("2022","InstructGPT →\nChatGPT","alinhamento\na instruções"),
        ("2023-26","agentes +\nprotocolos","o modelo age\nsobre o ambiente"),
    ]
    n=len(arch); margin=2.0; gap=1.0
    bw=(100-2*margin-(n-1)*gap)/n; bh=17
    ytop=64
    ax.text(margin, 96, "ARQUITETURAS", fontsize=12, color=ACC2, fontweight="bold")
    for i,(yr,name,lab) in enumerate(arch):
        x=margin+i*(bw+gap)
        hot = (name=="TRANSFORMER")
        _box(ax, x, ytop, bw, bh, "", fc=(ACCENT if hot else PANEL2 if i>=9 else WHITE),
             ec=(ACCENT if hot else RULE), lw=1.6 if hot else 1.1, r=1.2, pad=0.2)
        tc = WHITE if hot else INK
        ax.text(x+bw/2, ytop+bh-3.4, yr, ha="center", va="center", fontsize=8.5, fontweight="bold",
                color=(WHITE if hot else ACCENT))
        ax.text(x+bw/2, ytop+bh-8.2, name, ha="center", va="center", fontsize=8.2, fontweight="bold", color=tc)
        ax.text(x+bw/2, ytop+3.2, lab, ha="center", va="center", fontsize=6.6,
                color=(WHITE if hot else MUTED))
    # eixo do tempo
    ax.plot([margin, 100-margin],[58,58], color=ACCENT, lw=2, zorder=1)
    # seta box9->box11 (Transformer -> GPT-3): "a mesma arquitetura, só que maior"
    x9=margin+8*(bw+gap)+bw/2; x11=margin+10*(bw+gap)+bw/2
    ax.add_patch(FancyArrowPatch((x9, ytop-1.2),(x11, ytop-1.2), connectionstyle="arc3,rad=-0.35",
                 arrowstyle="-|>", mutation_scale=18, color=ACC2, lw=2.2, zorder=4))
    ax.text((x9+x11)/2, ytop-9.5, "“a mesma arquitetura,\nsó que maior”", ha="center", va="center",
            fontsize=8, style="italic", color=ACC2, fontweight="bold")
    # raia inferior — trabalho do desenvolvedor (5 bandas de LARGURA IGUAL p/ os rótulos caberem)
    periods=[("1958–1998","Projetar\nfeatures à mão"),
             ("1998–2017","Treinar o\npróprio modelo"),
             ("2018–2021","Fazer fine-tune\nde um pré-treinado"),
             ("2021–2023","Chamar\numa API"),
             ("2023–2026","Orquestrar, especificar\ne verificar")]
    ax.text(margin, 40, "O QUE O DESENVOLVEDOR FAZIA", fontsize=12, color=ACC2, fontweight="bold")
    npb=len(periods); pgap=1.2
    pbw=(100-2*margin-(npb-1)*pgap)/npb
    yb=13; hb=21
    for i,(per,lab) in enumerate(periods):
        xa=margin+i*(pbw+pgap)
        hot = "Orquestrar" in lab
        _box(ax, xa, yb, pbw, hb, "", fc=(PANEL2 if hot else PANEL), ec=(ACC2 if hot else RULE),
             lw=1.8 if hot else 1.0, r=1.0, pad=0.2)
        ax.text(xa+pbw/2, yb+hb-4, per, ha="center", va="center", fontsize=9, fontweight="bold", color=ACCENT)
        ax.text(xa+pbw/2, yb+hb/2-3.5, lab, ha="center", va="center", fontsize=9.5,
                fontweight="bold", color=(ACCENT if hot else INK))
    ax.text(50, 2, "A ideia é de 1958. O que mudou foi compute e dado — e a unidade de trabalho de quem escreve software.",
            ha="center", fontsize=8.5, style="italic", color=MUTED)
    return _save(fig, "s4_timeline.png")


# ---------- S6 — Anatomia do Transformer (vertical) ----------
def s6_transformer():
    ACCENT, ACC2, PANEL2 = FAMILY["sky"]      # Bloco 2
    fig, ax = _fig(9.0, 7.0)
    steps=[("texto de entrada", PANEL, INK, False),
           ("tokenização  (texto → tokens)", WHITE, INK, False),
           ("embeddings + codificação posicional (RoPE)", WHITE, INK, False)]
    block=[("atenção multi-cabeça  (Q, K, V)", PANEL2, ACCENT, True),
           ("residual + normalização", WHITE, INK, False),
           ("rede feed-forward", PANEL2, ACCENT, True),
           ("residual + normalização", WHITE, INK, False)]
    top=[("projeção final → logits", WHITE, INK, False),
         ("softmax  (distribuição sobre o vocabulário)", WHITE, INK, False),
         ("amostragem → próximo token", PANEL, GOOD, True)]
    x=14; w=62; h=5.6; gap=2.0; y=3
    def draw(seq):
        nonlocal y
        for (t,fc,tc,b) in seq:
            _box(ax, x, y, w, h, t, fc=fc, ec=RULE, tc=tc, fs=11.5, bold=b, r=0.6, pad=0.2)
            y+=h+gap
    draw(list(reversed(top))[::-1])  # placeholder to keep order below
    # (rebuild ordered bottom->top)
    ax.clear(); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")
    y=3
    draw(steps)
    # bloco repetido N×
    by0=y-0.6
    for (t,fc,tc,b) in block:
        _box(ax, x, y, w, h, t, fc=fc, ec=RULE, tc=tc, fs=11.5, bold=b, r=0.6, pad=0.2)
        y+=h+gap
    by1=y-gap+0.6
    ax.add_patch(FancyBboxPatch((x-3.2, by0), w+6.4, by1-by0, boxstyle="round,pad=0.2,rounding_size=1.0",
                 fc="none", ec=ACC2, lw=2.0, ls=(0,(4,3)), zorder=1))
    ax.text(x+w+4.2, (by0+by1)/2, "N×", ha="left", va="center", fontsize=15, fontweight="bold", color=ACC2, rotation=0)
    draw(top)
    # setas verticais entre grupos
    ax.annotate("", xy=(x+w/2, 100-2), xytext=(x+w/2, 100-2),
                arrowprops=dict(arrowstyle="-"))
    ax.text(50, 98.5, "fluxo de baixo para cima — previsão do próximo token", ha="center",
            fontsize=9.5, style="italic", color=MUTED)
    return _save(fig, "s6_transformer.png")


# ---------- S9 — MoE (Mixture of Experts) ----------
def s9_moe():
    ACCENT, ACC2, PANEL2 = FAMILY["sky"]      # Bloco 2
    fig, ax = _fig(11.5, 6.3)
    # token -> roteador -> escolhe k de N especialistas -> soma
    _box(ax, 3, 44, 15, 12, "token de\nentrada", fc=PANEL, ec=RULE, tc=INK, fs=11, r=0.8, pad=0.2)
    _box(ax, 24, 42, 17, 16, "ROTEADOR\n(gating)", fc=ACCENT, ec=ACCENT, tc=WHITE, fs=12, bold=True, r=0.8, pad=0.2)
    ax.add_patch(FancyArrowPatch((18,50),(24,50), arrowstyle="-|>", mutation_scale=16, color=ACC2, lw=2))
    # N especialistas
    N=6; ex_x=52; ew=34; eh=8.5; ey0=8
    chosen={1,4}
    for i in range(N):
        y=ey0+i*(eh+2.2)
        on=i in chosen
        _box(ax, ex_x, y, ew, eh, "especialista %d%s" % (i+1, "    ativado" if on else ""),
             fc=(PANEL2 if on else WHITE), ec=(ACC2 if on else RULE), tc=(ACCENT if on else MUTED),
             fs=10.5, bold=on, r=0.6, pad=0.2)
        col = ACC2 if on else RULE
        ax.add_patch(FancyArrowPatch((41, 50),(ex_x, y+eh/2), connectionstyle="arc3,rad=0.05",
                     arrowstyle="-|>", mutation_scale=12, color=col, lw=2.0 if on else 0.9,
                     ls="-" if on else (0,(3,3)), zorder=1))
    ax.text(ex_x+ew/2, ey0+N*(eh+2.2)+1.5, "N especialistas no total", ha="center", fontsize=10.5,
            color=INK, fontweight="bold")
    ax.text(ex_x+ew/2, ey0-4.5, "só k são ATIVADOS por token (aqui k = 2)", ha="center", fontsize=10.5,
            color=ACCENT, fontweight="bold")
    # a consequência
    _box(ax, 3, 6, 40, 22, "", fc=PANEL, ec=RULE, r=0.8, pad=0.2)
    ax.text(4.5, 24, "A conta que importa", fontsize=11.5, fontweight="bold", color=ACCENT)
    ax.text(4.5, 18.5, "VRAM ← parâmetros TOTAIS (todos na memória)\n"
            "custo/velocidade ← parâmetros ATIVOS (só os k)", fontsize=10, color=INK, va="center")
    ax.text(4.5, 9.5, "→ MoE gigante barateia a nuvem,\n   não ajuda quem hospeda em casa.", fontsize=10,
            color=WARN, fontweight="bold", va="center")
    return _save(fig, "s9_moe.png")


# ---------- S17 — RAG (dois trilhos) ----------
def s17_rag():
    C1, C2, PZ = FAMILY["emerald"]      # Bloco 4
    RED = "#dc2626"
    fig, ax = _fig(13.0, 6.6)
    def lane(y, title, boxes):
        ax.text(3, y+13, title, fontsize=12.5, color=C1, fontweight="bold")
        n=len(boxes); m=3.0; gap=2.2
        bw=(100-2*m-(n-1)*gap)/n; bh=11
        xs=[]
        for i,(t,red) in enumerate(boxes):
            x=m+i*(bw+gap)
            _box(ax, x, y, bw, bh, t, fc=(WHITE if not red else "#fdecec"),
                 ec=(RED if red else RULE), tc=(RED if red else INK), fs=9.3,
                 bold=red, r=0.8, pad=0.2, lw=2.0 if red else 1.1)
            xs.append((x,x+bw))
            if i>0:
                ax.add_patch(FancyArrowPatch((xs[i-1][1], y+bh/2),(x, y+bh/2),
                             arrowstyle="-|>", mutation_scale=13, color=C2, lw=1.8))
        return xs
    lane(72, "INGESTÃO (uma vez, offline)",
         [("documento",0),("chunking\n(fatiar)",1),("embedding\n(vetor)",0),("índice\nvetorial + léxico",0)])
    lane(40, "CONSULTA (a cada pergunta)",
         [("pergunta",0),("reescrita",0),("busca híbrida\n(léxica + densa)",1),
          ("reordenação\n(reranking)",1),("montagem",0),("geração\ncom citação",0)])
    ax.text(50, 22, "Os três pontos de quebra: fatiar mal, recuperar o trecho errado, e a ausência de reordenação.",
            ha="center", fontsize=10.5, color=RED, fontweight="bold")
    ax.text(50, 15, "RAG raramente falha na geração — falha na recuperação, e o time gasta semanas ajustando o prompt.",
            ha="center", fontsize=10, style="italic", color=MUTED)
    ax.text(50, 6, "RAG = Retrieval-Augmented Generation (geração aumentada por recuperação).",
            ha="center", fontsize=9.5, color=C1, fontweight="bold")
    return _save(fig, "s17_rag.png")


# ---------- S22 — O laço agêntico (ciclo) ----------
def s22_loop():
    C1, C2, PZ = FAMILY["amber"]        # Bloco 5
    fig, ax = _fig(12.5, 6.6)
    import math
    cx, cy, R = 38, 50, 27
    nodes=[("OBJETIVO",90),("RACIOCÍNIO",18),("AÇÃO\n(ferramenta)",-54),("OBSERVAÇÃO",-126),]
    pts=[]
    for (t,ang) in nodes:
        a=math.radians(ang); x=cx+R*math.cos(a); y=cy+R*math.sin(a)
        pts.append((x,y))
        hot = t.startswith("AÇÃO")
        _box(ax, x-11, y-5.5, 22, 11, t, fc=(C1 if hot else PZ), ec=C1,
             tc=(WHITE if hot else C1), fs=11.5, bold=True, r=0.9, pad=0.2, lw=1.6)
    order=[0,1,2,3,0]
    for i in range(4):
        (x1,y1)=pts[order[i]]; (x2,y2)=pts[order[i+1]]
        ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2), connectionstyle="arc3,rad=0.28",
                     arrowstyle="-|>", mutation_scale=18, color=C2, lw=2.4))
    ax.text(cx, cy, "repete\naté a\nparada", ha="center", va="center", fontsize=11,
            color=MUTED, style="italic", fontweight="bold")
    # saída
    ax.add_patch(FancyArrowPatch((cx+R+1, cy),(cx+R+11, cy), arrowstyle="-|>",
                 mutation_scale=16, color=C1, lw=2.2))
    _box(ax, cx+R+11, cy-5, 18, 10, "PARADA →\nresposta", fc=GOOD, ec=GOOD, tc=WHITE, fs=11, bold=True, r=0.8, pad=0.2)
    # 3 pontos de controle
    _box(ax, 78, 74, 21, 18, "", fc=PZ, ec=C1, r=0.7, pad=0.2)
    ax.text(79.5, 88, "Três pontos de controle", fontsize=11, fontweight="bold", color=C1)
    ax.text(79.5, 82, "1. quais ferramentas existem", fontsize=9.6, color=INK)
    ax.text(79.5, 78.5, "2. o que volta como observação", fontsize=9.6, color=INK)
    ax.text(79.5, 75, "3. quando o laço para", fontsize=9.6, color=INK)
    ax.text(50, 6, "Um agente = um modelo em laço, com ferramentas, sobre um ambiente, com critério de parada.",
            ha="center", fontsize=10.5, color=C1, fontweight="bold")
    return _save(fig, "s22_loop.png")


# ---------- S25 — Os seis padrões de composição (3×2) ----------
def s25_patterns():
    C1, C2, PZ = FAMILY["amber"]        # Bloco 5
    fig, ax = _fig(12.8, 6.4)
    pats=[("Encadeamento", "saída de um vira\nentrada do próximo", 0),
          ("Roteamento", "classifica e envia\nao especialista certo", 0),
          ("Paralelização", "secciona ou VOTA\n(reduz falso positivo)", 1),
          ("Orquestrador-\ntrabalhadores", "um coordena, vários\nexecutam isolados", 0),
          ("Avaliador-\notimizador", "um gera, um critica\ne manda refazer", 1),
          ("Agente autônomo", "decide os próprios\npassos (mais risco)", 0)]
    cols=3; rows=2; m=3.0; gx=2.4; gy=3.0
    bw=(100-2*m-(cols-1)*gx)/cols; bh=(78-(rows-1)*gy)/rows; y0=10
    for i,(t,d,hot) in enumerate(pats):
        r=i//cols; c=i%cols
        x=m+c*(bw+gx); y=y0+(rows-1-r)*(bh+gy)
        _box(ax, x, y, bw, bh, "", fc=(PZ if hot else WHITE), ec=(C1 if hot else RULE),
             r=0.8, pad=0.2, lw=2.0 if hot else 1.2)
        _box(ax, x, y+bh-3.2, bw, 0.1, "", fc=C1, ec=C1)  # topo colorido fino
        ax.text(x+bw/2, y+bh-6, t, ha="center", va="center", fontsize=11.5, fontweight="bold", color=C1)
        ax.text(x+bw/2, y+bh/2-4, d, ha="center", va="center", fontsize=10, color=INK)
    ax.text(50, 3.5, "Comece pelo mais simples que resolve. Os mais subutilizados e úteis aqui: VOTAÇÃO e AVALIADOR-OTIMIZADOR.",
            ha="center", fontsize=10.3, color=C1, fontweight="bold")
    return _save(fig, "s25_patterns.png")


# ---------- S28 — Curva do erro composto ----------
def s28_error():
    C1, C2, PZ = FAMILY["amber"]        # Bloco 5
    fig, ax = plt.subplots(figsize=(11.5, 6.0), dpi=200)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.9, bottom=0.13)
    steps = list(range(0, 21))
    series = [(0.90, "#dc2626", "90% por passo"),
              (0.95, C1, "95% por passo"),
              (0.99, "#059669", "99% por passo")]
    for p, col, lab in series:
        ys = [100*(p**k) for k in steps]
        ax.plot(steps, ys, color=col, lw=3.0, label=lab, marker="o", markersize=3.5)
        ax.text(20.3, 100*(p**20), "%d%%" % round(100*(p**20)), color=col, fontsize=12, fontweight="bold", va="center")
    # destaque 95% em 20 passos -> 36%
    ax.axvline(20, color=RULE, lw=1, ls="--")
    ax.annotate("95% por passo × 20 passos\n= 36% de sucesso fim a fim",
                xy=(20, 36), xytext=(11, 20), fontsize=11, color=C1, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.8))
    ax.set_xlim(0, 22); ax.set_ylim(0, 102)
    ax.set_xlabel("número de passos NÃO verificados", fontsize=12, color=INK)
    ax.set_ylabel("chance de sucesso fim a fim (%)", fontsize=12, color=INK)
    ax.set_title("Erro composto: cada passo sem verificação multiplica o risco",
                 fontsize=13.5, color=C1, fontweight="bold", pad=12)
    ax.legend(loc="upper right", fontsize=11, frameon=False)
    ax.grid(True, color="#eef1f7", lw=1)
    for sp in ["top","right"]: ax.spines[sp].set_visible(False)
    for sp in ["left","bottom"]: ax.spines[sp].set_color(RULE)
    ax.tick_params(colors=MUTED)
    p = os.path.join(DIR, "s28_error.png")
    fig.savefig(p, dpi=200, facecolor=WHITE, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig); return p


# ---------- S29 — Protocolos: vertical (MCP) × horizontal (A2A) ----------
def s29_protocols():
    C1, C2, PZ = FAMILY["rose"]          # Bloco 6
    SKY = FAMILY["sky"]; VIO = FAMILY["violet"]
    fig, ax = _fig(12.8, 6.6)
    # agente no centro
    _box(ax, 41, 42, 18, 14, "AGENTE", fc=C1, ec=C1, tc=WHITE, fs=14, bold=True, r=0.8, pad=0.2)
    # eixo VERTICAL = MCP (ferramentas)
    ax.text(50, 96, "MCP — eixo VERTICAL: agente → ferramentas", ha="center", fontsize=11.5, color=SKY[0], fontweight="bold")
    _box(ax, 38, 78, 24, 11, "Servidores MCP\nTools · Resources · Prompts", fc=SKY[2], ec=SKY[0], tc=SKY[0], fs=10.5, bold=True, r=0.7, pad=0.2)
    ax.add_patch(FancyArrowPatch((50, 78),(50, 56), arrowstyle="<|-|>", mutation_scale=16, color=SKY[0], lw=2.2))
    _box(ax, 40, 10, 20, 9, "USB-C das ferramentas", fc=SKY[2], ec=SKY[0], tc=SKY[0], fs=10.5, bold=True, r=0.7, pad=0.2)
    ax.add_patch(FancyArrowPatch((50, 42),(50, 19), arrowstyle="-", mutation_scale=1, color=SKY[1], lw=1.4, ls=(0,(3,3))))
    # eixo HORIZONTAL = A2A (outros agentes)
    ax.text(50, 2.5, "A2A — eixo HORIZONTAL: agente ↔ agente (AgentCard, tarefa em 8 estados)", ha="center", fontsize=11, color=VIO[0], fontweight="bold")
    _box(ax, 4, 44, 20, 10, "outro AGENTE\n(AgentCard)", fc=VIO[2], ec=VIO[0], tc=VIO[0], fs=10.5, bold=True, r=0.7, pad=0.2)
    _box(ax, 76, 44, 20, 10, "outro AGENTE\n(AgentCard)", fc=VIO[2], ec=VIO[0], tc=VIO[0], fs=10.5, bold=True, r=0.7, pad=0.2)
    ax.add_patch(FancyArrowPatch((24, 49),(41, 49), arrowstyle="<|-|>", mutation_scale=16, color=VIO[0], lw=2.2))
    ax.add_patch(FancyArrowPatch((59, 49),(76, 49), arrowstyle="<|-|>", mutation_scale=16, color=VIO[0], lw=2.2))
    ax.text(15, 28, "Limite do MCP: dois servidores\nNÃO conversam entre si (hub-and-spoke).",
            ha="center", fontsize=9.3, color=C1, style="italic", fontweight="bold")
    ax.text(85, 28, "A2A é o “HTTP” da colaboração\nentre agentes. Em produção, usa os DOIS.",
            ha="center", fontsize=9.3, color=C1, style="italic", fontweight="bold")
    return _save(fig, "s29_protocols.png")


# ---------- S37 — LangGraph: máquina de estados ----------
def s37_langgraph():
    C1, C2, PZ = FAMILY["indigo"]        # Bloco 7
    fig, ax = _fig(12.5, 6.4)
    _box(ax, 6, 46, 16, 11, "coletar\nevidência", fc=WHITE, ec=C1, tc=C1, fs=11, bold=True, r=0.8, pad=0.2)
    _box(ax, 30, 46, 16, 11, "avaliar\ncritério", fc=WHITE, ec=C1, tc=C1, fs=11, bold=True, r=0.8, pad=0.2)
    # nó de decisão (losango via caixa girada aproximada -> usamos caixa destacada)
    _box(ax, 54, 44, 17, 15, "conforme?\n(aresta condicional)", fc=PZ, ec=C1, tc=C1, fs=10.5, bold=True, r=0.8, pad=0.2)
    _box(ax, 80, 62, 16, 11, "INTERRUPÇÃO\naprovação humana", fc=FAMILY["amber"][2], ec=FAMILY["amber"][0], tc=FAMILY["amber"][0], fs=10.5, bold=True, r=0.8, pad=0.2)
    _box(ax, 80, 30, 16, 11, "notificar", fc=FAMILY["emerald"][2], ec=FAMILY["emerald"][0], tc=FAMILY["emerald"][0], fs=11, bold=True, r=0.8, pad=0.2)
    ax.add_patch(FancyArrowPatch((22, 51.5),(30, 51.5), arrowstyle="-|>", mutation_scale=14, color=C2, lw=2))
    ax.add_patch(FancyArrowPatch((46, 51.5),(54, 51.5), arrowstyle="-|>", mutation_scale=14, color=C2, lw=2))
    ax.add_patch(FancyArrowPatch((66, 55),(80, 66), arrowstyle="-|>", mutation_scale=14, color=FAMILY["amber"][0], lw=2))
    ax.add_patch(FancyArrowPatch((88, 62),(88, 41), arrowstyle="-|>", mutation_scale=14, color=C2, lw=2))
    ax.text(74, 60.5, "sim", fontsize=9.5, color=FAMILY["amber"][0], fontweight="bold")
    # checkpointer
    _box(ax, 30, 20, 40, 9, "checkpointer — estado persistente (sobrevive a reinício)", fc=PZ, ec=C1, tc=C1, fs=10.5, bold=True, r=0.7, pad=0.2)
    ax.add_patch(FancyArrowPatch((38, 46),(40, 29), arrowstyle="-", color=C1, lw=1.2, ls=(0,(3,3))))
    ax.add_patch(FancyArrowPatch((62, 44),(60, 29), arrowstyle="-", color=C1, lw=1.2, ls=(0,(3,3))))
    ax.text(50, 8, "LangGraph = grafo de estados: nós, arestas condicionais, estado durável e PARADA para aprovação humana.",
            ha="center", fontsize=10.3, color=C1, fontweight="bold")
    return _save(fig, "s37_langgraph.png")


# ---------- S46 — O ciclo SDD (pipeline com gates) ----------
def s46_sdd():
    C1, C2, PZ = FAMILY["indigo"]        # Bloco 9
    GRN = FAMILY["emerald"]
    fig, ax = _fig(13.0, 5.6)
    stages = ["Intenção","Especificação","Plano","Tarefas","Implementação","Verificação"]
    n=len(stages); m=2.0; gate_w=4.0; gap=1.0
    bw=(100-2*m-(n-1)*(gate_w+2*gap))/n; bh=16; y=52
    xs=[]
    for i,st in enumerate(stages):
        x=m+i*(bw+gate_w+2*gap)
        hot = st in ("Especificação",)
        _box(ax, x, y, bw, bh, st, fc=(PZ if hot else WHITE), ec=C1, tc=C1, fs=11.5, bold=True, r=0.8, pad=0.2,
             lw=2.2 if hot else 1.3)
        xs.append((x,x+bw))
        if i>0:
            gx=xs[i-1][1]+gap
            # gate (losango aprox: quadrado girado -> caixa verde pequena "GATE")
            ax.add_patch(FancyBboxPatch((gx, y+bh/2-3.0), gate_w, 6.0, boxstyle="round,pad=0.2,rounding_size=0.5",
                         fc=GRN[2], ec=GRN[0], lw=1.6, zorder=3))
            ax.text(gx+gate_w/2, y+bh/2, "GATE", ha="center", va="center", fontsize=8.5, color=GRN[0], fontweight="bold")
            ax.add_patch(FancyArrowPatch((xs[i-1][1], y+bh/2),(gx, y+bh/2), arrowstyle="-|>", mutation_scale=11, color=C2, lw=1.8))
            ax.add_patch(FancyArrowPatch((gx+gate_w, y+bh/2),(xs[i][0], y+bh/2), arrowstyle="-|>", mutation_scale=11, color=C2, lw=1.8))
    # seta de retorno em falha
    ax.add_patch(FancyArrowPatch((xs[-1][0]+bw/2, y),(xs[1][0]+bw/2, y), connectionstyle="arc3,rad=0.32",
                 arrowstyle="-|>", mutation_scale=16, color="#dc2626", lw=2.0, ls=(0,(5,3))))
    ax.text(50, 20, "em caso de falha, volta — nenhum passo avança sem passar no seu gate",
            ha="center", fontsize=10, color="#dc2626", style="italic", fontweight="bold")
    ax.text(50, 84, "Cada GATE corta a cadeia não verificada: aprovação humana · teste automatizado · verificação de política · verificação formal",
            ha="center", fontsize=10, color=GRN[0], fontweight="bold")
    ax.text(50, 8, "SDD = Spec-Driven Development (Desenvolvimento Orientado a Especificação). A spec é primária; o código é derivado.",
            ha="center", fontsize=10.3, color=C1, fontweight="bold")
    return _save(fig, "s46_sdd.png")


# ---------- S62 — AI Co-Scientist: fases, agentes, torneio ----------
def s62_coscientist():
    C1, C2, PZ = FAMILY["violet"]        # Bloco 11
    fig, ax = _fig(13.0, 6.6)
    # supervisor no topo
    _box(ax, 22, 86, 56, 10, "SUPERVISOR  ·  decompõe o objetivo  ·  aloca recursos  ·  gerencia a fila",
         fc=C1, ec=C1, tc=WHITE, fs=10.5, bold=True, r=0.7, pad=0.2)
    phases=[("GERAR", ["Generation\n(debate em self-play)","Proximity\n(grafo de proximidade)"], FAMILY["emerald"]),
            ("DEBATER", ["Reflection\n(revisor por pares)","Ranking\n(torneio Elo)"], FAMILY["amber"]),
            ("EVOLUIR", ["Evolution\n(cria, não muta)","Meta-review\n(realimenta prompts)"], FAMILY["sky"])]
    pw=30; x0=3; gap=3.5; y_ag=44; ah=13
    for i,(ph,agents,col) in enumerate(phases):
        px=x0+i*(pw+gap)
        ax.add_patch(FancyBboxPatch((px, 40), pw, 34, boxstyle="round,pad=0.3,rounding_size=1.0",
                     fc=col[2], ec=col[0], lw=1.6, zorder=1))
        ax.text(px+pw/2, 70, ph, ha="center", fontsize=12.5, color=col[0], fontweight="bold")
        for j,ag in enumerate(agents):
            _box(ax, px+2, 55-j*15, pw-4, ah, ag, fc=WHITE, ec=col[0], tc=INK, fs=9.2, bold=True, r=0.7, pad=0.2)
        if i>0:
            ax.add_patch(FancyArrowPatch((x0+i*(pw+gap)-gap, 57),(px, 57), arrowstyle="-|>", mutation_scale=13, color=C1, lw=2))
    # torneio Elo -> loop
    _box(ax, 30, 20, 40, 11, "TORNEIO ELO  ·  rating inicial 1200  ·  debate par a par (multi-turno)",
         fc=PZ, ec=C1, tc=C1, fs=10, bold=True, r=0.7, pad=0.2)
    ax.add_patch(FancyArrowPatch((80, 47),(70, 26), connectionstyle="arc3,rad=-0.3", arrowstyle="-|>", mutation_scale=14, color=C1, lw=1.8))
    ax.add_patch(FancyArrowPatch((30, 26),(20, 47), connectionstyle="arc3,rad=-0.3", arrowstyle="-|>", mutation_scale=14, color=C1, lw=1.8))
    ax.text(50, 15.5, "as melhores hipóteses voltam para uma nova rodada", ha="center", fontsize=9, color=MUTED, style="italic")
    ax.text(50, 8, "Test-time compute: quanto mais “pensa”, maior o Elo. Meta-revisão = aprendizado SEM gradiente (em contexto).",
            ha="center", fontsize=10.3, color=C1, fontweight="bold")
    ax.text(50, 3, "Base: Gemini 2.0 · validação: Elo mais alto ↔ acerto no GPQA (AUC 0,643→0,651)",
            ha="center", fontsize=9, color=MUTED)
    return _save(fig, "s62_coscientist.png")


ALL = {"s4": s4_timeline, "s6": s6_transformer, "s9": s9_moe,
       "s17": s17_rag, "s22": s22_loop, "s25": s25_patterns, "s28": s28_error,
       "s29": s29_protocols, "s37": s37_langgraph, "s46": s46_sdd, "s62": s62_coscientist}

if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or list(ALL.keys())
    for k in which:
        print(ALL[k]())

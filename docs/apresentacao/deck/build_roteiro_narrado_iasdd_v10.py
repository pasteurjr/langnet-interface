# -*- coding: utf-8 -*-
"""V10 · roteiro narrado. NÃO sobrescreve o roteiro da V9.

O texto sob “O que a narradora fala” é fala literal — não é instrução de palco.
Nada de “mostre”, “aponte”, “apresente-se”: é para ser lido em voz alta como está.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_deck_iasdd_v10_biobyte as deck

RAIZ = HERE.parent
SAIDA = RAIZ / "roteiro_narrado_iasdd_v10_biobyte.md"
TELAS = "roteiro_narrado_iasdd_v10_biobyte_slides"

PPM = 135.0   # palavras por minuto, ritmo de aula com pausas


def minutos(texto):
    return len(texto.split()) / PPM


def tempo(m):
    seg = int(round(m * 60))
    return "%d min %02d s" % (seg // 60, seg % 60) if seg >= 60 else "%d s" % seg


def build():
    S = deck.SLIDES
    fala_total = sum(minutos(s.get("fala", "")) for s in S)
    video_total = sum(s.get("minutos", 0) for s in S if s["tipo"] == "video")

    L = []
    L.append("# Roteiro narrado — Engenharia de IA e Desenvolvimento Orientado a Especificação (V10)\n")
    L.append("> **Esta é a versão 10.** A versão 9 permanece intacta nos arquivos "
             "`apresentacao_iasdd_v9_biobyte.pptx` e `roteiro_narrado_iasdd_v9_biobyte.md`.\n")
    L.append("")
    L.append("| | |")
    L.append("|---|---|")
    L.append("| **Lâminas** | %d |" % len(S))
    L.append("| **Tempo falado das lâminas** | **%s** (a %g palavras por minuto) |" % (tempo(fala_total), PPM))
    L.append("| **Vídeos** | %d demonstrações · %g minutos |"
             % (sum(1 for s in S if s["tipo"] == "video"), video_total))
    L.append("| **Total** | %s |" % tempo(fala_total + video_total))
    L.append("| **Palavras de narração** | %d |" % sum(len(s.get("fala", "").split()) for s in S))
    L.append("")
    L.append("## Como ler este roteiro\n")
    L.append("Cada lâmina tem três partes:\n")
    L.append("1. **A imagem da lâmina** — o arquivo correspondente em `%s/`." % TELAS)
    L.append("2. **O que está escrito na lâmina** — o texto que a plateia lê na tela.")
    L.append("3. **O que a narradora fala** — a fala literal, para ser lida em voz alta exatamente como está. "
             "Não há instrução de palco misturada ao texto.\n")
    L.append("---\n")

    # sumário por bloco
    L.append("## Sumário\n")
    for i, s in enumerate(S, 1):
        if s["tipo"] == "divisor":
            L.append("- **Bloco %d — %s** (lâmina %d)" % (s["bloco"], s["titulo"], i))
        elif s["tipo"] == "video":
            L.append("  - ▶ *vídeo %g min — %s* (lâmina %d)" % (s["minutos"], s["titulo"], i))
    L.append("\n---\n")

    for i, s in enumerate(S, 1):
        titulo = s.get("titulo", "Capa")
        L.append('<div class="slide" id="slide-%d"></div>\n' % i)
        L.append("## Lâmina %02d — %s\n" % (i, titulo))

        if s["tipo"] == "video":
            L.append("**▶ VÍDEO — %g minutos.** %s\n" % (s["minutos"], s["resumo"]))
        else:
            L.append("**Tempo falado:** %s\n" % tempo(minutos(s.get("fala", ""))))

        L.append("![Lâmina %02d](%s/slide_%02d.png)\n" % (i, TELAS, i))

        # o que está escrito na lâmina
        L.append("### O que está escrito na lâmina\n")
        if s["tipo"] == "capa":
            L.append("- **%s**" % s["titulo"])
            L.append("- *%s*" % s["subtitulo"])
            L.append("- %s" % s["rodape"])
        elif s["tipo"] == "divisor":
            L.append("- **BLOCO %d — %s**" % (s["bloco"], s["titulo"]))
            L.append("- *%s*" % s["mensagem"])
        elif s["tipo"] == "algoritmo":
            L.append("- **Ideia central:** %s" % s["ideia"])
            L.append("- **Como funciona:** %s" % s["como"])
            L.append("- **Para que se presta:** %s" % s["serve"])
            L.append("- **Onde é mais adequado:** %s" % s["onde"])
        elif s["tipo"] == "etapa":
            L.append("- *Trilha das etapas, com estas em destaque:* **%s**"
                     % ", ".join(s["trilha"][j - 1] for j in s["atual"]))
            for c in s["cartoes"]:
                L.append("- **%s** — %s" % (c[0], c[1]))
        elif s["tipo"] == "cartoes":
            if s.get("destaque"):
                L.append("- *%s*" % s["destaque"])
            for c in s["cartoes"]:
                L.append("- **%s** — %s" % (c[0], c[1]))
        elif s["tipo"] == "codigo":
            L.append("- *%s*" % s["intro"])
            L.append("")
            L.append("```python")
            L.append(s["codigo"])
            L.append("```")
            L.append("")
            L.append("- **Ao lado do código:** %s" % s["explicacao"])
        elif s["tipo"] == "tabela":
            L.append("")
            L.append("| " + " | ".join(s["colunas"]) + " |")
            L.append("|" + "---|" * len(s["colunas"]))
            for r in s["linhas"]:
                L.append("| " + " | ".join(x.lstrip("*") for x in r) + " |")
            L.append("")
            if s.get("nota"):
                L.append("- **Nota na lâmina:** %s" % s["nota"])
        elif s["tipo"] == "citacao":
            L.append("- > **%s**" % s["frase"])
            for c in s["cartoes"]:
                L.append("- **%s** — %s" % (c[0], c[1]))
        elif s["tipo"] == "video":
            L.append("- **▶ VÍDEO · %g minutos** — %s" % (s["minutos"], s["resumo"]))
            for j, p in enumerate(s["percurso"], 1):
                L.append("- **%d.** %s" % (j, p))
        elif s["tipo"] == "encerramento":
            L.append("- > **%s**" % s["frase"])
            L.append("- %s" % s["assinatura"])
        L.append("")

        if s.get("fala"):
            L.append("### O que a narradora fala\n")
            L.append(s["fala"] + "\n")

        if s["tipo"] == "video":
            L.append("### Produção deste vídeo\n")
            L.append("Gravar %g minutos cobrindo, nesta ordem:\n" % s["minutos"])
            for j, p in enumerate(s["percurso"], 1):
                L.append("%d. %s" % (j, p))
            L.append("")

        L.append("---\n")

    SAIDA.write_text("\n".join(L), encoding="utf-8")
    return SAIDA, len(S), fala_total, video_total


if __name__ == "__main__":
    caminho, n, f, v = build()
    print("gravado: %s" % caminho)
    print("lâminas: %d | falado: %s | vídeos: %g min | total: %s"
          % (n, tempo(f), v, tempo(f + v)))

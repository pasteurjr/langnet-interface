# -*- coding: utf-8 -*-
"""Gera a V4 do deck: pipeline de ML, algoritmos e vídeo de 20 minutos."""
from pathlib import Path
import re
from pptx import Presentation

HERE = Path(__file__).resolve().parent
OUT = HERE / "output" / "apresentacao_iasdd_v4_biobyte.pptx"
import sys
sys.path.insert(0, str(HERE))
import build_deck_iasdd_v2_biobyte as base

D = base.D
TOTAL = 73


def slide(prs, block, title):
    s = D._blank(prs)
    D.header(s, block, "Bloco 1 · Fundamentos de IA", title)
    return s


def register(title, minutes, script):
    base.base.reg(0, 1, title, minutes, 0, script)


def ml_pipeline(prs):
    s = slide(prs, 1, "Pipeline de Machine Learning")
    D.cards(s, 1, [
        ("1 · VISUALIZAR", "entender distribuição e relações"),
        ("2 · PREPARAR", "limpar, transformar e normalizar"),
        ("3 · DIVIDIR", "treino, validação e teste"),
        ("4 · ESCOLHER", "modelo e hiperparâmetros"),
        ("5 · TREINAR", "aprender padrões nos dados"),
        ("6 · AVALIAR", "medir generalização em dados novos"),
    ], x=.6, y=2.15, size=13.5)
    D.callout(s, 1, [("Machine Learning é um processo completo: ", {"size": 16, "bold": True, "color": D.INK}),
                     ("dados → modelo → evidência", {"size": 16, "bold": True, "color": D.FAM['violet'][0]}),
                     (". O algoritmo é apenas uma etapa.", {"size": 16, "color": D.INK})], y=5.2, h=.85)
    D.footer(s, 1, 8, TOTAL)
    register("Pipeline de Machine Learning", 1.5,
             "Antes de escolher um algoritmo, precisamos entender o pipeline. Primeiro visualizamos os dados para conhecer sua distribuição e suas relações. Depois limpamos, transformamos e normalizamos os fatores. Em seguida separamos treinamento, validação e teste. Só então escolhemos o modelo e seus hiperparâmetros, treinamos com os dados de desenvolvimento e avaliamos em dados que o modelo ainda não viu. A ideia central é simples: Machine Learning é um processo de dados, modelo e evidência; o algoritmo é apenas uma etapa.")


def ml_evaluation(prs):
    s = slide(prs, 1, "Treinamento e avaliação: o modelo generaliza?")
    D.table(s, 1, ["Etapa", "Pergunta", "Sinal de alerta"], [
        ["Treinamento", "O modelo aprendeu os exemplos?", "perda cai e acurácia sobe"],
        ["Teste", "Ele funciona em dados novos?", "diferença entre treino e teste"],
        ["Diagnóstico", "Que tipo de erro ocorre?", "falsos positivos e negativos"],
        ["Métrica", "A medida serve ao problema?", "acurácia inadequada ao risco"],
    ], x=.7, y=2.0, w=11.9, h=3.25, fsize=13, header_fs=13)
    D._txt(s, .85, 5.7, 11.6, .7, [[("Overfitting", {"size": 16, "bold": True, "color": D.FAM['rose'][0]}),
                                      (" = memoriza o treinamento; ", {"size": 16, "color": D.INK}),
                                      ("underfitting", {"size": 16, "bold": True, "color": D.FAM['violet'][0]}),
                                      (" = não aprende o suficiente. Avaliar é medir a generalização.", {"size": 16, "color": D.INK})]])
    D.footer(s, 1, 9, TOTAL)
    register("Treinamento e avaliação", 1.5,
             "Treinar não é provar que o modelo funciona. O conjunto de treinamento mostra se ele aprendeu os exemplos; o conjunto de teste mostra se ele generaliza para dados novos. Precisamos observar overfitting, quando o modelo memoriza o treinamento, e underfitting, quando ele não aprende o suficiente. A matriz de confusão organiza falsos positivos, falsos negativos, verdadeiros positivos e verdadeiros negativos. A métrica depende do risco: em diagnóstico, recall pode ser mais importante que acurácia; em outras situações, precisão, F-score, ROC e AUC podem ser mais adequados.")


def ml_algorithms(prs):
    s = slide(prs, 1, "Principais algoritmos e para que servem")
    D.table(s, 1, ["Família", "Objetivo principal", "Exemplo de uso"], [
        ["Regressão linear", "prever valor numérico", "risco ou medida contínua"],
        ["Regressão logística", "classificar e estimar probabilidade", "evento presente/ausente"],
        ["Árvore / Random Forest", "regras e classificação robusta", "triagem e fatores de risco"],
        ["SVM / K-vizinhos", "separar ou comparar casos", "classes e similaridade"],
        ["Redes neurais / CNN", "aprender padrões complexos", "texto, imagem e sinais"],
        ["K-Means", "agrupar sem rótulos", "perfis e segmentos"],
    ], x=.55, y=1.8, w=12.1, h=4.9, fsize=11.5, header_fs=12)
    D.footer(s, 1, 10, TOTAL)
    register("Principais algoritmos de Machine Learning", 2.0,
             "Com o pipeline claro, podemos situar os algoritmos. A regressão linear prevê valores numéricos; a regressão logística classifica e estima probabilidades. Árvores de decisão expressam regras legíveis, e Random Forest combina várias árvores para ganhar robustez. Máquinas de vetores de suporte procuram uma boa fronteira entre classes, enquanto K-vizinhos classifica por similaridade. Redes neurais e redes convolucionais aprendem padrões complexos em textos, imagens e sinais. K-Means agrupa dados sem rótulos. A escolha deve partir do problema, dos dados, da necessidade de explicação e do custo do erro.")


def fix_text_and_numbers(path):
    prs = Presentation(str(path))
    for slide_obj in prs.slides:
        for shape in slide_obj.shapes:
            if not getattr(shape, "has_text_frame", False):
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.text = run.text.replace("15 minutos", "20 minutos").replace("15 min", "20 min")
                    run.text = run.text.replace("o caso do PDF: COVID-19 em tomografia", "o exemplo de COVID-19 em tomografia da fonte original")
    for index, slide_obj in enumerate(prs.slides, start=1):
        wanted = f"{index:02d} / {len(prs.slides):02d}"
        for shape in slide_obj.shapes:
            if hasattr(shape, "text") and re.fullmatch(r"\d{1,2} / \d{1,2}", shape.text.strip()):
                for paragraph in shape.text_frame.paragraphs:
                    if paragraph.runs:
                        paragraph.runs[0].text = wanted
                        for run in paragraph.runs[1:]: run.text = ""
    prs.save(str(path))


def build():
    base.base.META = []
    prs = base.base.D.new_prs()
    funcs = [base.base.s1, base.s2, base.base.s3, base.base.s4, base.base.s5,
             base.base.s5b, base.base.s5c, ml_pipeline, ml_evaluation, ml_algorithms,
             base.base.s6, base.base.s7, base.base.s8, base.base.s9, base.base.s10, base.base.s11,
             base.base.s12, base.base.s13, base.base.s14, base.base.s15, base.base.s16, base.base.s17,
             base.base.s18, base.base.s19, base.base.s20, base.base.s21, base.base.s22b,
             base.base.s23, base.base.s24, base.base.s25, base.base.s26, base.base.s27, base.base.s28,
             base.base.s29, base.base.s30, base.base.s31, base.base.s32, base.base.s33, base.base.s_intervalo,
             base.base.s34, base.base.s35, base.base.s36, base.base.s37, base.s38, base.s39, base.base.s40,
             base.base.s41, base.base.s42, base.base.s43, base.base.s44, base.base.s45, base.base.s46,
             base.base.s47, base.base.s48, base.base.s49, base.base.s50, base.base.s51, base.base.s52,
             base.base.s53, base.base.s54, base.base.s55, base.base.s56, base.base.s57, base.s58, base.s59,
             base.s60, base.s61, base.base.s62, base.base.s63, base.base.s64, base.base.s65, base.base.s66,
             base.base.s67]
    for fn in funcs: fn(prs)
    # O novo conteúdo ocupa cinco minutos; o vídeo passa de 15 para 20.
    # Compensações: cinco minutos são retirados de blocos expositivos
    # repetitivos para manter a duração total em 120 minutos.
    targets = {0: 3.0, 1: 10.0, 2: 9.0, 3: 2.0, 4: 8.0, 5: 11.0,
               6: 9.0, 7: 9.0, 8: 3.0, 9: 16.0, 10: 4.0, 11: 31.0, 12: 5.0}
    for block, target in targets.items():
        rows = [x for x in base.base.META if x["block"] == block]
        if block == 11:
            video = [x for x in rows if x["title"].startswith("DEMON") or x["title"].startswith("DEMO")]
            other = [x for x in rows if x not in video]
            if video: video[0]["minutes"] = 20.0; video[0]["title"] = "DEMO BioByte: 20 minutos"
            factor = (target - 20.0) / sum(x["minutes"] for x in other)
            for x in other: x["minutes"] *= factor
        else:
            factor = target / sum(x["minutes"] for x in rows)
            for x in rows: x["minutes"] *= factor
    acum = 0.0
    for x in base.base.META: acum += x["minutes"]; x["acum"] = acum
    prs.save(str(OUT)); fix_text_and_numbers(OUT)
    print(f"PPTX: {OUT} slides: {len(prs.slides)} tempo: {sum(x['minutes'] for x in base.base.META):.2f} min")


if __name__ == "__main__": build()

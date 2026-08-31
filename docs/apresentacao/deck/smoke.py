import decklib as D
prs = D.new_prs()
meta = []
# S1 capa
s = D._blank(prs)
D._rect(s, 0, 0, D.SW, D.SH, fill=D.BG)
D._rect(s, 0, 0, D.SW, 0.22, fill=D.ACCENT)
D._rect(s, 0, D.SH-0.22, D.SW, 0.22, fill=D.ACC2)
D._txt(s, 1.0, 2.4, D.SW-2, 1.6, [[("Engenharia de IA e Desenvolvimento de Software Orientado a Especificação",
      {"size": 34, "bold": True, "color": D.ACCENT})]])
D._txt(s, 1.0, 4.2, D.SW-2, 1.0, [[("Do modelo à spec: como times de software crítico incorporam IA sem perder auditabilidade",
      {"size": 18, "italic": True, "color": D.MUTED})]])
D.notes(s, "Boas-vindas. Apresente-se em 20 segundos citando os 40 anos de engenharia.")
meta.append({"n":1,"title":"Capa","minutes":0.5,"acum":0.5,
             "script":"<b>Boas-vindas.</b> Apresente-se em 20 segundos citando os 40 anos de engenharia e não volte ao assunto."})
# S2 conteúdo
s = D._blank(prs)
D._rect(s, 0, 0, D.SW, D.SH, fill=D.BG)
D.header(s, "Bloco 0 — Abertura", "A tese central da palestra", block="S3")
D.rich_bullets(s, [
  (0, [("O gargalo deixou de ser escrever código. Passou a ser ", "n"), ("especificar e verificar.", "b")]),
  (0, [("Três consequências que vamos provar ao longo das duas horas:", "n")]),
  (1, [("a capacidade de gerar código virou commodity — o ", "n"), ("método", "b"), (", não.", "n")]),
  (1, [("um agente sem ", "n"), ("portão de verificação (gate)", "b"), (" degrada de forma previsível.", "n")]),
  (1, [("a especificação executável é o que torna código de IA ", "n"), ("auditável", "b"), (".", "n")]),
], size=18, gap=10)
D.footer(s, 2, 2)
D.notes(s, "Leia a frase da tese devagar. É o fio condutor.")
meta.append({"n":2,"title":"A tese","minutes":1,"acum":1.5,
             "script":"<b>Leia a tese devagar</b> e deixe no ar. Este slide reaparece no fechamento (S65). As três consequências são o mapa da palestra: commoditização, degradação previsível, auditabilidade."})
prs.save("output/smoke.pptx")
print("pptx salvo")
out,n = D.render_companion_pdf("output/smoke.pptx", meta, "output/smoke_roteiro.pdf", "output/_work")
print("companion pdf:", out, "paginas de slide:", n)

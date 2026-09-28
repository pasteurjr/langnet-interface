#!/usr/bin/env python3
"""Gera o RELATÓRIO DE CONFERÊNCIA do roteiro: cada cena, a sua tela em tamanho grande,
o que a imagem mostra, a medição técnica e o apontamento, se houver."""
import json, os, re
from collections import Counter
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image as RImg,
                                Table, TableStyle, PageBreak)

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, 'roteiro_narrado_v5_biobyte.md')
PDF = os.path.join(BASE, 'conferencia_do_roteiro.pdf')

# ---- o que cada tela mostra, escrito à mão a partir da inspeção visual ----
CONTEUDO = {
 'A0-painel-projetos': 'Painel de projetos do LangNet, com o menu geral e a lista de projetos.',
 'A0b-pipeline-menu': 'Etapa de Documentos aberta, com as doze etapas do pipeline visíveis na coluna da esquerda.',
 '01-documento-fonte': 'Etapa de Documentos com o levantamento de requisitos carregado.',
 'G1-origem-documento': 'A mesma etapa, mostrando de onde o pipeline parte.',
 '02-requisitos-natureza': 'Documento de requisitos aberto: 1.159 linhas, 172 mil caracteres, 22 seções, com o sumário à direita.',
 '02b-requisitos-coluna-natureza': 'Tabela de requisitos com a coluna de origem (🔴 extraído, 🤖 sugerido pela IA) e a de natureza (⚙️ convencional, 🤖 agêntica).',
 'G3-especificacao-geracao': 'Etapa de Especificação: origem escolhida, campo de instruções preenchido e os botões Gerar, Revisar, Refinar e Visualizar.',
 'H1-especificacao-casos-de-uso': 'Caso de uso aberto com o Fluxo Principal em duas colunas: ação do ator e resposta do sistema.',
 'H2-especificacao-fluxo-excecao': 'O mesmo caso de uso, rolado até os Fluxos de Exceção.',
 '03b-caso-de-uso-natureza': 'Ficha do caso de uso com as linhas Natureza (agêntica) e Decisão do Agente.',
 'G4-modelo-dados-geracao': 'Etapa de Modelo de Dados: barra de origem com a especificação e a data, seletor de banco e os botões da etapa.',
 'M1-modelo-entidades': 'Aba Entidades: as tabelas com os seus campos e relacionamentos.',
 'M2-modelo-schema-sql': 'Aba Schema SQL: o DDL das 28 tabelas.',
 'R5-modelo-historico-versoes': 'Histórico da etapa: versão 2, 28 tabelas, e o relatório do validador com nota 75/100 e os 15 problemas apontados.',
 'R2-modelo-pedido': 'O pedido de correção escrito em português no campo de refino.',
 'R4-modelo-coluna-corrigida': 'O esquema depois da correção, com as colunas em DECIMAL(5,2).',
 'G5-interface-geracao': 'Etapa de Interface: instrução escrita antes de gerar e os botões da etapa.',
 '07-interface-telas': 'Especificação de interface com as 30 telas e os componentes declarados.',
 '73-prototipo-tela': 'Protótipo navegável: trilha de auditoria com filtros, verificação de integridade e as entradas encadeadas.',
 '61-ferramentas-resultado': 'Etapa Ferramentas: 3 ferramentas, 3 com implementação, 0 pendentes, com origem e quem usa cada uma.',
 'G6-agentes-tarefas-geracao': 'Etapa de Agentes e Tarefas: origem, nível de detalhamento e os botões.',
 '04b-cinco-tarefas-dois-agentes': 'Documento de Agentes e Tarefas com as cinco tarefas de agente.',
 'H6-ats-rastreabilidade': 'Ficha de uma tarefa: agente, ferramentas, esquema de entrada e saída, restrições, e as linhas UC Relacionado e RF Relacionado.',
 'G7-yaml-geracao': 'Etapa de YAML: abas Agents YAML e Tasks YAML, seleção do documento e o botão de gerar.',
 '05-yaml-crewai': 'Os arquivos de configuração no formato do CrewAI.',
 'G8-sequencia-tarefas': 'Etapa de Sequência de Tarefas com os botões Gerar, Revisar, Refinar e Visualizar.',
 'H5-sequencia-documento': 'A instrução da etapa: o fluxo sai da Especificação, do documento de Agentes e Tarefas e do tasks.yaml.',
 'G9-petri-geracao': 'Etapa da Rede de Petri, com as opções de gerar a partir da origem.',
 'H7-petri-estrutura': 'A rede em estrutura: lugares, transições e o código de cada lugar.',
 '08-rede-de-petri': 'A rede desenhada: 7 lugares e 6 transições.',
 '64-grafo-causa-efeito': 'Grafo de causa e efeito de um caso de uso: causas à esquerda, com os círculos de negação, e os arcos para os efeitos.',
 '65-tabela-de-decisao': 'Tabela de decisão: colunas C1…C12, cada uma uma combinação de causas.',
 '66-casos-de-teste-texto': 'Os casos de teste escritos: entradas (ações do ator) e resposta esperada do sistema.',
 'G10-codigo-geracao': 'Etapa de Geração de Código com os botões Gerar/Atualizar e Visualizar.',
 '09-codigo-gerado': 'A lista dos arquivos gerados.',
 'E0-app-menu': 'Interface do hospital com uma tela de conteúdo aberta; no menu, o losango marca a tela de agente e o ponto a convencional.',
 'E1-cadastro-pacientes': 'Cadastro de Pacientes: 3 de 3 registros, com Novo, Ver, Editar e Excluir.',
 'N1-relatorio-vigilancia': 'Relatórios de vigilância com período, formato e quantidade de registros.',
 'N2-painel-vigilancia': 'Painel de vigilância com casos ativos, escore médio e alertas em aberto.',
 'E2-cadastro-classificacoes': 'Classificações gravadas pelos agentes, com critério e justificativa.',
 'N3-alertas': 'O alerta de multirresistência, com o texto redigido pelo agente.',
 'E4-notificacoes': 'Notificações à equipe: duas entregues e uma com falha, com o motivo.',
 'E3-trilha-auditoria': 'Trilha de auditoria com os dez eventos do ciclo e a marca da entrada anterior.',
 'E5-agente-traducao': 'Tela de tradução com o resultado do agente e a versão do prompt.',
 'E6-agente-classificacao': 'Tela de classificação com a resposta do agente: critério aplicado, resultado e a resposta completa em JSON.',
 'E7-agente-alerta': 'Tela de alerta com a recusa do agente e o motivo da insuficiência.',
 'B0-bancada-inicio': 'Bancada com a rede carregada, o endereço do servidor no ar e as cinco tarefas.',
 'B1-marca-P1': 'A marca no primeiro lugar da rede.',
 'B2-marca-P2': 'A marca no segundo lugar.',
 'B3-marca-P3': 'A marca no terceiro lugar.',
 'B4-marca-P4': 'A marca no quarto lugar.',
 'B5-marca-P5': 'A marca no quinto lugar.',
 '41-bancada-log-disparos': 'Log de disparos com a hora, a transição e as marcas que mudaram de lugar.',
 'C3-painel-inputs': 'Painel de acompanhamento: tarefa iniciada, agente trabalhando, raciocínio, saída final e as 11 etiquetas.',
 '34-bancada-passo': 'A rede com um lugar em erro, bloqueando a transição seguinte.',
 '62-casos-de-teste-etapa': 'Etapa de Casos de Teste com o botão de refinar por conversa.',
}

est = getSampleStyleSheet()
H1 = ParagraphStyle('H1', parent=est['Heading1'], fontSize=18, textColor=colors.HexColor('#1f3a5f'), spaceAfter=10)
H2 = ParagraphStyle('H2', parent=est['Heading2'], fontSize=12.5, textColor=colors.HexColor('#2b5a8c'), spaceBefore=12, spaceAfter=6)
P  = ParagraphStyle('P',  parent=est['BodyText'], fontSize=9.5, leading=13.5)
FALA = ParagraphStyle('F', parent=P, leftIndent=10, backColor=colors.HexColor('#f2f6fb'),
                      borderPadding=6, fontSize=9.2, leading=13, spaceAfter=4)
NOTA = ParagraphStyle('N', parent=P, fontSize=8.4, textColor=colors.HexColor('#555'))
OKST = ParagraphStyle('OK', parent=P, fontSize=8.6, textColor=colors.HexColor('#166534'))
BAD  = ParagraphStyle('BAD', parent=P, fontSize=8.6, textColor=colors.HexColor('#b91c1c'))

def medir(t):
    im = Image.open(t).convert('RGB'); w,h = im.size
    peq = im.resize((150, int(150*h/w)))
    cnt = Counter(peq.getdata()); dom,n = cnt.most_common(1)[0]
    fundo = n/(150*int(150*h/w))
    d = []
    if fundo > 0.72: d.append('mais de 72% de fundo liso')
    if h > 2000: d.append('altura acima de 2000 px — fica ilegível reduzida')
    if len(cnt) < 350: d.append('pouquíssimo conteúdo')
    if w < 1400: d.append(f'largura {w} px — baixa para lâmina')
    return w, h, os.path.getsize(t)//1024, round(fundo*100), len(cnt), d

md = open(MD, encoding='utf-8').read()
cenas = re.split(r'(?m)^## Cena ', md)[1:]
fluxo = []
fluxo.append(Paragraph('Conferência do roteiro — BioByte Sentinela v5', H1))
fluxo.append(Paragraph(
  'Cada cena do roteiro, a sua tela, o que a imagem mostra, a medição técnica e o apontamento. '
  'A medição procura três defeitos: tela quase toda de fundo liso (conteúdo não apareceu), '
  'altura acima de 2.000 px (fica ilegível quando reduzida para a lâmina) e largura baixa demais.', P))
fluxo.append(Spacer(1, 10))

tot = ok = 0
resumo = []
for c in cenas:
    titulo = c.split('\n')[0].strip()
    cab = c.split('**Narração:**')[0]
    telas = re.findall(r'`(telas/[^`]+\.png)`', cab)
    fala = ''
    if '**Narração:**' in c:
        bloco = c.split('**Narração:**')[1].split('**Produção:**')[0]
        fala = ' '.join(l.strip('> ').strip() for l in bloco.splitlines() if l.strip().startswith('>'))
    fluxo.append(Paragraph(f'Cena {titulo}', H2))
    if fala:
        fluxo.append(Paragraph('<b>Narração:</b> ' + fala[:700].replace('&','&amp;').replace('<','&lt;'), FALA))
    for t in telas:
        tot += 1
        caminho = os.path.join(BASE, t)
        if not os.path.exists(caminho):
            fluxo.append(Paragraph(f'<b>{t}</b> — <b>A TELA NÃO EXISTE</b>', BAD)); resumo.append((titulo,t,'não existe')); continue
        w,h,kb,fundo,cores,d = medir(caminho)
        chave = os.path.basename(t)[:-4]
        desc = CONTEUDO.get(chave, '—')
        fluxo.append(Paragraph(f'<b>{t}</b> — {desc}', P))
        fluxo.append(Paragraph(f'{w}×{h} px · {kb} KB · {fundo}% de fundo liso · {cores} cores', NOTA))
        if d:
            fluxo.append(Paragraph('APONTAMENTO: ' + '; '.join(d), BAD)); resumo.append((titulo,t,'; '.join(d)))
        else:
            fluxo.append(Paragraph('sem apontamento', OKST)); ok += 1
        try:
            img = Image.open(caminho); r = img.height/img.width
            larg = 15.0*cm
            fluxo.append(RImg(caminho, width=larg, height=min(larg*r, 11.5*cm)))
        except Exception as e:
            fluxo.append(Paragraph(f'[imagem não pôde ser embutida: {e}]', NOTA))
        fluxo.append(Spacer(1, 8))
    fluxo.append(Spacer(1, 6))

# resumo no começo
cabecalho = [Paragraph('<b>Resultado</b>', H2),
             Paragraph(f'{len(cenas)} cenas · {tot} telas · <b>{ok} sem apontamento</b> · {tot-ok} com apontamento', P)]
if resumo:
    linhas = [['Cena','Tela','Apontamento']] + [[a[:38], b.replace('telas/',''), c] for a,b,c in resumo]
    t = Table(linhas, colWidths=[5*cm, 5.5*cm, 6*cm])
    t.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),7.6),('GRID',(0,0),(-1,-1),0.3,colors.grey),
                           ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eef2f7')),
                           ('VALIGN',(0,0),(-1,-1),'TOP')]))
    cabecalho.append(t)
else:
    cabecalho.append(Paragraph('Nenhuma tela ficou com apontamento.', OKST))
cabecalho.append(PageBreak())
fluxo = fluxo[:2] + cabecalho + fluxo[2:]

SimpleDocTemplate(PDF, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                  leftMargin=2*cm, rightMargin=2*cm,
                  title='Conferência do roteiro — BioByte Sentinela v5').build(fluxo)
print('PDF:', PDF, os.path.getsize(PDF)//1024, 'KB')
print(f'{len(cenas)} cenas, {tot} telas, {ok} sem apontamento, {tot-ok} com apontamento')

"""O portão de lógica separa INSTRUÇÃO AO AGENTE de LACUNA de implementação.

Uma tarefa de IA é, na maior parte, instrução: proibição, entrada, julgamento em texto.
Cobrar código disso reprovava a geração por construção. Continua cobrado o passo que
manda contar, comparar, calcular ou consultar o banco — esses o agente erra.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backend")
from agents.langnetagents import _passo_e_instrucao_ao_agente as f

INSTRUCAO = [  # não é lacuna: o agente faz
    '6. NÃO inventar microrganismo, antibiograma ou classe quando situacao = "pendente".',
    "7. NÃO mapear termo ambíguo para correspondência inventada.",
    "9. NÃO consultar tabelas fora do schema biobyte.",
    "1. Receber o resultado bruto do laboratório e a versão do vocabulário do hospital.",
    "4. Se múltiplos critérios cobrirem a data: escolher o de vigência mais recente e citar na justificativa.",
    "5. Redigir o texto do alerta em linguagem clínica.",
    "4. Para cada termo sem correspondência, adicionar em termos_nao_mapeados e marcar aproveitavel = false.",
]
LACUNA = [  # é lacuna de verdade: tem de virar código
    "3. Contar quantas classes de antimicrobianos apresentam resistência.",
    "4. Se a contagem for maior que 3, marcar multirresistente.",
    "2. Calcular o percentual de redução de risco.",
    "5. Consultar a tabela resultados_hemocultura pelo identificador da amostra.",
    "6. Gravar na tabela classificacoes o critério escolhido.",
    "7. Comparar o escore com o limiar: se maior que 0.7, alto risco.",
]

falhas = []
for linha in INSTRUCAO:
    if not f(linha):
        falhas.append(("deveria ser INSTRUCAO", linha))
for linha in LACUNA:
    if f(linha):
        falhas.append(("deveria ser LACUNA", linha))

total = len(INSTRUCAO) + len(LACUNA)
print(f"casos: {total} | passaram: {total - len(falhas)} | falharam: {len(falhas)}")
for m, l in falhas:
    print(f"  X {m}: {l[:90]}")
sys.exit(1 if falhas else 0)

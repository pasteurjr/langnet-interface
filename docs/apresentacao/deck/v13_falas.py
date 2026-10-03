# -*- coding: utf-8 -*-
"""Falas da V13: as da V12, sem alteração, mais as duas lâminas de infraestrutura."""
from v12_falas import FALAS as F12

NOVAS = {
"Infraestrutura: a GPU, e onde treinar":
"Uma palavra sobre infraestrutura. Tudo isso roda em GPU, a placa de vídeo: milhares de núcleos simples fazendo em paralelo a multiplicação de matrizes. E o que manda é a memória da placa. Há placas pessoais, de doze a trinta e dois gigabytes, e placas de datacenter, com oitenta ou mais. Para começar, o Google Colab dá GPU no navegador; para escalar, aluga-se por hora na AWS, no Google Cloud ou no Azure. Regra de bolso: um modelo de vinte e sete bilhões em quatro bits ocupa uns dezesseis gigabytes; ajuste fino cabe numa placa pessoal; treinar do zero, só em cluster.",

"A nossa infraestrutura":
"E esta é a nossa. A máquina principal tem um i7 de décima segunda geração, cento e vinte e oito gigabytes de memória e três placas, uma RTX 5080, uma 5060 e uma 4060, com dois discos NVMe de dois terabytes. Ela serve os modelos abertos para o LangNet e faz os treinos pesados. A de apoio, com noventa e seis gigabytes e uma RTX 3060, fica com os treinos menores e os notebooks. O motivo de ter isso em casa: o dado sensível não sai, e o modelo local faz o trabalho repetitivo sem gastar tokens pagos.",
}

FALAS = dict(F12)
FALAS.update(NOVAS)
FIM = "__fim__"


def aplicar(slides):
    faltam = [s.get("titulo", FIM) for s in slides if s.get("titulo", FIM) not in FALAS]
    if faltam:
        raise SystemExit("sem fala na V13: %s" % faltam)
    for s in slides:
        s["fala"] = FALAS[s.get("titulo", FIM)]
    return slides

# Documento de Legislação — Parâmetros Urbanísticos de Uso e Ocupação do Solo

**Finalidade:** complementa os requisitos do sistema com os **parâmetros urbanísticos** que devem ser
verificados na avaliação de conformidade de um empreendimento contra a **zona** de uso do solo.

## Base legal
- **Lei de Uso e Ocupação do Solo (LUOS)** e **Plano Diretor** municipais (cada município define os
  valores por zona). Ex.: Belo Horizonte — Lei nº 7.166/1996 e alterações.

## Requisito funcional: verificação dos parâmetros por zona
Para cada empreendimento, o sistema DEVE identificar a **zona** (por geoprocessamento — a poligonal do
zoneamento que contém o imóvel) e comparar o **projeto** com os **limites da zona**:

| Parâmetro | Definição | Verificação (projeto × limite da zona) |
|---|---|---|
| Coeficiente de Aproveitamento (CA) | área construída ÷ área do terreno | `área_construída ≤ CA_máx × área_terreno` |
| Taxa de Ocupação (TO) | % do terreno coberto pela projeção | `projeção ÷ terreno ≤ TO_máx` |
| Taxa de Permeabilidade (TP) | % mínimo de solo permeável | `área_permeável ÷ terreno ≥ TP_mín` |
| Recuos/Afastamentos | distâncias mínimas às divisas (frontal/lateral/fundos) | comparar com o mínimo da zona |
| Gabarito | altura máxima / nº de pavimentos | `altura ≤ gabarito_máx` |
| Área/testada mínima de lote | dimensões mínimas | `área_lote ≥ mínimo` |
| Uso permitido | usos da zona (residencial/comercial/industrial/misto) | uso do empreendimento ∈ usos permitidos |

**Exemplo:** lote 720 m², zona com CA 2,0 e TO 50% → área construível máx 1.440 m², projeção máx 360 m².

## Regras de conformidade que o sistema deve gerar (por zona)
Cada parâmetro da zona vira uma **regra aplicável** e, quando incidir, um **requisito**:
- `tipo = urbanistico`
- `fundamentacao_legal` = ex. "Plano Diretor Municipal, art. X" / "LUOS, Anexo de zoneamento"
- `parametro` = CA | TO | TP | recuo_frontal | gabarito | uso_permitido
- `valor_exigido` = ex. "CA ≤ 2,0", "TO ≤ 50%", "uso residencial"
- `valor_projeto` = valor informado do projeto; `situacao` = conforme | nao_conforme | pendente

## Impacto no modelo de dados / tarefas
- Tarefa `avaliar_conformidade_urbanistica`: compara o projeto com os parâmetros da zona incidente e
  gera requisitos urbanísticos com fundamentação e valor exigido.
- Zoneamento deve armazenar, por zona, os limites (CA, TO, TP, recuos, gabarito, usos permitidos).

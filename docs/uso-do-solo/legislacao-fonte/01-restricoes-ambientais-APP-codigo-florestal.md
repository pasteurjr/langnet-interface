# Documento de Legislação — Restrições Ambientais e APP (Código Florestal)

**Finalidade:** este documento complementa os requisitos do sistema de avaliação de uso do solo.
Descreve as **restrições ambientais** que o sistema DEVE verificar automaticamente (por
geoprocessamento) ao avaliar a conformidade de um imóvel/empreendimento.

## Base legal
- **Lei nº 12.651/2012 (Código Florestal)** — Áreas de Preservação Permanente (APP) e Reserva Legal.
- Aplicável em zonas **urbanas e rurais**, observados o Plano Diretor e a lei de uso do solo municipal.

## Requisito funcional: verificação de APP (Área de Preservação Permanente)
O sistema DEVE, a partir da **localização georreferenciada** do imóvel e das **bases hidrográficas e de
relevo**, calcular se o imóvel incide em APP e gerar o requisito correspondente. Faixas mínimas (art. 4):

| Feição | Faixa de APP (verificar por buffer/ST_DWithin) |
|---|---|
| Curso d'água natural < 10 m de largura | 30 m de cada margem |
| Curso d'água 10 a 50 m | 50 m |
| Curso d'água 50 a 200 m | 100 m |
| Curso d'água 200 a 600 m | 200 m |
| Curso d'água > 600 m | 500 m |
| Nascente / olho d'água perene ou intermitente | raio de 50 m |
| Lago/lagoa natural em área urbana | 30 m |
| Lago/lagoa natural em área rural | 50 m (espelho < 20 ha) / 100 m (≥ 20 ha) |
| Encostas | declividade superior a 45° |
| Topo de morros/montanhas | terço superior da elevação |

## Requisito: Reserva Legal (imóvel rural)
Percentual mínimo de vegetação nativa a manter: 20% (regra geral / Mata Atlântica) até 80% (Amazônia Legal).

## Regras de conformidade que o sistema deve gerar (por zona/imóvel)
- Se o imóvel **intersecta APP** → requisito **ambiental**, `fundamentacao_legal = "Lei 12.651/2012, art. 4"`,
  `parametro = "APP"`, `valor_exigido = "faixa mínima non aedificandi"`, `situacao = nao_conforme` se houver
  edificação na faixa, senão `conforme`.
- Se declividade > 45% na área do imóvel → requisito ambiental (restrição de ocupação).
- Emitir a **fundamentação legal** e o **valor exigido** em cada requisito gerado.

## Impacto no modelo de dados / tarefas
- Tarefa `avaliar_restricoes_ambientais`: usa geoprocessamento (interseção com hidrografia/nascentes,
  declividade a partir de modelo digital de elevação) e gera requisitos ambientais com fundamentação.
- Requisito gerado deve conter: `tipo=ambiental`, `fundamentacao_legal`, `parametro`, `valor_exigido`, `situacao`.

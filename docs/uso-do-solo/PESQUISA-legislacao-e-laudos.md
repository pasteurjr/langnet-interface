# Pesquisa — Legislação de uso do solo + formato de laudos (para complementar os requisitos)

**Data:** 22/08/2026 · **Contexto:** enriquecer o que o app "Uso do Solo" gera como requisitos de
conformidade e como estrutura o laudo/parecer técnico.

---

## 1. Dimensões de conformidade do uso do solo (o que checar → vira requisito)

### 1.1 Parâmetros urbanísticos (Lei de Uso e Ocupação do Solo / Plano Diretor — municipal)
Cada município define os valores por **zona**; o sistema deve comparar o **projeto** com o **limite da zona**:

| Parâmetro | Definição | Cálculo / verificação |
|---|---|---|
| **Coeficiente de Aproveitamento (CA)** | área construída ÷ área do terreno (básico e máximo) | `área_construída ≤ CA_máx × área_terreno`. Ex.: lote 720 m², CA 2,0 → 1.440 m² |
| **Taxa de Ocupação (TO)** | % do terreno coberto pela projeção da edificação | `projeção ÷ terreno × 100 ≤ TO_máx` (ex.: 50%) |
| **Taxa de Permeabilidade** | % mínimo de solo permeável | `área_permeável ÷ terreno ≥ TP_mín` |
| **Recuos/Afastamentos** | distâncias mínimas às divisas (frontal/lateral/fundos) | comparar com o mínimo da zona |
| **Gabarito** | altura máx / nº de pavimentos | `altura ≤ gabarito_máx` |
| **Lote/área mínima** | dimensões mínimas do lote | `área_lote ≥ mínimo` |
| **Uso permitido** | usos da zona (residencial/comercial/industrial/misto) | uso do empreendimento ∈ usos permitidos da zona |

### 1.2 Restrições ambientais — Código Florestal (Lei 12.651/2012, art. 4) — **APP**
Faixas de **Área de Preservação Permanente** (o app pode calcular a incidência por geoprocessamento —
`ST_DWithin`/buffer sobre hidrografia/nascentes):

| Feição | Faixa de APP |
|---|---|
| Curso d'água < 10 m de largura | **30 m** de cada margem |
| Curso d'água 10–50 m | **50 m** |
| Curso d'água 50–200 m | **100 m** |
| Curso d'água 200–600 m | **200 m** |
| Curso d'água > 600 m | **500 m** |
| Nascentes / olhos d'água | raio de **50 m** |
| Lagos/lagoas naturais (área **urbana**) | **30 m** |
| Lagos/lagoas naturais (rural) | **50 m** (< 20 ha) / **100 m** (≥ 20 ha) |
| Encostas | declividade **> 45°** |
| Topo de morros/montanhas | terço superior |
| **Reserva Legal** (imóvel rural) | 20% (Mata Atlântica/demais) a 80% (Amazônia Legal) |

Em área **urbana**, APP é observada conjuntamente com o Plano Diretor e a lei de uso do solo municipal
(respeitados os limites do Código Florestal).

### 1.3 Licenciamento ambiental em MG (Sisema — COPAM DN 217/2017 e DN 74/2004)
Fluxo que o app pode espelhar para o **empreendimento**:
- **FCEI** (Formulário de Caracterização do Empreendimento Integrado) → gera o **FOBI** (orientações/documentos exigidos).
- **Classe** = função do **porte** × **potencial poluidor** (classes 1 a 6):
  - Classes **1–2** (impacto não significativo): **AAF** (Autorização Ambiental de Funcionamento) ou dispensa.
  - Classes **3–6**: **licenciamento** (LP/LI/LO ou modalidades LAC/LAT), com estudos (RCA/PCA, EIA/RIMA conforme o caso).
- O Sisema faz **cruzamento espacial** das coordenadas do empreendimento com bases (UCs, hidrografia, etc.) — é exatamente o tipo de análise que a `GeoprocessamentoTool` faz.

---

## 2. Formato de laudo / parecer técnico-ambiental (o que o app deve gerar como documento)

Estrutura consolidada (laudo de viabilidade / parecer):

1. **Identificação / Capa** — responsável técnico (**CREA/CFBio + ART/TRT**), requerente, imóvel (matrícula, coordenadas), data.
2. **Resumo executivo** — síntese e **conclusão de viabilidade**.
3. **Introdução e objetivos** — escopo, área investigada, parâmetros analisados.
4. **Metodologia** — normas ABNT, **geoprocessamento** (bases, SRID, datas), equipamentos.
5. **Caracterização da área** — localização **georreferenciada**, **zona de uso do solo** incidente, geologia/hidrologia, uso atual do solo, **APP/UC incidentes**.
6. **Análise de conformidade** — cada **parâmetro urbanístico** e **restrição ambiental** × projeto → **conforme / não conforme**.
7. **Requisitos / condicionantes** — lista de exigências (uma por regra) + documentos necessários.
8. **Conclusão** — **viável / viável com condicionantes / inviável**.
9. **Referências** — legislação citada (lei/artigo).
10. **Anexos** — mapas, registro fotográfico, ART, certidões.

> Laudo × Parecer: o **laudo** diagnostica as condições; o **parecer** interpreta e conclui sobre a
> viabilidade / condicionantes. O app pode gerar ambos (laudo = caracterização + análise; parecer = conclusão).

---

## 3. Como dobrar isto no sistema (proposta de enriquecimento — pela UI depois)

**Modelo de dados** (enriquecer via etapa Modelo de Dados na UI):
- `regra_aplicavel`: + `tipo` (urbanistico|ambiental|documental), `fundamentacao_legal` (lei/artigo), `parametro` (CA|TO|TP|recuo|gabarito|APP|uso), `valor_exigido`.
- `requisito_gerado`: + `tipo`, `fundamentacao_legal`, `parametro`, `valor_exigido`, `valor_projeto`, `situacao` (conforme|nao_conforme|pendente).
- Nova entidade `laudo`: `consulta_id`, `conclusao` (viavel|condicionado|inviavel), `responsavel_tecnico`, `art`, `documento` (o laudo montado), `data_emissao`.

**Tarefas agênticas** (Agent-Task Spec):
- `avaliar_conformidade_urbanistica` — compara projeto × parâmetros da zona.
- `avaliar_restricoes_ambientais` — `GeoprocessamentoTool` (APP por `ST_DWithin` sobre hidrografia/nascentes; declividade por raster/QGIS).
- `classificar_empreendimento` — porte × potencial poluidor → classe/modalidade (Sisema).
- `emitir_laudo` — monta o documento na estrutura da Seção 2 (caracterização + análise + requisitos + conclusão).

**GeoprocessamentoTool** (já existe) cobre: zona do imóvel (`zonas_do_ponto`), APP incidente (`buffer`/`ST_DWithin`),
área/distância, e — via QGIS (679 algoritmos) — declividade a partir de MDE, interseção com UCs, etc.

---

## Fontes
- [Taxa de ocupação e coeficiente de aproveitamento — Urbanidades](https://urbanidades.arq.br/2020/03/29/taxa-de-ocupacao-e-coeficiente-de-aproveitamento-v-2-0/)
- [Lei nº 7166/1996 (parâmetros urbanísticos) — Belo Horizonte](https://www.legisweb.com.br/legislacao/?id=172504)
- [Como fazer um laudo técnico ambiental — SR Geologia & Ambiental](https://srgeologia.com.br/como-fazer-um-laudo-tecnico-ambiental/)
- [Laudo de viabilidade ambiental — Ambifort](https://www.ambifort.com.br/laudo-viabilidade-ambiental)
- [AAF — SEMAD/SISEMA (MG)](https://meioambiente.mg.gov.br/w/aaf)
- [Deliberação Normativa COPAM nº 217/2017](https://www.siam.mg.gov.br/sla/download.pdf?idNorma=45558)
- [Deliberação Normativa COPAM nº 74/2004 (classes)](https://www.siam.mg.gov.br/sla/download.pdf?idNorma=37095)
- [Código Florestal (Lei 12.651/2012) — APP e Reserva Legal — Ambiensys](https://ambiensys.com.br/post/codigo-florestal-app-reserva-legal)
- [Áreas de Preservação Permanente Urbanas — Jusbrasil](https://www.jusbrasil.com.br/artigos/areas-de-preservacao-permanente-urbanas/1372041318)

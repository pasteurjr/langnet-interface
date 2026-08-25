# Documento de Legislação — Licenciamento Ambiental (Sisema/MG) e Classificação

**Finalidade:** complementa os requisitos com a **classificação do empreendimento** e a **modalidade de
regularização ambiental** exigida no estado de Minas Gerais, integrando com a IDE Sisema.

## Base legal / institucional
- **Sisema** — Sistema Estadual de Meio Ambiente (SEMAD/FEAM/IEF/IGAM) de Minas Gerais.
- **Deliberação Normativa COPAM nº 217/2017** — classifica empreendimentos por **porte × potencial
  poluidor** (classes 1 a 6) e define a modalidade de licenciamento.
- **DN COPAM nº 74/2004** (referência histórica de classes 1–2 de impacto não significativo).

## Requisito funcional: classificar e orientar a regularização
O sistema DEVE, a partir da **atividade**, do **porte** e do **potencial poluidor** do empreendimento:
1. Determinar a **classe (1 a 6)** conforme o cruzamento porte × potencial poluidor.
2. Indicar a **modalidade**:
   - Classes **1–2** (impacto não significativo): **AAF** (Autorização Ambiental de Funcionamento) ou dispensa.
   - Classes **3–6**: **licenciamento ambiental** (LP/LI/LO ou modalidades LAC/LAT), com estudos exigidos
     (RCA/PCA; EIA/RIMA quando aplicável).
3. Gerar a **lista de documentos exigidos** (espelhando o fluxo **FCEI → FOBI**: o preenchimento da
   caracterização do empreendimento gera as orientações/documentos necessários).

## Integração georreferenciada (IDE Sisema)
O sistema DEVE cruzar as **coordenadas do empreendimento** com bases oficiais (zoneamento, hidrografia,
Unidades de Conservação, restrições) — análise espacial equivalente à que o Sisema faz. Fonte de dados:
serviços **OGC WMS/WFS** da IDE Sisema (carga de camadas para o banco geoespacial).

## Regras de conformidade que o sistema deve gerar
- Requisito `tipo = documental` para cada documento exigido pela classe/modalidade.
- `fundamentacao_legal = "DN COPAM 217/2017"`, `parametro = "classe/modalidade"`,
  `valor_exigido` = ex. "AAF" ou "Licenciamento LP/LI/LO".

## Impacto no modelo de dados / tarefas
- Tarefa `classificar_empreendimento`: calcula classe e modalidade e gera requisitos documentais.
- Empreendimento deve conter porte e potencial poluidor (já existem no modelo); adicionar `classe` e
  `modalidade_licenciamento` conforme a avaliação.

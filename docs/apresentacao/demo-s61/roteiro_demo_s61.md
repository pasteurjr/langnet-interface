# Roteiro de Demonstração — S61: da especificação ao aplicativo (LangNet → Uso do Solo)

**Vídeo gravado, sem áudio, legendas grandes.** Duração do vídeo: **2:28** · fala ao vivo do apresentador ao fim: **~30 s** · total do slide: **3:00**.

> Regra de ouro (S61): acelere as esperas 2×–4× com o **tempo real** carimbado na legenda; deixe a **spec** e o **portão verde** parados para leitura; e **não corte** a falha de teste.


| # | Fase | Entra | Dura | Velocidade |
|---|------|-------|------|------------|
| 1 | Especificação (a fonte) | 0:00 | 18s | tempo real (sem aceleração) |
| 2 | Modelo de Dados (PostGIS) | 0:18 | 14s | 2× ao trocar de aba; pausa de 2 s na coluna geométrica |
| 3 | UI Spec & Protótipo | 0:32 | 16s | 2×; tempo real no protótipo do laudo |
| 4 | Agent-Task Spec → tasks.yaml | 0:48 | 14s | 2×; pausa de 2 s no bloco da task |
| 5 | Rede de Petri | 1:02 | 13s | tempo real; opcional 'Simular' por 2 s |
| 6 | Código gerado (real, do repositório) | 1:15 | 14s | tempo real; realce nas 2 linhas-chave |
| 7 | App implantado: mapa | 1:29 | 15s | tempo real; movimento suave no mapa |
| 8 | Calculador ponta a ponta | 1:44 | 16s | tempo real no clique e no resultado; 2× entre os dois casos |
| 9 | Resultados persistidos no banco | 2:00 | 14s | tempo real; 2× na rolagem da tabela |
| 10 | Portão de rastreabilidade VERDE | 2:14 | 14s | tempo real; congela 3 s no verde |
| — | **Fala ao vivo do apresentador** | 2:28 | ~30s | tempo real, você falando |


---

## Tomada 1 · Especificação (a fonte)

**Tempo:** 0:00 → 0:18  (18 s)  ·  **Velocidade:** tempo real (sem aceleração)

**Imagem/tela:** `01_specification.png`

**Legenda (aparece na tela — é o texto narrado):**

> Tudo começa com uma especificação — a Plataforma de Gestão de Uso do Solo e Cálculos Urbanísticos.

**Produção da tela (como gravar/capturar):**

No LangNet, abra o projeto Uso do Solo → etapa Especificação → botão Histórico → carregue a versão gerada → clique Visualizar. A janela mostra o documento REAL (Introdução, Escopo: eixo operacional, urbanístico, ambiental e IA). Role devagar pelas seções; deixe legível. NÃO acelere.


---

## Tomada 2 · Modelo de Dados (PostGIS)

**Tempo:** 0:18 → 0:32  (14 s)  ·  **Velocidade:** 2× ao trocar de aba; pausa de 2 s na coluna geométrica

**Imagem/tela:** `02_data_model.png`

**Legenda (aparece na tela — é o texto narrado):**

> Da spec deriva o modelo de dados: PostgreSQL/PostGIS, 17 tabelas — com colunas de geometria SRID 4674.

**Produção da tela (como gravar/capturar):**

Etapa Modelo de Dados: mostre 'Aprovado · v4 · POSTGRESQL · 17 tabelas' e as tabelas (municipios, zoneamentos com coluna GEOMETRY). Passe pelas abas Entidades → Schema SQL → models.py → Alembic para provar que gera o DDL, os modelos e as migrations.


---

## Tomada 3 · UI Spec & Protótipo

**Tempo:** 0:32 → 0:48  (16 s)  ·  **Velocidade:** 2×; tempo real no protótipo do laudo

**Imagem/tela:** `03_ui_spec.png`

**Legenda (aparece na tela — é o texto narrado):**

> Antes do código, as telas: 10 telas geradas por caso de uso — com protótipo interativo do laudo.

**Produção da tela (como gravar/capturar):**

Etapa Interface & Protótipo: mostre a lista de 10 telas (Resultado de Conformidade, Cálculos Urbanísticos, Mapa de Consulta, Dashboard, Simulação…) e, à direita, o protótipo do 'Resultado de Conformidade' com o mapa e o resumo CA/TO/Recuos/APP. É a interface planejada, não improvisada.


---

## Tomada 4 · Agent-Task Spec → tasks.yaml

**Tempo:** 0:48 → 1:02  (14 s)  ·  **Velocidade:** 2×; pausa de 2 s no bloco da task

**Imagem/tela:** `06_yaml_tasks.png`

**Legenda (aparece na tela — é o texto narrado):**

> As tarefas viram YAML rastreável: cada task com uc/fr, execução determinística e o SQL PostGIS.

**Produção da tela (como gravar/capturar):**

Etapa YAML → aba Tasks YAML → Visualizar. Mostre uma task real (ex.: import_zoneamento_geodata) com traceability {uc, fr}, execution: deterministic e o INSERT com ST_GeomFromText(..., 4674). É o contrato de cada tarefa, ligado ao requisito.


---

## Tomada 5 · Rede de Petri

**Tempo:** 1:02 → 1:15  (13 s)  ·  **Velocidade:** tempo real; opcional 'Simular' por 2 s

**Imagem/tela:** `07_petri.png`

**Legenda (aparece na tela — é o texto narrado):**

> A orquestração vira uma Rede de Petri gerada de agents.yaml + tasks.yaml — verificável, não só código.

**Produção da tela (como gravar/capturar):**

Etapa Rede de Petri: mostre o canvas com 'Início do Fluxo' (com o token), o T_start e as transições/tarefas (consultar_regramentos, gerar_dashboard, gerenciar_permissoes…) até 'Fim do Fluxo'. Se quiser, clique Simular por 2 s para mover o token.


---

## Tomada 6 · Código gerado (real, do repositório)

**Tempo:** 1:15 → 1:29  (14 s)  ·  **Velocidade:** tempo real; realce nas 2 linhas-chave

**Imagem/tela:** `12_code_real.png`

**Legenda (aparece na tela — é o texto narrado):**

> O calculador CA/TO nasceu da spec — determinístico, sem LLM, sem edição manual.

**Produção da tela (como gravar/capturar):**

Abra o arquivo REAL ws-server/adapters.py no editor e role até calculate_urban_compliance. Realce a consulta SQL com JOIN (zoneamentos + parametros + imoveis por ST_Contains) e a linha do status conforme/não-conforme. É o código do repositório, não slide.


---

## Tomada 7 · App implantado: mapa

**Tempo:** 1:29 → 1:44  (15 s)  ·  **Velocidade:** tempo real; movimento suave no mapa

**Imagem/tela:** `01-app-home.png`

**Legenda (aparece na tela — é o texto narrado):**

> O aplicativo de verdade rodando: mapa Leaflet, desenho de área, importação de Shapefile, laudo em PDF.

**Produção da tela (como gravar/capturar):**

Abra o app gerado em http://localhost:3001 na tela Resultado de Conformidade. Mova o mapa, passe por cima das ferramentas de desenho e do botão Gerar Laudo PDF. É a interface REAL gerada, contra PostGIS.


---

## Tomada 8 · Calculador ponta a ponta

**Tempo:** 1:44 → 2:00  (16 s)  ·  **Velocidade:** tempo real no clique e no resultado; 2× entre os dois casos

**Imagem/tela:** `02-calculos-urbanisticos.png`

**Legenda (aparece na tela — é o texto narrado):**

> Preenche a área, clica Calcular — CA=1,5 → conforme. Com área maior, CA=2,5 → não-conforme.

**Produção da tela (como gravar/capturar):**

Tela Cálculos Urbanísticos: preencha Área Construída = 1500 e Projeção = 500, clique Calcular e mostre o resultado 'conforme'. Repita com 2500 → 'não-conforme'. O cálculo roda no ws-server contra o PostGIS — é o E2E de verdade.


---

## Tomada 9 · Resultados persistidos no banco

**Tempo:** 2:00 → 2:14  (14 s)  ·  **Velocidade:** tempo real; 2× na rolagem da tabela

**Imagem/tela:** `07-calculos-conformidade-crud.png`

**Legenda (aparece na tela — é o texto narrado):**

> Os resultados ficam gravados: CA, TO e status por imóvel — inclusive uma linha não-conforme.

**Produção da tela (como gravar/capturar):**

Abra a lista Cálculos Conformidade (CRUD) mostrando as linhas gravadas no PostGIS: CA_CALCULADO, TO_CALCULADA, STATUS_CA, STATUS_TO — com a linha 2,50 / não_conforme ao lado das conformes. Prova de que o app persiste de verdade.


---

## Tomada 10 · Portão de rastreabilidade VERDE

**Tempo:** 2:14 → 2:28  (14 s)  ·  **Velocidade:** tempo real; congela 3 s no verde

**Imagem/tela:** `gate_verde.png`

**Legenda (aparece na tela — é o texto narrado):**

> De volta à spec: 37/37 requisitos rastreados até o código. Verde em todos os saltos.

**Produção da tela (como gravar/capturar):**

Rode o portão de rastreabilidade (CLI tools/langnet_trace_gate.py ou o painel na UI) e mostre a saída VERDE — 37/37 FR, e todos os hops OK (Req→Spec, Matriz, FR→Implementação, Task→DM, Task→código). Congele 2–3 s: é o clímax que fecha o arco spec → código → verificação.


---

## Fala ao vivo do apresentador (~30 s, depois do vídeo)

> "O que vocês viram rodou de verdade: **spec de 15 linhas → aplicativo completo**, com mapa, cálculo e banco. O número que importa não é a taxa de acerto do modelo — é que o **portão determinístico pegou ~10 erros do gerador antes do deploy**, e a rastreabilidade fechou **37 de 37**. Tempo real de ponta a ponta: [preencher] minutos; tokens: [preencher]; e corrigi à mão: [preencher]."


### Checklist de gravação

- [ ] Resolução 1920×1080, cursor grande, tema claro do sistema.
- [ ] Legendas em fonte grande (≥ 32 pt), alto contraste, uma frase por tomada.
- [ ] Carimbo de **tempo real** no canto quando acelerar (ex.: "12 s reais · 4×").
- [ ] App no ar: frontend :3001, ws-server :5030, PostGIS (uso_solo_green).
- [ ] Gravar a **falha de teste real** (tomada 11) — não encenar.
- [ ] Congelar 3 s no **portão verde** (tomada 12).

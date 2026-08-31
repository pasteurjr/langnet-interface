# Engenharia de IA, Agentes e SDD — Planejamento de Apresentação
**Versão 6.0** — plateia: desenvolvedores sêniores, empresa de sistemas para controle de infecção hospitalar (IRAS)
Duração: 120 minutos | 68 slides | intervalo incluído

> **Como ler esta v6:** é a v5 **preservada integralmente** (mesmo título, mesma estrutura, mesma numeração S1–S67, todo o conteúdo e todos os números). As únicas alterações estão marcadas inline com **`[v6]`** — assim você vê exatamente o que mudou. Nada foi removido; só houve acréscimo/refinamento nos pontos abaixo.

## Mudanças da v4 para a v5
1. **CrewAI e AutoGen ganham slides próprios** (S38 e S39), com o mesmo peso dos SDKs da OpenAI e da Anthropic e do LangGraph.
2. **OKF ganha slide dedicado** (S31), separado do AGENTS.md / DESIGN.md / Skills, que ficaram no S32.
3. **Novo S62 — como o AI Co-Scientist funciona**, com o mecanismo completo do paper da Nature: as três fases, os seis agentes, o supervisor, o torneio Elo e o laço de meta-revisão.
4. Cortes proporcionais para caber: contexto (−1), agentes (−1), ambientes (−1), Bloco 3 (−0,5), Bloco 1 (−0,5), adaptação (−1).

## Mudanças da v5 para a v6 `[v6]`
*(Somente refinamento — estrutura, numeração, título e conteúdo da v5 intactos.)*
1. **S62 e S58 enriquecidos com detalhe de FONTE PRIMÁRIA** do paper (Gottweis et al., *Accelerating scientific discovery with Co-Scientist*, **Nature 2026** — `s41586-026-10644-y` / arXiv **2502.18864**, base **Gemini 2.0**): papéis exatos dos agentes, **Elo inicial 1200**, debate multi-turno × turno único, **validação GPQA AUC 0,643→0,651**, meta-revisão realimentando o Reflection, e o caso de **resistência antimicrobiana via cf-PICIs** em ***E. coli*/*K. pneumoniae*** — o mais relevante para esta plateia.
2. **S60** passa a citar **números reais medidos** na validação do LangNet (deixa de ser aspiracional).
3. **S61** alinhado 1:1 ao que o LangNet faz, com o **portão de rastreabilidade** explícito no passo 7.
4. **S63** ganha uma **nota de honestidade**: não há réplica completa do Co-Scientist no repositório hoje — confirmar artefato ou enquadrar como "direção que estamos construindo".
5. **S11 e S12** ganham nota de robustez (**fonte por linha + "última verificação"**) — **sem remover nenhum número**.
6. **S20 e S52** ganham um reforço **opcional** (marcado), sem mexer na estrutura nem no tempo.
7. **Direção visual de produção do PPTX:** clean/claro corporativo, uma cor de acento, mono para código; as marcações `Fala:`/`Layout:` vão para as **notas do apresentador**.

## Estrutura macro

| Bloco | Tema | Tempo | Acum. |
|---|---|---|---|
| 0 | Abertura e agenda | 3 | 3 |
| 1 | Linha do tempo: Perceptron → agentes | 3,5 | 6,5 |
| 2 | Modelos de linguagem: arquitetura e panorama | 14 | 20,5 |
| 3 | O que mudou para quem escreve software | 2 | 22,5 |
| 4 | Engenharia de contexto e RAG | 8 | 30,5 |
| 5 | Agentes: anatomia, ferramentas, padrões, falhas | 14 | 44,5 |
| 6 | Protocolos e formatos de interoperabilidade | 7,5 | 52 |
| — | **Intervalo** | 5 | 57 |
| 7 | Frameworks e SDKs agênticos | 12 | 69 |
| 8 | Ambientes agênticos | 4 | 73 |
| 9 | SDD e o argumento regulatório | 19 | 92 |
| 10 | Adaptação: fine-tuning, LoRA, RLHF | 7 | 99 |
| 11 | LangNet, demo, AI Co-Scientist, Redes de Petri | 15,5 | 114,5 |
| 12 | Fechamento e perguntas | 5,5 | 120 |

**Marcos de relógio:** min 20,5 (fim dos LLMs), min 52 (intervalo), min 73 (fim dos ambientes), min 92 (fim do SDD), min 99 (entrar nos seus sistemas).

---

# BLOCO 0 — Abertura (3 min)

### S1 — Capa (0,5 min)
- *Engenharia de IA e Desenvolvimento de Software Orientado a Especificação*. Subtítulo: *do modelo à spec: como times de software crítico incorporam IA sem perder auditabilidade*.
- Apresente-se em 20 segundos citando os 40 anos de engenharia e não volte ao assunto.

### S2 — Agenda (1,5 min)
- Os 12 blocos com tempo ao lado. Destaque nos três do núcleo: **LLMs**, **SDD**, **Sistemas**. Reaparece nas transições dos blocos 5, 9 e 11.

### S3 — A tese (1 min)
> **O gargalo deixou de ser escrever código. Passou a ser especificar e verificar.**
- Três consequências a provar: capacidade commoditizada e método não; agente sem gate degrada de forma previsível; spec executável é o que torna código de IA auditável.

---

# BLOCO 1 — Linha do tempo (3,5 min)

### S4 — Do Perceptron ao desenvolvimento agêntico (3 min)
**Layout: linha do tempo horizontal, duas raias paralelas, eixo de tempo compartilhado. Fundo escuro, 14–16pt.** Leitura guiada por você. `[v6: no PPTX final, versão clara/corporativa com acento forte; mantenho o alto contraste que este slide pede.]`

**RAIA SUPERIOR — arquiteturas (13 caixas):**

| # | Ano | Marco | Rótulo |
|---|---|---|---|
| 1 | 1958 | **Perceptron** (Rosenblatt) | neurônio único, separador linear |
| 2 | 1969 | **Inverno** (Minsky & Papert) | XOR não é linearmente separável |
| 3 | 1986 | **Backpropagation** (Rumelhart, Hinton, Williams) | MLP treinável, camadas ocultas |
| 4 | 1997 | **LSTM** (Hochreiter & Schmidhuber) | memória em sequência, gates |
| 5 | 1998 | **CNN / LeNet-5** (LeCun) | convolução, pesos compartilhados |
| 6 | 2012 | **AlexNet** | GPU + ImageNet |
| 7 | 2014-15 | **seq2seq + Atenção** (Sutskever; Bahdanau) | encoder-decoder, alinhamento suave |
| 8 | 2015 | **U-Net / ResNet** | segmentação médica; conexões residuais |
| 9 | **2017** | **TRANSFORMER** | atenção pura, paralelizável |
| 10 | 2018 | **BERT / GPT** | pré-treino + transferência |
| 11 | 2020 | **GPT-3 / leis de escala** | *in-context learning* |
| 12 | 2022 | **InstructGPT / RLHF → ChatGPT** | alinhamento a instruções |
| 13 | 2023-26 | **Tool use → raciocínio → agentes → protocolos** | o modelo age sobre o ambiente |

**RAIA INFERIOR — o que o desenvolvedor fazia:**

| Período | Unidade de trabalho |
|---|---|
| 1958–1998 | **Projetar features à mão** |
| 1998–2017 | **Treinar o próprio modelo** |
| 2018–2021 | **Fazer fine-tune** de um pré-treinado |
| 2021–2023 | **Chamar uma API** |
| 2023–2026 | **Orquestrar, especificar e verificar** |

- Seta grossa da caixa 9 à 11: *"a mesma arquitetura, só que maior"*.
- Seta de retorno de "fine-tune" para a raia superior: **"é aqui que se faz o transplante em cima do modelo pronto"** — gancho para o Bloco 10.
- Marca d'água: *2018 — NLP clínico com BERT*, *2021 — AlphaFold*.

**Fala (3 min):** 30s até 2012 ("a ideia é de 1958; o que mudou foi compute e dado"); 40s parando no Transformer; 40s até 2022 com o salto do in-context learning; **60s na raia inferior**, que é o argumento real; 20s na seta do transplante. **Faça este slide por último.**

### S5 — Onde a IA já está na área de vocês (0,5 min)
- **Antes:** escores de risco tabulares, preditivos de sepse, CNN em imagem, alertas por regra. **Agora:** extração estruturada de texto clínico livre, critérios de caso sobre evolução narrativa, agentes com ferramentas sobre bases hospitalares.
- **O que mudou foi o acesso ao texto livre do prontuário.**

---

# BLOCO 2 — Modelos de linguagem (14 min)

### S6 — Anatomia do Transformer (3 min)
- **Diagrama vertical detalhado**, de baixo para cima:
  `texto → tokenização → embeddings + codificação posicional (RoPE) → N × [ atenção multi-cabeça → residual + norm → feed-forward → residual + norm ] → projeção final → logits → softmax → amostragem`
- **Q, K, V** em 40 segundos com a analogia de recuperação: cada token emite uma *query*, todos oferecem *keys*, o produto interno decide de quem cada posição puxa *value*. Multi-cabeça = várias relações em paralelo.
- **O ponto de engenharia, em destaque:** a atenção é **O(n²)** no comprimento. Toda a economia de contexto longo, todo o custo de token e todo o problema de janela nascem dessa quadrática.
- Respostas do setor: **FlashAttention**, atenção esparsa (Longformer, BigBird), aproximações lineares. Prepara o S9 e o S13.
- **Fala:** único slide de arquitetura em que vale gastar 3 minutos. Tudo depois — agentes, protocolos, SDD — é engenharia em cima desta caixa.

### S7 — Por que o Transformer venceu (1 min)
- Contraste com a LSTM: recorrência é **sequencial no treino**, atenção é **paralelizável**. Não foi qualidade por token, foi throughput de treinamento.
- Decoder-only, autorregressivo, máscara causal. Objetivo único: **prever o próximo token**.
- **Fala:** "não existe módulo de raciocínio nem módulo de código. Existe previsão de próximo token e o que emergiu dela."

### S8 — Escala e o que emerge dela (1,5 min)
- Leis de escala. **In-context learning** como o salto de 2020: aprender na inferência sem tocar nos pesos — é o que torna prompt e RAG possíveis e o que tirou fine-tuning do caminho padrão.
- Deslocamento recente: de compute no treino para **compute na inferência**. Marque este ponto — ele volta idêntico no S62.

### S9 — MoE e arquiteturas esparsas (1,5 min)
- **Diagrama:** roteador escolhe k especialistas entre N. Parâmetros **totais** × **ativos por token**.
- Números reais: DeepSeek-V4-Pro 1,6T totais / 49B ativos; Kimi K3 2,8T / 104B; MiniMax M3 428B / 23B.
- **Consequência prática:** o que dita a sua conta de VRAM é o total, não o ativo — MoE gigante barateia inferência em nuvem e não ajuda quem hospeda em casa. E um modelo **denso** pequeno pode superar um MoE muito maior: a linha Qwen de 27B denso superou o MoE de 397B da própria Alibaba lançado dois meses antes, e a geração seguinte repetiu o feito contra proprietários de fronteira em código. **Densidade e tamanho pequeno voltaram a ser vantagem — para quem hospeda.**

### S10 — Inferência: os parâmetros que importam (1,5 min)
- Temperatura e top-p, KV cache, prefix caching, quantização, decodificação especulativa.
- Trecho: mesma chamada com `temperature=0` e `1.0` em geração de código.
- Regra prática: geração de código e extração estruturada pedem temperatura baixa; exploração de hipóteses pede o contrário. **Gancho para o S62** — o Co-Scientist depende disso.

### S11 — Panorama: modelos proprietários (1 min)
- Fronteira de meados de 2026 em **SWE-bench Verified**: GPT-5.6 Sol com 96,2% na medição independente da Vals AI, Claude Fable 5 com 95,0%, Gemini 3.1 Pro no agrupamento dos 80%.
- **Ressalva obrigatória:** número de fabricante e de harness independente divergem, às vezes muito. Cite sempre a fonte. *(Reconfira na semana da palestra.)*
- `[v6]` **Rodapé do slide, para trocar rápido:** `Fonte por número · fabricante ≠ harness independente · Última verificação: __/__/____`.

### S12 — Panorama: modelos abertos, e quais servem para código (2,5 min)
**O slide que essa plateia mais vai fotografar.**

| Modelo | Arquitetura | Contexto | Licença | Referência | Onde roda |
|---|---|---|---|---|---|
| **Kimi K3** (Moonshot) | 2,8T total / 104B ativos | 1M | pesos abertos (27/07/2026) | melhor aberto no índice agregado; 88,3 Terminal-Bench 2.1; 81,2 FrontierSWE; **1º na Frontend Code Arena, à frente do Fable 5** | infraestrutura séria |
| **DeepSeek-V4-Pro** | 1,6T / 49B ativos | 1M | **MIT** | 80,6% SWE-bench Verified — melhor entre pesos baixáveis | cluster |
| **DeepSeek-V4-Flash** | 284B / 13B ativos | 1M | **MIT** | mesma atenção esparsa, fração do custo | servidor médio |
| **GLM-5.2** | MoE | longo | **MIT** | melhor MIT em SWE-bench Pro (62,1%); forte em terminal e agêntico | servidor |
| **Qwen3.8-27B** (Alibaba, 14/08/2026) | **denso 27,78B**, multimodal (texto, imagem, vídeo), Gated DeltaNet + MTP | **262K nativo**, extensível a 1M via YaRN | **Apache-2.0** | **61,7 SWE-bench Pro · 73,0 Terminal-Bench 2.1 · 42,2 DeepSWE 1.1 · 90,3 LiveCodeBench v6 · 84,3 OSWorld-Verified** | **24GB de VRAM** |
| **Qwen3.6-27B** (predecessor) | denso 27B | longo | **Apache-2.0** | 77,2% SWE-bench Verified — referência histórica | uma GPU de consumo |
| **Muse Glimmer 30B** (Meta, 10/08/2026) | denso, multimodal | 131K | **Apache-2.0** | perde para o Qwen3.8-27B nos oito benchmarks em que se sobrepõem | 24GB quantizado |
| **MiniMax M3** | 428B / 23B ativos | 1M (atenção esparsa) | comunitária | agêntico barato, imagem e vídeo nativos | ⚠️ ver licença |
| **Devstral 2**, **MiMo-V2.5-Pro** | — | — | — | menções para código auto-hospedado | — |

- **Alerta de licença:** *pesos abertos* não é *código aberto*. MIT e Apache-2.0 são livres; a licença comunitária do MiniMax é **não comercial por padrão**. Em empresa que vende software, decisão jurídica, não técnica.
- **A linha que importa, e o slide dentro do slide:** o **Qwen3.8-27B**, de 14 de agosto de 2026, é hoje o candidato mais convincente a melhor denso multimodal localmente implantável na faixa dos 30B. Contra o Qwen3.6-27B, o salto é de dois dígitos nas tarefas agênticas: Terminal-Bench 2.1 de 63,4 para 73,0, DeepSWE 1.1 de 13,3 para 42,2, OSWorld-Verified de 63,9 para 84,3 — **sem aumentar o tamanho do decodificador**. Meta lançou o Muse Glimmer 30B em 10 de agosto como melhor aberto de 30B; quatro dias depois o Qwen3.8-27B o superou em todos os benchmarks de sobreposição direta.
- **O número que cala a plateia:** em SWE-bench Pro o Qwen3.8-27B (61,7) supera o Claude Opus 4.6 Max (53,4). Ele ainda perde em Terminal-Bench 2.1 (73,0 × 78,2), GPQA Diamond, Humanity's Last Exam e NL2Repo-Bench. **A fronteira não caiu; ficou irregular.** Diga com essas palavras.
- Sinais independentes nas duas primeiras semanas: 1º entre abertos no benchmark de agente jurídico da Harvey, 9º geral no Code Arena WebDev, 1º entre abertos no Image-to-WebDev da Arena.ai. AMD entregou suporte no dia do lançamento, com 24 a 52 tokens/s em hardware de estação.
- **Ressalva metodológica:** esses números são do cartão do modelo, da Alibaba, não de réplica independente. Pesos abertos significam que qualquer um pode rodar de novo — **é argumento a favor do aberto, não contra.**
- Aviso de memória: **os pesos são o piso, não o total.** O KV cache vem por cima e escala com contexto e concorrência; um 27B servindo contexto longo a vários usuários pode dobrar a pegada.
- `[v6]` **Rodapé do slide, para atualizar sem retrabalho:** `Números do cartão do modelo salvo indicação · Fonte por linha · Última verificação: __/__/____`. *(É o slide que mais envelhece; deixei-o estruturado para troca rápida — sem tirar nenhum número seu.)*
- `[v6]` **Nota de ritmo (opcional):** se o ensaio cronometrado estourar aqui, considere desdobrar em dois slides (tabela | o caso Qwen3.8) mantendo TODO o conteúdo. Só se precisar — a estrutura padrão continua sendo um slide.

### S13 — Contexto longo: o número anunciado é o menos útil (2 min)
- Treze ou mais modelos com 1M+; Llama 4 Scout e Gemini 3 Pro anunciam 10M **sem benchmark publicado que sustente qualidade perto disso**.
- **Context rot:** capacidade efetiva em torno de **60–70% do anunciado**, e a queda não é gradual — segura até um limiar e despenca. Janela de 1M pode degradar já em 50K.
- O resultado contraintuitivo: nos testes da Chroma os modelos foram **melhor com texto embaralhado do que coerente**, porque texto coerente cria viés de recência e o modelo sobrepesa o final e negligencia o começo.
- Custo: encher 1M vai de ~US$ 0,14 no DeepSeek V4 Flash a US$ 10,00 no Claude Fable 5 — spread de 71×.
- **Frase de fecho do bloco:** *contexto menor e curado supera contexto grande e velho.* Agravante em domínio regulado: quando a janela estoura e o modelo trunca em silêncio, **não fica registro do que foi perdido**.

---

# BLOCO 3 — O que mudou para quem escreve software (2 min)

### S14 — A escada de abstração (1 min)
- assembly → alto nível → framework → **spec + verificação**. Cada degrau teve a mesma objeção e se consolidou com a verificação correspondente (compilador, type checker, teste).

### S15 — O que a IA faz bem e mal em código, e quanto custa (1 min)
- **Bem:** código de fronteira bem especificado, tradução entre representações, testes a partir de critérios explícitos, refatoração mecânica. **Mal:** decisão arquitetural com trade-off implícito, corretude dependente de contexto não escrito, invariantes não declarados.
- Rodapé: 50 mil a 500 mil tokens por tarefa agêntica; PT-BR gasta ~1,5× mais tokens.
- **Fala:** "a coluna da direita é toda ela *falta de especificação*."

---

# BLOCO 4 — Engenharia de contexto e RAG (8 min)

### S16 — De prompt para contexto (0,5 min)
- O trabalho é **decidir o que ocupa a janela**, com o S13 fresco. Barra: instruções | ferramentas | histórico | documentos | saída.

### S17 — RAG: o diagrama (2,5 min)
- **Dois trilhos.** *Ingestão:* documento → chunking → embedding → índice vetorial + léxico. *Consulta:* pergunta → reescrita → busca híbrida (BM25 + densa) → reranking → montagem → geração com citação.
- Vermelho nos três pontos de quebra: **chunking**, **recuperação**, **ausência de reranking**.
- **Fala:** "RAG raramente falha na geração. Falha na recuperação, e o time passa semanas ajustando prompt."

### S18 — Por que chunking ingênuo destrói um critério de IRAS (1,5 min)
- Critério de definição de caso (ICSAC) cujo enunciado ocupa três parágrafos: critério clínico, critério laboratorial, janela temporal.
- Em chunks de 512 tokens, o laboratorial se separa da janela; a recuperação devolve metade da regra e o modelo completa o resto sozinho: **falso positivo de notificação**.
- Solução: chunking semântico pela unidade lógica, metadados por tipo de infecção, expansão de janela.

### S19 — Saída estruturada como contrato (2 min)
- Extração de critérios de IRAS de texto livre. Mostre o **schema**: por critério, `atendido: bool`, `evidencia_textual: str`, `data_referencia: date`, `confianca: float`.
- **Todo booleano vem com o trecho literal que o justifica.** Sem isso não há revisão humana viável nem trilha de auditoria.
- **Fala:** "não peçam parecer. Peçam formulário preenchido com evidência citada."

### S20 — Avaliação e guardrails (1,5 min)
- Acurácia agregada é inútil: falso negativo e falso positivo têm custos assimétricos e diferentes por tipo de infecção.
- **Sensibilidade e especificidade estratificadas**, conjunto dourado revisado por infectologista, versionado, em CI a cada mudança de prompt, **modelo** ou base. Trecho de eval com asserção.
- Guardrails: menor privilégio, anonimização antes de chamada externa, injeção vinda do próprio prontuário, LGPD.
- **Fala:** "trocar versão de modelo sem esse conjunto rodando é mudança não controlada em software de saúde."
- `[v6]` **Reforço opcional (sem alterar o tempo):** se sobrar respiro, ponha na tela uma mini-matriz de eval — *estratificação por tipo de infecção · conjunto dourado versionado · gatilho de CI a cada mudança de prompt/modelo/base · asserção sobre o dourado*. É o slide que a recomendação final (S65) manda construir primeiro; vale ancorá-lo visualmente.

---

# BLOCO 5 — Agentes (14 min)

*(Reexiba o S2 com o Bloco 5 destacado.)*

### S21 — Definição operacional (1,5 min)
- **Um agente é um LLM em laço, com ferramentas, sobre um ambiente, com critério de parada.**
- O que não é agente: fluxo de caminho fixo com LLM nos nós — isso é workflow, e quase sempre é a escolha certa.
- Eixo de autonomia: determinístico → roteamento por LLM → agente com ferramentas → autônomo. **Autonomia é custo e risco, não virtude.**

### S22 — O laço agêntico (2 min)
- **Diagrama circular:** objetivo → raciocínio → ação → observação → repete → parada → resposta.
- Três pontos de controle: **quais ferramentas existem**, **o que volta como observação**, **quando o laço para**.

### S23 — Tool use sem framework nenhum (3 min)
- Declaração em JSON Schema — `consultar_resultado_microbiologia(paciente_id, janela_dias)`; resposta com `tool_use`; execução local, `tool_result`, `while` explícito.
- **"O laço agêntico tem trinta linhas. Tudo que vem depois é conveniência."**
- A descrição da ferramenta **é prompt**. Descrição ruim de ferramenta causa mais falha do que prompt de sistema ruim.

### S24 — Componentes (0,5 min)
- Memória curta × longa, planejamento, reflexão, ferramentas. **Memória longa em arquivo versionado costuma superar vetorial** em regras estáveis — auditável e diffável. Gancho para o S31.

### S25 — Os seis padrões de composição (3 min)
- **Grade 3×2:** prompt chaining, routing, parallelization (seccionamento e votação), orchestrator-workers, evaluator-optimizer, agente autônomo.
- "Comecem pelo mais simples que resolve." Marque votação e evaluator-optimizer como os mais subutilizados e os mais úteis para reduzir falso positivo aqui.

### S26 — O mesmo caso resolvido de três formas (2 min)
- **Agente de vigilância de IRAS** — varre microbiologia, prescrição e evolução; aplica critérios; propõe notificação; **para em revisão humana**.
- Workflow encadeado | orchestrator-workers (um worker por tipo, contexto isolado) | evaluator-optimizer (crítico contesta contra o critério normativo, menos falso positivo, dobro de tokens).

### S27 — Multiagente: quando compensa (0,5 min)
- Só com subtarefas paralelizáveis **e** contextos isolados. Em fluxo linear, 4 a 15× mais tokens para reimplementar um `if`. Passagem de contexto é lossy.

### S28 — Por que agentes falham em produção (1,5 min)
- **Erro composto:** 95% por passo, 20 passos → ~36% fim a fim. Curva com três linhas (90%, 95%, 99%).
- Laço infinito, ferramenta alucinada, contexto contaminado, custo imprevisto, **falha silenciosa**.
- **Confiabilidade não vem de prompt melhor, vem de reduzir o número de passos não verificados.**

---

# BLOCO 6 — Protocolos e formatos (7,5 min)

### S29 — O mapa: vertical × horizontal (2 min)
- **Diagrama em cruz**, agente no centro.
- **MCP** (Anthropic, nov/2024; Linux Foundation em dez/2025): vertical. Host → Client → Server com **Tools**, **Resources**, **Prompts**, sobre JSON-RPC. Limite: hub-and-spoke — **dois servidores MCP não conversam entre si**, sem delegação nem negociação.
- **A2A** (Google, abr/2025; Linux Foundation em jun/2025; v1.0 em abr/2026): horizontal. **AgentCard** em `/.well-known/agent-card.json` com skills, MIME types, transportes e segurança. JSON-RPC 2.0, **Task em oito estados** (submitted, working, input_required, auth_required, completed, failed, canceled, rejected), SSE e webhooks. Mais de 150 organizações; integrado em AWS, Microsoft e Google Cloud.
- **A analogia:** MCP é o *USB-C* das ferramentas; A2A é o *HTTP* da colaboração entre agentes. Em produção usam-se os dois.

### S30 — A2Family e alternativas (1,5 min)
- Extensões oficiais do A2A: Secure Passport, Timestamp, Traceability, Agent Gateway Protocol.
- **A2Family:** **AP2** (pagamentos iniciados por agente, 60+ organizações financeiras), **UCP** (comércio, compatível com AP2, com evidência criptográfica de consentimento), **A2UI**.
- **Alternativas:** **ACP** (IBM — REST, MIME multipart, herança FIPA-ACL, performativas typed: propose, accept, reject, counter) e **ANP** (identidade descentralizada).
- **A crítica que valoriza o slide:** trabalho recente mostra que **nenhum desses protocolos expressa governança**. Registram quem chamou quem, não sob qual política nem com que base legal. Em software de saúde essa é exatamente a camada que sobra para vocês. Gancho para o S51 e o S65.

### S31 — OKF: Open Knowledge Format (2 min) — SLIDE DEDICADO
- **Abertura da distinção:** protocolos definem **comunicação entre sistemas**; o OKF define **conhecimento**. É baseado em arquivo, legível por humano e versionado junto com o código.
- **Origem:** Google Cloud, 12 de junho de 2026, v0.1, especificação de 451 linhas.
- **Problema que ataca:** conhecimento organizacional espalhado por catálogos de metadados, wikis, comentários de código e cabeça de engenheiro. Cada desenvolvedor de agente resolve isso do zero, e sempre de um jeito diferente.
- **A especificação inteira em cinco regras — ponha as cinco na tela:**
  1. Um **bundle é um diretório de arquivos markdown**. Nada de banco, nada de servidor.
  2. **Cada arquivo é um conceito**, e **o caminho do arquivo é o identificador**.
  3. Cada arquivo abre com **frontmatter YAML** cujo **único campo obrigatório é `type`**.
  4. Arquivos se referenciam por **links markdown comuns** — o que faz do diretório um **grafo**, não uma lista.
  5. Dois nomes reservados: **`index.md`** (listagem do bundle) e **`log.md`** (histórico de mudanças).
- **Produtor e consumidor desacoplados:** um bundle escrito por humano é consumido por agente, e o contrário também. Independente de nuvem, banco e framework.
- **Implementações de referência publicadas junto:** um agente que varre datasets do BigQuery e gera um documento OKF por tabela; um visualizador HTML estático; bundles de exemplo; ingestão no Knowledge Catalog.
- **A aplicação direta para eles, e vale dizer com essas palavras:** um bundle OKF com as **definições de caso de IRAS**, as **fórmulas dos indicadores** (densidade de incidência, taxa de utilização de dispositivo) e os **runbooks da CCIH** é exatamente o conhecimento que hoje vive em PDF, em planilha e na cabeça das pessoas. Em OKF ele fica legível por agente, revisável por infectologista, com `log.md` de histórico e `git blame` de autoria — que é a metade do que uma auditoria pede.
- **Ressalva obrigatória:** v0.1. Padroniza o **contêiner**, não a **semântica**. Não existe ainda vocabulário de `type` para domínio clínico — se vocês adotarem, vocês definem. Apresente como direção do setor, não como aposta técnica. *(Confirme o estado da spec na semana da palestra.)*

### S32 — Os outros formatos em markdown (1 min)
- **AGENTS.md** (Agentic AI Foundation / Linux Foundation): contexto de projeto para agentes de código — comandos de build e teste, convenções, decisões arquiteturais. Markdown puro, sem schema.
- **DESIGN.md** (Google Labs): identidade visual — tokens de design em YAML mais racional em prosa.
- **Agent Skills:** capacidade empacotada como pasta com um arquivo markdown, com registries públicos.
- **O padrão por trás dos três:** o setor convergiu, sem combinar, para **markdown versionado no repositório** como formato de contexto para agente. Não foi por elegância — foi porque é a única coisa que humano e máquina leem, que o git versiona e que o revisor consegue auditar num diff.

### S33 — A ponte para o SDD (1 min)
- **Spec do SDD, AGENTS.md e bundle OKF são a mesma ideia**, em escopos diferentes: conhecimento formalizado em markdown versionado, consumido por agente e revisável por humano. A spec descreve o que o sistema deve fazer; o AGENTS.md descreve como se trabalha no repositório; o OKF descreve o domínio.
- Guardem essa frase para o S49: **os três convivem no mesmo repositório, e é isso que constrói a rastreabilidade.**

---

## INTERVALO — 5 min

---

# BLOCO 7 — Frameworks e SDKs (12 min)

### S34 — Critério de leitura (0,5 min)
- Uma pergunta aplicada a todos: **o que este framework controla por mim — o laço, o estado, ou nenhum dos dois?**
- Aviso: o mesmo agente do S26 aparece nos cinco, para comparar custo de abstração e não sintaxe.

### S35 — OpenAI Agents SDK (2 min)
- `Agent`, `handoffs`, `guardrails`, `sessions`, tracing embutido.
- Trecho de 10 linhas: triagem → especialista por tipo de infecção, via handoff.
- **Modelo de controle:** o SDK controla o laço; o estado vive na sessão. Tracing de primeira linha, acoplado ao provedor.

### S36 — Anthropic Claude Agent SDK (2 min)
- O laço do Claude Code exposto como biblioteca: busca agêntica no sistema de arquivos sem indexação prévia, subagentes com contexto isolado, hooks, sistema de permissões, MCP nativo, modo headless.
- Trecho: execução headless sobre repositório com hook de permissão.
- **Diferencial:** projetado em torno de **código e arquivos**, não de conversa. O mais relevante para o Bloco 9.

### S37 — LangChain e LangGraph (2 min)
- LangChain é abstração de componentes; **LangGraph é máquina de estados**.
- **Diagrama:** nós, arestas condicionais, `checkpointer` persistente, `interrupt` para aprovação humana.
- Trecho: `StateGraph` com nó condicional e interrupção antes da notificação.
- **Durabilidade e human-in-the-loop nativos são o argumento decisivo aqui** — notificação de IRAS não sai sem aprovação, e o processo precisa sobreviver a reinício.

### S38 — CrewAI (2 min)
- **Modelo mental:** organização, não grafo. `Agent` com **role**, **goal** e **backstory**; `Task` com descrição e saída esperada; `Crew` reunindo os dois; `Process` sequencial ou hierárquico (com um agente gerente delegando); e **Flows** quando você precisa de controle determinístico em volta da crew.
- Trecho: crew de dois agentes para o caso do S26 — um agente coletor de evidência, um agente avaliador de critério, com `expected_output` explícito em cada Task.
- **Onde brilha:** protótipo e demonstração. A curva de entrada é a mais baixa do grupo, e a decomposição por papel força o time a escrever o que cada agente deve fazer — o que, sem querer, é meio caminho para uma spec.
- **Onde dói, e diga isso:** a metáfora de papéis **esconde o laço**. Quando falha, você depura uma abstração, não uma sequência de chamadas. `backstory` é prompt disfarçado de narrativa, e times acabam ajustando personalidade quando o problema era o schema da ferramenta. Estado e durabilidade são fracos comparados ao LangGraph.
- **Veredito para eles:** ótimo para levantar um piloto em uma tarde e mostrar à direção. Pense duas vezes antes de colocar em produção regulada.
- `[v6]` **Nota honesta (é o framework do LangNet):** o S59 usa CrewAI. Vale dizer em uma frase que o que aprendemos apanhando dele — o laço escondido, o gate que não vem de graça — é justamente o que o Bloco 11 mostra resolvido com portão determinístico.

### S39 — AutoGen / AG2 (2 min)
- **Modelo mental:** conversa entre agentes. `ConversableAgent` como unidade base, `GroupChat` com um **gerente de conversa** que escolhe quem fala em seguida, `UserProxyAgent` como ponto de entrada humano e **executor de código** embutido — o agente escreve, executa e vê o resultado.
- **Human-in-the-loop nativo e granular:** o modo de intervenção é configurável por agente (sempre, nunca, só ao terminar), o que é raro nos outros frameworks e diretamente aplicável ao gate de notificação de vocês.
- Trecho: group chat de três participantes com o proxy humano e a política de intervenção explícita.
- **Onde brilha:** exploração, pesquisa, tarefas em que o caminho não é conhecido de antemão. É o framework mais próximo do que o AI Co-Scientist faz — **guardem isso para o S62**.
- **Onde dói:** comportamento emergente. A conversa pode divergir, repetir ou consumir tokens sem convergir; restringir isso exige trabalho que o framework não faz por você. Nota histórica útil: o projeto se dividiu entre a linha da Microsoft e o fork comunitário **AG2**, então documentação e exemplos de terceiros muitas vezes se referem a versões incompatíveis — verifique a linhagem antes de copiar código.
- **Veredito:** o mais interessante intelectualmente, o mais arriscado em produção.

### S40 — Tabela comparativa e a opinião contrária (1,5 min)
- Linhas: OpenAI SDK, Claude Agent SDK, LangGraph, **CrewAI**, **AutoGen/AG2**, laço próprio. Colunas: modelo de controle | estado e durabilidade | human-in-the-loop | observabilidade | acoplamento | suporte a MCP/A2A | caso de uso ideal. Leia em voz alta só a última coluna.
- **A opinião contrária:** para talvez 70% dos casos o laço direto é mais simples de depurar. Framework se justifica por durabilidade, observabilidade e human-in-the-loop — não por elegância. "Não adotem framework antes de ter o eval do S20."

---

# BLOCO 8 — Ambientes agênticos (4 min)

### S41 — Mudança de unidade de trabalho (1 min)
- Do autocomplete de linha para a tarefa sobre o repositório. A revisão passa a ser de diff inteiro — isso muda o code review do time.

### S42 — Claude Code (2 min)
- CLI, busca agêntica sem indexação, `CLAUDE.md`, subagentes, hooks, skills, MCP, headless para CI. Diagrama terminal ↔ repositório ↔ testes ↔ hooks.
- **Hooks são o mecanismo de gate:** lint, teste e política rodam *dentro* do laço.

### S43 — Cursor e o panorama (1 min)
- **Cursor:** IDE, indexação prévia, Composer/Agent, regras de projeto. Indexação prévia (rápida, risco de índice defasado) × exploração sob demanda (lenta, sempre atual).
- Uma linha: Copilot, Windsurf, Aider, Codex, Devin. **Primeiro slide a cortar.**

---

# BLOCO 9 — SDD (19 min) — núcleo

*(Reexiba o S2 com o Bloco 9 destacado.)*

### S44 — O problema (1,5 min)
- *Vibe coding* funciona no protótipo e colapsa no sistema. Sintoma: o código existe, funciona, e ninguém sabe qual requisito ele atende nem se ainda atende. Em domínio regulado isso tem outro nome: **não conformidade**.

### S45 — A inversão (2 min)
- **Dois fluxos.** *(a)* requisito informal → código → doc desatualizada. *(b)* **spec primária** → plano → tarefas → código **derivado**.
- **A spec é o que se versiona, revisa e mantém; o código é o que se regenera.**
- **Fala:** "é a relação entre código-fonte e binário. Ninguém revisa o binário."

### S46 — O ciclo SDD (2,5 min)
- **Diagrama central:** `Intenção → Especificação → Plano → Tarefas → Implementação → Verificação`, com **gate entre cada par** e retorno em falha. Gates rotulados: aprovação humana, teste automatizado, verificação de política, verificação formal.
- **Conecte ao S28:** cada gate corta a cadeia não verificada. É assim que se derruba a curva do erro composto.

### S47 — Anatomia de uma spec útil (2 min)
- Contexto e escopo | **não-objetivos** | requisitos EARS | critérios de aceitação verificáveis | contratos | invariantes | referências normativas.
- EARS na tela: *"Quando um resultado de hemocultura positiva for registrado, o sistema deve avaliar os critérios de ICSAC dentro da janela de 48 horas e produzir um parecer com evidência citada."* Contraste com *"o sistema deve detectar infecções corretamente."*

### S48 — Exemplo ponta a ponta (3 min)
- **Três painéis:** trecho da spec com critério e janela | teste gerado do critério, com bordas da janela | implementação gerada.
- Rastreabilidade: **R-014 → `test_r014_janela_48h` → `avaliar_icsac()`**.
- **Fala:** "o teste nasceu do critério, não do código. Por isso não herda os bugs da implementação."

### S49 — Ferramental (2 min)
- **GitHub Spec Kit** (`/specify`, `/plan`, `/tasks`, `/implement`), **Kiro** (`requirements.md`, `design.md`, `tasks.md`), **Tessl**. Árvore com `specs/` ao lado de `src/`.
- **Feche a promessa do S33:** `specs/`, `AGENTS.md` e o bundle OKF no mesmo repositório — o que o sistema deve fazer, como se trabalha nele, e o domínio que ele modela. Tudo markdown versionado.

### S50 — Onde SDD encontra agentes (2,5 min)
- **Diagrama:** especificador → arquiteto → implementador → verificador, com **gate entre cada um**, contexto isolado, e **gate em código determinístico, não em outro LLM**.
- **Feche o S28:** o monolítico de 20 passos tem 36% de sucesso; a cadeia de 4 agentes com gate determinístico se comporta de forma inteiramente diferente, porque o erro não se propaga.
- `[v6]` **Antecipe o Bloco 11 numa frase:** "vou mostrar isto rodando — um gerador cujo portão determinístico pega o bug do agente antes do deploy." (É o S60.)

### S51 — SDD produz o artefato regulatório de graça (3 min)
- **O slide de maior valor comercial.** Software para saúde exige rastreabilidade requisito → projeto → teste → código, gestão de risco documentada e ciclo de vida controlado: **IEC 62304**, **ISO 14971**, e a regulamentação da ANVISA para software como dispositivo médico. *(Verifique a numeração da RDC vigente.)*
- Quem faz SDD **já tem** a matriz de rastreabilidade como subproduto, versionada, com autoria e histórico.
- **Inversão da objeção:** eles pensam "IA generativa em software regulado é risco". A resposta é que o SDD é o que torna código gerado por IA auditável. **O que não é auditável é código escrito à mão sem especificação.**
- Complemente com o S30 e o S13: os protocolos não expressam governança e a janela que estoura trunca em silêncio sem deixar registro. Política de autorização e controle de contexto são responsabilidade da sua arquitetura.
- **Pausa depois dessa frase. É o pico da palestra.**

### S52 — Antipadrões (0,5 min)
- Spec inflada, spec envelhecida, critério não executável, gate humano virado carimbo, e **spec gerada por IA e aprovada sem leitura** — a pior, porque produz aparência de rastreabilidade sem substância. **Segundo slide a cortar.**
- `[v6]` **Se NÃO cortar (recomendo manter, é onde o sênior te testa):** dê a cada antipadrão o antídoto de uma linha — spec inflada → só entra o que tem critério de aceitação; envelhecida → CI que falha quando código diverge da spec; critério não executável → EARS + limite numérico; carimbo → revisor assina o diff, não o PDF; aprovada sem leitura → se ninguém leu, não há SDD, há teatro.

---

# BLOCO 10 — Adaptação (7 min)

### S53 — A escada de adaptação (1,5 min)
- **Degraus:** prompt → few-shot → RAG → SFT/LoRA → RL → pré-treino contínuo. **Só suba quando o anterior falhar com evidência medida** — e a evidência é o eval do S20.
- Retome a seta do S4: "o transplante em cima do modelo pronto que eu prometi no começo."

### S54 — SFT e os dados (1 min)
- Trecho JSONL com `messages`. **500 a 5.000 exemplos bem curados superam 100 mil sujos.** O custo real de um dataset clínico é tempo de infectologista, não GPU.

### S55 — LoRA e QLoRA (2,5 min)
- **Diagrama:** `W` congelado + `ΔW = B·A`, posto `r` ≪ `d`. Explique `r`, `alpha`, `target_modules`, e o porquê de treinar 0,1–1% dos parâmetros.
  ```
  LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
             target_modules=["q_proj","k_proj","v_proj","o_proj"],
             task_type="CAUSAL_LM")
  ```
- QLoRA: base em 4 bits (NF4) + adaptadores em precisão maior. Tabela de VRAM por tamanho.
- Vantagem operacional: adaptadores são arquivos de dezenas de MB, **versionáveis e trocáveis em runtime**. Um adaptador por especialidade, mesma base — e a base pode ser o Qwen3.8-27B do S12.

### S56 — RLHF e sucessores (1 min)
- **Diagrama:** comparações humanas → reward model → PPO. Depois: **DPO** (sem reward model), **GRPO** (raciocínio), **RLAIF / Constitutional AI**.
- Por que importa sem treinar: **explica o comportamento do modelo que vocês consomem** — bajulação, recusa e excesso de hedging são artefatos do alinhamento, não do pré-treino.

### S57 — Quando NÃO treinar, e o modelo local (1 min)
- Não treine com conhecimento volátil (protocolo muda → RAG), tarefa que muda toda semana, ausência de eval. Custos ocultos: esquecimento catastrófico e **manutenção perpétua do modelo derivado**.
- Local, retomando o S12: quantização (GGUF, AWQ), runtimes (LM Studio, vLLM, Ollama). Três argumentos: **o dado do paciente não sai da rede**, custo marginal previsível, independência de provedor.

---

# BLOCO 11 — Os sistemas (15,5 min)

*(Reexiba o S2 com o Bloco 11 destacado.)*

### S58 — Ponte com o domínio deles (1 min)
- O Co-Scientist da Google foi validado em laboratório em três cenários biomédicos, um deles **descoberta de mecanismo de resistência antimicrobiana**. *(Verifique e cite só o que confirmar.)*
- `[v6 — confirmado na fonte primária, Nature 2026]` O cenário de RAM é sobre **cf-PICIs** (ilhas cromossômicas induzíveis por fago, formadoras de capsídeo) — elementos móveis que carregam **genes de virulência e de resistência a antibióticos** entre espécies, **incluindo *E. coli* e *K. pneumoniae***. Com informação de fundo mínima, o Co-Scientist propôs de forma independente a hipótese **top-ranqueada** de que os cf-PICIs **interagem com caudas de fagos diversos para expandir o espectro de hospedeiros**, **recapitulando um achado experimental ainda não publicado** dos pesquisadores (uma década de bancada). Os outros dois cenários: **repurposing para LMA** e **alvos epigenéticos para fibrose hepática**.
- **Fala:** "o segundo sistema que vou mostrar foi validado, na origem, exatamente no tipo de problema que vocês enfrentam. Chego nele. Antes, o de engenharia." `[v6:` reforço opcional — "ele chegou sozinho ao mesmo mecanismo de disseminação de resistência entre *E. coli* e *Klebsiella* que um laboratório levou dez anos para provar."`]`

### S59 — LangNet: arquitetura (3 min)
- **Diagrama:** intenção → especificação → plano → geração de código → verificação, com o LLM local no centro.
- Stack real: **Qwen2.5-Coder-32B via LM Studio, contexto de 64k**, com avaliação em curso do **Qwen3.8-27B** como substituto — motivada por visão, tool use e reasoning em modelo menor, sob o critério de não perder capacidade de geração de código.
- **Amarre com o S12:** o modelo que você está avaliando saiu há duas semanas e é hoje o melhor denso multimodal que roda em 24GB. O argumento inteiro do LangNet só existe porque essa faixa chegou a esse patamar em 2026.
- Se a avaliação já tiver resultado parcial, diga qual: o critério era não perder geração de código, e o Qwen3.8 sobe justamente em benchmark agêntico. **Isso é evidência de método, não de sorte.**
- `[v6:` confere com o repositório — CrewAI como framework, 64k de contexto, avaliação do Qwen3.8-27B em curso.`]`

### S60 — LangNet: evidência (1,5 min)
- Um exemplo real de spec → código gerado. **Um número medido**: tempo de ciclo, taxa de aprovação no gate, tokens por tarefa, ou percentual concluído sem intervenção.
- **Este número separa a apresentação de um pitch. Se não tiver, meça antes.**
- `[v6 — já temos números reais medidos na validação do LangNet, use estes:]`
  - **Cobertura de rastreabilidade: 100%** — todos os requisitos funcionais atravessam Spec → Modelo de Dados → Implementação, medido por **portão determinístico** (não por confiança no LLM).
  - **Suíte de tarefas geradas: 100% executando ponta a ponta** contra banco real — núcleo determinístico + tarefas com agente (relatório, extração de documento).
  - **~10 defeitos do gerador capturados pelo portão *antes* do deploy** (variável indefinida, coluna inexistente, join espacial faltante), cada um com o salto exato onde quebrava.
  - **Frase:** "o número não é a taxa de acerto do LLM — é a taxa em que o **gate pega o erro do LLM antes de virar produção**. É o S50 acontecendo." *(Meça de novo no exemplo clínico do vídeo, para o número casar com o domínio da plateia.)*

### S61 — DEMO GRAVADA: da especificação à aplicação completa (3 min)
- **Vídeo de até 3 minutos, gravado, sem áudio, legendas grandes.**
- **Roteiro:** (1) você escreve uma spec curta, 15–20 linhas — **deixe-a na tela tempo de ser lida**; (2) geração do plano e das tarefas; (3) geração da aplicação completa: modelo de dados, lógica, API e **interface**; (4) execução da suíte derivada dos critérios; (5) **uma falha de teste e a correção — não corte**; (6) aplicação rodando com a interface; (7) volta à spec, com a rastreabilidade visível.
- **Acelere os trechos de espera (2× a 4×) com o tempo real na legenda.**
- **30 segundos seus ao fim:** tempo real, tokens, e o que você corrigiu à mão.
- `[v6:` este roteiro mapeia 1:1 no que o LangNet faz de fato — o passo (7) "rastreabilidade visível" é literalmente o portão do S60 ficando verde. Você vai me passar como o vídeo será feito; eu entrego o storyboard tomada-a-tomada e a spec-de-tela para exibir.`]`

### S62 — Como funciona o AI Co-Scientist (2,5 min) — SLIDE NOVO

**Contexto em uma linha:** sistema multiagente da Google DeepMind sobre Gemini, apresentado em fevereiro de 2025 e publicado na **Nature em 2026** (Gottweis et al.), com liberação experimental a pesquisadores via Gemini for Science. Não é uma ferramenta de *deep research*: o objetivo declarado é **produzir hipóteses novas e verificáveis**, com protocolo experimental, a partir de um objetivo de pesquisa escrito em linguagem natural. `[v6:` base **Gemini 2.0**; arXiv **2502.18864**; usa ferramentas — busca web, ChEMBL, UniProt, AlphaFold — para ancorar as hipóteses; toda hipótese é filtrada por quatro critérios: **alinhamento, plausibilidade, novidade e testabilidade**.`]`

**Diagrama principal do slide — três fases, seis agentes especializados e um supervisor:**

| Fase | Agente | O que faz |
|---|---|---|
| **Gerar** | **Generation** | propõe áreas de foco e hipóteses iniciais, ancoradas em literatura e bases estruturadas, via **debate científico em self-play** |
| | **Proximity** | mapeia e agrupa as hipóteses em **grafo de proximidade**, deduplica e impede que o sistema colapse numa única linha de pensamento |
| **Debater** | **Reflection** | atua como **revisor por pares virtual**: critica correção, qualidade, novidade e segurança |
| | **Ranking** | conduz o **torneio de ideias**: comparações par a par com **debates científicos simulados**, pontuadas em **Elo** |
| **Evoluir** | **Evolution** | refina, recombina e amplia as hipóteses mais bem colocadas |
| | **Meta-review** | sintetiza os padrões de todas as revisões e debates e escreve a **visão geral de pesquisa** final |
| **Acima de tudo** | **Supervisor** | decompõe o objetivo em plano, aloca recursos, gerencia a **fila de trabalhadores** e escreve estatísticas na memória de contexto |

**Os quatro mecanismos que fazem o sistema funcionar — e que valem mais que a lista de agentes:**

1. **Torneio Elo.** Hipóteses entram com rating inicial e disputam par a par. O vencedor ganha pontos, o perdedor perde, e **quando uma hipótese mal colocada vence uma bem colocada, a variação é maior**. Com o tempo o rating separa o que merece refinamento do que não merece. O Elo não é enfeite: é a função de aptidão do sistema inteiro. `[v6:` rating inicial de **1200**; as **top-ranqueadas** disputam em **debate de múltiplos turnos** (mais criterioso, reduz viés de ordem), as **fracas** em **turno único**.`]`
2. **Emparelhamento informado pela proximidade.** O grafo do agente Proximity decide **quais duelos vale a pena marcar** — pares próximos são agendados com mais frequência, porque comparar duas hipóteses parecidas discrimina mais do que comparar duas distantes.
3. **A evolução não muta, ela cria.** O agente Evolution **gera novas hipóteses em vez de alterar as existentes**, justamente para não destruir entradas que já foram testadas no torneio. As estratégias incluem combinar, simplificar, aumentar viabilidade e sair da caixa. Este é um detalhe de engenharia excelente para mostrar a dev sênior.
4. **Meta-revisão como aprendizado sem gradiente.** O agente Meta-review extrai padrões recorrentes das críticas e **os acrescenta aos prompts das rodadas seguintes** — `[v6:` concretamente, realimenta o **agente Reflection** para revisões futuras mais completas`]`. O sistema melhora sem nenhum ajuste de peso — **é aprendizado sem backpropagation**, feito em contexto. Diga isso com essas palavras; é o insight que a plateia leva para casa.

**A validação do próprio Elo:** os autores verificaram se o rating auto-atribuído mede qualidade de verdade, comparando-o com acerto no conjunto diamond do GPQA. **Elo mais alto correlaciona com maior probabilidade de resposta correta.** É a resposta à objeção óbvia — "o sistema se avalia sozinho, e daí?". `[v6:` o número concreto — a **AUC no GPQA subiu de 0,643 para 0,651** na corrida com **Gemini 2.0 Flash**; e as avaliações automáticas mostram **benefício contínuo de mais test-time compute**.`]`

**Amarre com três pontos anteriores da palestra, e este é o valor do slide:**
- **S8** — é test-time compute puro: mais compute na inferência produz hipóteses melhores. O supervisor existe para escalar compute contra o objetivo.
- **S25** — reconheçam os padrões: **evaluator-optimizer** (Generation × Reflection), **parallelization por votação** (o torneio), **orchestrator-workers** (o Supervisor e a fila).
- **S39** — é o parente próximo do que o AutoGen faz com debate entre agentes, só que com uma função de aptidão explícita em vez de conversa livre. **A diferença entre os dois é exatamente o Elo.**

### S63 — AI Co-Scientist: a sua replicação (2 min)
- **Diagrama do seu torneio:** geração → crítica → pareamento → ranqueamento → evolução das melhores → nova rodada.
- Três partes: **o que você manteve** do paper, **o que você mudou**, **por quê**. O "por quê" é o que demonstra engenharia e não reprodução.
- Pontos onde uma replicação séria necessariamente diverge, e vale nomear os seus: o paper roda sobre agendamento interno do Google e é **exclusivamente Gemini**; qualquer replicação precisa de fila durável própria, camada de LLM agnóstica de provedor e índice vetorial para a proximidade. Se você resolveu isso, é engenharia sua, não do paper.
- Se houver, um resultado ou caso exercitado.
- `[v6 — CONFIRMADO NO REPOSITÓRIO: a réplica existe e roda.]` **QuanticaResearch AI Co-Scientist** (`github.com/pasteurjr/aicoscientist`) — plataforma full-stack: **React 19 → FastAPI → MariaDB**, motor multiagente sobre **LangGraph** (fork estendido do `open-coscientist-agents`), progresso ao vivo via **SSE** e UI que visualiza o torneio e o grafo de proximidade.
  - **O que você MANTEVE do paper (fielmente):** os **seis agentes + Supervisor** implementados em LangGraph; **torneio Elo com rating inicial 1200 e K=32**, **debate par a par multi-turno** (`max_turns=10`) para as top-ranqueadas e **turno único** para as fracas, **pareamento guiado pelo grafo de proximidade**; e a **meta-revisão realimentando os prompts dos outros agentes** ("feedback appended to the prompts of the others") — o aprendizado sem gradiente do S62, no seu código.
  - **O que você MUDOU, e por quê (é aqui que está a engenharia):**
    1. **LLM agnóstico de provedor** — pools "Smarter/Cheaper" com **o3, Gemini 2.5, Claude Sonnet 4, DeepSeek e locais (Ollama `qwen3:32b`, LM Studio)**, com fallback de embeddings (OpenAI → HuggingFace `all-MiniLM-L6-v2` local). *O paper é só Gemini; o seu roda inclusive **local** — casa com a tese do S57/S59.*
    2. **Fila e estado próprios** — `RunManager` (FastAPI) com fila durável e `projects.status` recuperável em MariaDB + checkpoints pickle, **no lugar do agendamento interno do Google**.
    3. **Proximidade** — grafo semântico com **NetworkX + Louvain** sobre embeddings (não um vetor-DB formal; diga isso — é honesto e suficiente para o porte).
    4. **Além do paper:** ~30 agentes especialistas seus (crítico, advogado, evidência, lacuna, analista de plano, escrita científica, acompanhamento de projeto).
  - **Resultado exercitado (cite este número):** o run **UC-10** rodou **ponta a ponta** — revisão de literatura + **4 hipóteses** + verificação profunda + **1º torneio Elo** + **1ª meta-revisão** — em **~2,8 h com DeepSeek** (`runtime/validation_run.txt`). **Honestidade:** o motor roda fim-a-fim; a sincronização backend↔banco ainda tem um bug conhecido (alfa). Apresente como **réplica funcional pronta para piloto**, não produção.
  - **Ponte com a plateia (opcional, forte):** o sistema aceita **qualquer objetivo em linguagem natural** — os 3 projetos semeados são biologia estrutural/AlphaFold3, fármaco KRAS G12C e meta-pesquisa, mas dá para apontá-lo a um objetivo de **resistência antimicrobiana** (o caso cf-PICI do S58) e mostrar o torneio de hipóteses rodando no domínio deles.
  - `[v6:` **AÇÃO:** para o slide, capture uma tela real da aba **Tournament** (rankings Elo + transcrição de debate) e do **Proximity Graph** do run UC-10 — vale mais que qualquer diagrama.`]`

### S64 — A camada que amarra tudo: validação por Redes de Petri (2 min)
- **Diagrama da rede:** lugares, transições, marcações, invariantes garantidos.
- VisualTasksExec: sincronização entre agentes com propriedades verificáveis — ausência de deadlock, alcançabilidade, invariantes de estado.
- **Feche o arco inteiro:** o S28 mostrou que agentes degradam de forma previsível; o S50 mostrou que gates cortam a cadeia; o S30 mostrou que **nenhum protocolo do mercado expressa governança**; o S62 mostrou um sistema que se auto-avalia por Elo — **mas Elo mede qualidade de hipótese, não corretude de execução**. Este slide mostra que a estrutura da orquestração pode ser **verificada formalmente**, não apenas testada ou pontuada.
- Deixe o argumento técnico falar. Não transforme em pitch.
- `[v6:` o editor de Redes de Petri já está no repositório (`petri-net-editor`); **confirme o caminho/estado do VisualTasksExec** antes da palestra.`]`

---

# BLOCO 12 — Fechamento (5,5 min)

### S65 — As três conclusões (1,5 min)
- Retome o S3. Recomendação acionável: **construam primeiro o conjunto de eval do S20.** Antes de framework, antes de agente, antes de trocar de modelo.

### S66 — Referências e contato (0,5 min)
- QR do repositório, papers (Co-Scientist na Nature), specs (MCP, A2A, OKF, Spec Kit), tabela de modelos do S12 com links, seu contato.
- `[v6:` referência do Co-Scientist para o QR — Gottweis et al., *Accelerating scientific discovery with Co-Scientist*, Nature 2026 (`s41586-026-10644-y`) / arXiv 2502.18864.`]`

### S67 — Perguntas (3,5 min)

---

## Anexo A — Perguntas prováveis e resposta curta

| Pergunta | Linha de resposta |
|---|---|
| "Qual modelo aberto usar para código?" | S12. Uma GPU de 24GB: **Qwen3.8-27B**, Apache-2.0, denso, multimodal, 262K — supera o Muse Glimmer 30B em toda a sobreposição e bate o Opus 4.6 Max em SWE-bench Pro. Infra séria e MIT: DeepSeek-V4-Pro ou GLM-5.2. Licença antes do benchmark. |
| "CrewAI ou LangGraph?" | S38 e S37. CrewAI para levantar piloto rápido; LangGraph quando precisar de durabilidade, retomada e aprovação humana estruturada. Em produção regulada, LangGraph. |
| "Contexto de 1M resolve nosso problema de prontuário?" | S13. Não. Efetivo é 60–70% do anunciado, a queda é abrupta e pode começar em 50K. Recuperação curada vence janela grande. |
| "Como validamos software não determinístico?" | Não se valida a saída, valida-se o gate. (S50) |
| "Dado de paciente vai para a nuvem?" | S57. Modelo local, anonimização, ou instância com retenção zero. |
| "Adotamos MCP, A2A, ou esperamos?" | MCP já é seguro para ferramentas internas. A2A quando houver fronteira organizacional. OKF é v0.1 — direção, não aposta. |
| "Isso não substitui desenvolvedor?" | S14. Substituiu escrever a linha, não decidir qual sistema construir e provar que está correto. |
| "Já tentamos e alucinou." | S19 e S20. Faltava saída estruturada com evidência citada e conjunto de eval. |

## Anexo B — Checklist de produção

1. **Gravar a demo do S61** — maior prazo, comece por ela.
2. **Medir o número do S60.** `[v6:` já temos os números da validação do LangNet — remeça no exemplo clínico do vídeo.`]`
3. **Reconferir as tabelas de modelos (S11 e S12) na semana da palestra.** Mudam mensalmente; dado errado na frente de dev sênior custa caro. `[v6:` rodapé de "fonte por linha + data de verificação" já está nos dois slides — só atualizar.`]`
4. Blocos 2, 9 e 11 — o núcleo.
5. Exemplos de código do domínio de IRAS (S19, S23, S48) — precisam ser realistas.
6. **Dez diagramas, mesmo estilo:** S4 (linha do tempo), S6 (Transformer), S9 (MoE), S17 (RAG), S22 (laço), S25 (padrões), S29 (protocolos), S37 (grafo LangGraph), S46 (ciclo SDD), S62 (fases e torneio do Co-Scientist).
7. Verificar: RDC da ANVISA (S51), estado da spec do OKF (S31). `[v6:` casos do Co-Scientist (S58/S62) **CONFIRMADOS** na fonte — Nature 2026 / arXiv 2502.18864. **Réplica do S63 CONFIRMADA e roda** (QuanticaResearch, `github.com/pasteurjr/aicoscientist`): capturar telas reais das abas Tournament + Proximity Graph do run UC-10. Só **caminho/estado do VisualTasksExec (S64)** ainda a confirmar.`]`
8. **S4 por último.**
9. Ensaio cronometrado separado dos Blocos 2, 5, 7 e 11.

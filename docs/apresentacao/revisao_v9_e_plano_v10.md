# Revisão da apresentação V9 e o que mudou na V10

**Data:** 28 de setembro de 2026
**Arquivos revisados:** `apresentacao_iasdd_v9_biobyte.pptx` (102 lâminas) e `roteiro_narrado_iasdd_v9_biobyte.md`
**Arquivos novos:** `apresentacao_iasdd_v10_biobyte.pptx` (92 lâminas) e `roteiro_narrado_iasdd_v10_biobyte.md`

> A V9 **não foi tocada**. A V10 são arquivos novos, com gerador próprio.

---

## 1. O que eu medi na V9

| O que foi medido | V9 | Teto / alvo | Situação |
|---|---|---|---|
| Palavras de narração das lâminas | 9.270 | — | — |
| **Tempo falado das lâminas** | **62 a 71 min** | **60 min** | **estourava** |
| Tempo declarado nas lâminas | 58,2 min | — | subestimado em ~10 min |
| Lâminas acima de 110 palavras | 13 | 0 | carregadas |
| Lâmina mais pesada | 242 palavras (IA na saúde 1/3) | ~95 | muito carregada |
| Trechos com instrução de palco no lugar de fala | 34 de 102 | 0 | não dá para ler em voz alta |

O cabeçalho do roteiro anunciava "58 minutos de lâminas". A contagem real do texto a ser falado dá
**62 a 71 minutos**, dependendo do ritmo. Com os 60 minutos de vídeo, a apresentação chegava a
**126 minutos**, acima dos 118 previstos — e acima da hora que você pediu para a parte falada.

---

## 2. Defeitos encontrados na V9

### Graves

**1. Lâminas duplicadas dentro do Bloco 8.**
As lâminas 64–67 (Onde o agente trabalha / Claude Code / Codex / Cursor) e as 68–70
(Mudou a unidade de trabalho / Claude Code / Cursor e o panorama) são duas versões do mesmo
bloco, uma do deck antigo e outra da reorganização, ambas presentes. O chapéu denuncia:
`AMBIENTES DE GERAÇÃO DE CÓDIGO` nas primeiras, `AMBIENTES` nas segundas.

**2. Anúncio de demonstração duplicado.**
A lâmina 94 diz "DEMONSTRACAO BIOBYTE — 20 minutos" e a 100 é o vídeo final de 20 minutos.
O mesmo vídeo é anunciado duas vezes, com seis lâminas de intervalo.

**3. O fechamento acontece antes do vídeo final.**
Ordem na V9: lâmina 98 "As três conclusões" → 99 "Referências e contato" → **100 vídeo de 20 min**
→ 101 "BLOCO 12 — Fechamento" → 102 "Perguntas". Você conclui, exibe vinte minutos de vídeo,
e conclui de novo.

**4. Referências penduradas a uma numeração que não existe mais.**
As lâminas 85 e 97 mandam "feche o S28", "o S50", "o S30", "o S62". Esses números são de um
deck anterior. Lidos em voz alta, não significam nada para a plateia.

**5. Acentuação comida em duas lâminas.**
Lâmina 93: "evidencia", "Execucao", "classificacao", "notificacoes", "sao", "a 13a".
Lâmina 94: "DEMONSTRACAO", "rastreaveis", "atribuicao", "sequencia", "codigo".

**6. O roteiro não é narração, é instrução de palco.**
Em 34 das 102 lâminas o texto sob "Texto para a narradora ler" diz o que fazer, não o que falar:
*"Apresente-se em cerca de 20 segundos"*, *"Mostre os doze blocos com o tempo ao lado, mas não
leia todos — aponte para…"*, *"Não desenvolva agora"*. Isso não pode ir para um narrador.

### Estruturais

**7. Deep Learning existe, mas com uma lâmina só.**
O Bloco 3 tem a divisória (lâmina 20) e **uma** lâmina de conteúdo (21, Transfer Learning),
seguida de um vídeo de 8 minutos. A estrutura aprovada pede redes neurais profundas, treinamento,
reutilização de modelos pré-treinados e adaptação para imagens — quatro assuntos numa lâmina.
Pior: redes neurais são explicadas antes, na lâmina 13, dentro do bloco de Machine Learning,
e dividindo lâmina com o K-Means.

**8. Adaptação de modelo partida em dois blocos distantes.**
"Como adaptar um modelo ao negócio" está na lâmina 33 (Bloco 4), e "A escada da adaptação",
"SFT e os dados" e "LoRA e QLoRA" estão nas lâminas 88–90, dentro do **Bloco 10, que é SDD**.
É exatamente o "não misturar os assuntos" que o briefing pede.

**9. Os algoritmos não diziam para que servem.**
As lâminas 8–13 tinham "Como funciona" e "Onde é útil", mas sem a ideia central em uma frase,
e a 13 juntava Redes Neurais com K-Means — dois algoritmos de naturezas opostas na mesma lâmina.

**10. O pipeline de Machine Learning passava em duas lâminas.**
Lâminas 6 e 7 resumiam as seis etapas. Não havia passagem etapa a etapa.

**11. O bloco do LangNet não mostrava as etapas do LangNet.**
O Bloco 11 tinha: conceito (92), tabela de evidências (93), anúncio de demo (94), AI Co-Scientist
(95–96) e Redes de Petri (97). Em nenhum momento ele percorria Requisitos → Especificação →
Modelo de Dados → Interface → Ferramentas → Agentes e Tarefas → Petri → Testes → Código →
Aplicação, que é o que o vídeo final mostra durante vinte minutos.

### Corretos, conferidos

- **"Attention Is All You Need"** está bem contextualizado: título, Vaswani et al., Google Brain e
  University of Toronto, 2017, com o antes (RNN/LSTM), a contribuição e o impacto. Mantido na V10.
- **Q, K e V** aparecem explicados, com a observação da atenção quadrática. Mantido.
- **Claude Code, Codex e Cursor vêm antes** de protocolos, SDD e LangNet. Ordem correta.
- **Os comandos são reais e atuais** (`claude -c`, `claude -r`, `claude -p`, `claude mcp`,
  `codex exec --json`, `--output-schema`). Conferidos e mantidos.
- **IA na saúde está presente** e tecnicamente correta nas três frentes. Só estava carregada demais.

---

## 3. O que a V10 faz

| Item | V9 | V10 |
|---|---|---|
| Lâminas | 102 | 92 |
| Palavras de narração | 9.270 | 7.989 |
| **Tempo falado das lâminas** | **62–71 min** | **59 min** |
| Total com os vídeos | ~126 min | **119 min** |
| Lâmina mais pesada (corpo) | 242 palavras | ~123 palavras |
| Corpo médio por lâmina | ~110 palavras | ~78 palavras |
| Roteiro | instrução de palco em 34 lâminas | fala literal em 100% |

### Mudanças de conteúdo

**Algoritmos — uma lâmina cada, no formato que você pediu.**
Sete lâminas, cada uma com quatro campos: **Ideia central** (uma frase), **Como funciona**,
**Para que se presta** e **Onde é mais adequado**. São: K Vizinhos Mais Próximos, Regressão Linear,
Regressão Logística, Árvore de Decisão, Random Forest, Máquina de Vetores de Suporte e K-Means.
O conteúdo saiu de `deck/algoritmos inteligentes3.pptx` (lâminas 44–67 e 153–154), resumido.
Redes Neurais saiu daqui e foi para o bloco de Deep Learning, que é o lugar dela.

**Pipeline de Machine Learning — etapa a etapa, rápido.**
Cinco lâminas com uma trilha no alto mostrando em que etapa você está: o mapa das seis etapas,
Visualizar e Preparar, Conjuntos e Modelo, Treinar e Avaliar (com o sobreajuste), e Como se mede
um classificador. Mais uma de ferramental. Conteúdo das lâminas 29–42 da fonte.

**Deep Learning com conteúdo de verdade.**
Quatro lâminas: do neurônio artificial à rede de camadas (com o ou-exclusivo), retropropagação,
redes convolucionais, e Transfer Learning com código. Conteúdo das lâminas 68–151 da fonte.

**Bloco do LangNet aderente ao pipeline real.**
Oito lâminas percorrendo as etapas na ordem em que elas aparecem na interface, com a mesma trilha
visual: a fábrica e a máquina · o ritual que se repete em toda etapa (origem e versão → gerar →
refinar conversando → aprovar) · Documento e Requisitos (procedência e natureza) · Especificação
funcional (fluxos de exceção e croqui) · Modelo de Dados (a etapa aponta o próprio defeito, e a
correção é dita em português) · Interface e Protótipo · Ferramentas, Agentes e Tarefas (MCP e
rastreabilidade) · Rede de Petri · Casos de Teste e Geração de Código · Aplicação e bancada.
Os conceitos são os mesmos do roteiro da demonstração final de 20 minutos.

**Adaptação de modelo reunida num lugar só** (Bloco 4), com LoRA e QLoRA absorvidos na escada.

**Fechamento depois do vídeo final**, como manda a ordem.

### Lâminas removidas, e por quê

| Removida | Motivo |
|---|---|
| Claude Code / Cursor (duplicatas do Bloco 8) | repetiam as lâminas 65 e 67 |
| DEMONSTRACAO BIOBYTE — 20 minutos | duplicava o vídeo final |
| As cinco opções (frameworks) | a tabela comparativa já percorre os cinco |
| Ajuste fino: SFT e os dados | absorvido na escada da adaptação |
| A família A2A | a crítica que importava migrou para o mapa MCP × A2A |
| AI Co-Scientist (2 lâminas) | fora da estrutura aprovada; não é BioByte nem LangNet |
| O que fica com vocês | absorvido nas três conclusões |

Se você quiser o AI Co-Scientist de volta, ele custa ~2 minutos e cabe — diga que eu reponho.

---

## 4. Plano de gravação dos seis vídeos

Os cinco primeiros têm 8 minutos; o último, 20. Total de 60 minutos.

### Vídeo 1 — O pipeline de Machine Learning (8 min) · depois da lâmina 21

**Material:** `jupyter/exalgint3.ipynb` e `jupyter/pipeline_ml_video_v2/`.

| Tempo | O que capturar |
|---|---|
| 0:00–1:00 | Carregar a base clínica; `df.head()`, `df.describe()` e o mapa de correlação |
| 1:00–2:30 | Preparar: valores ausentes, colunas descartadas, `StandardScaler` — mostrar antes e depois da escala |
| 2:30–3:30 | `train_test_split`, e por que a separação importa (mostrar o resultado inflado quando se treina no teste) |
| 3:30–5:00 | `GridSearchCV` comparando os sete algoritmos das lâminas — a tabela de resultados |
| 5:00–6:30 | Treinar o melhor e ler o gráfico de perda por época; apontar o ponto de sobreajuste |
| 6:30–8:00 | Matriz de confusão, sensibilidade, especificidade e curva ROC |

### Vídeo 2 — Classificação e apoio à decisão em saúde (8 min) · depois da lâmina 26

| Tempo | O que capturar |
|---|---|
| 0:00–1:00 | A base e o desfecho a prever; a prevalência da classe positiva |
| 1:00–2:00 | Por que a acurácia mente: o modelo que responde sempre "não" e acerta 98% |
| 2:00–4:00 | Regressão logística; o coeficiente virando razão de chances, lido na tela |
| 4:00–5:30 | Árvore de decisão; imprimir a regra e ler em voz alta |
| 5:30–7:00 | Curva de Kaplan-Meier e o efeito de um fator no tempo |
| 7:00–8:00 | O que o modelo não decide: o ponto em que a conduta volta para o clínico |

### Vídeo 3 — Treinamento e Transfer Learning (8 min) · depois da lâmina 32

| Tempo | O que capturar |
|---|---|
| 0:00–1:00 | A base de imagens e as classes |
| 1:00–2:30 | Treinar do zero com poucas imagens: a curva que não sobe |
| 2:30–4:00 | Carregar a rede pré-treinada, congelar os pesos, trocar a camada final |
| 4:00–6:00 | Treinar de novo: a curva agora, e quantas imagens bastaram |
| 6:00–7:00 | Descongelar as camadas finais e fazer o ajuste fino |
| 7:00–8:00 | Mapa de saliência sobre a imagem: onde a rede olhou |

### Vídeo 4 — Tokens, atenção e geração (8 min) · depois da lâmina 44

| Tempo | O que capturar |
|---|---|
| 0:00–1:30 | O tokenizador quebrando uma frase clínica; contar os tokens de "hemocultura" |
| 1:30–3:30 | Mapa de atenção: a que cada token está olhando |
| 3:30–5:00 | A distribuição do próximo token, antes do sorteio |
| 5:00–6:30 | O mesmo pedido com temperatura 0 e temperatura 1 |
| 6:30–7:15 | A janela de contexto enchendo, e o que acontece quando estoura |
| 7:15–8:00 | Uma invenção confiante, flagrada e explicada |

### Vídeo 5 — Sistema multiagente com resultado verificável (8 min) · depois da lâmina 52

**Material:** o servidor MCP do BioByte (`consultar_microbiologia`, `escore_risco_cox`) e a bancada.

| Tempo | O que capturar |
|---|---|
| 0:00–1:00 | O objetivo e as ferramentas declaradas |
| 1:00–3:00 | O agente pedindo a ferramenta e o programa executando — os dois lados na tela |
| 3:00–4:30 | O resultado real voltando para o contexto |
| 4:30–6:00 | Dois agentes com contextos isolados, e a agregação |
| 6:00–7:00 | Injetar uma falha de propósito |
| 7:00–8:00 | O portão em código pegando a falha antes de ela seguir adiante |

### Vídeo 6 — O pipeline completo do LangNet (20 min) · depois da lâmina 89

**Material:** `docs/apresentacao/demo-biobyte-v5/` — o roteiro de 40 cenas e as 79 capturas já
existentes servem de base direta. O mapeamento é este:

| Tempo | Etapa | Cenas do roteiro v5 |
|---|---|---|
| 0:00–1:30 | A fábrica e as etapas na coluna | 1–2 |
| 1:30–4:00 | Documento e Requisitos: procedência e natureza | 3–7 |
| 4:00–6:00 | Especificação: caso de uso, exceções, croqui | 8–10 |
| 6:00–8:30 | Modelo de Dados: o defeito apontado e a correção por conversa | 11–14 |
| 8:30–10:00 | Interface e Protótipo | 15–17 |
| 10:00–12:00 | Ferramentas, Agentes e Tarefas, com a rastreabilidade | 18–21 |
| 12:00–13:30 | Sequência e Rede de Petri | 22–23 |
| 13:30–15:00 | Casos de Teste e Geração de Código | 24–26 |
| 15:00–17:30 | A aplicação: cadastros, relatórios, registros dos agentes | 27–34 |
| 17:30–19:30 | A bancada: entradas, etiquetas, saída | 35–38 |
| 19:30–20:00 | Falha que não passa calada, e a correção por conversa | 39–40 |

**Se precisar encurtar para 15 minutos:** cortar as cenas 15–17 (protótipo) e 29 (relatórios),
e reduzir a aplicação de 2:30 para 1:30. O argumento não perde nada.

---

## 5. Pendências que dependem de você

1. **Data de verificação dos panoramas de modelos** (lâminas 39 e 40). Estão com os números atuais,
   mas a tabela envelhece em semanas. Diga a data e eu fecho.
2. **O vídeo final: 20 ou 15 minutos.** Está em 20. O corte para 15 está descrito acima.
3. **AI Co-Scientist:** removido. Digo de novo porque foi uma escolha minha, não uma regra do
   briefing — reponho em duas lâminas se você quiser.

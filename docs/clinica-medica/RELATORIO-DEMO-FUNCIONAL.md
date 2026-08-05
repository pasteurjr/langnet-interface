# Demonstração Funcional — ClinIA (Clínica Médica Inteligente)

**Data:** 2026-08-05 · **Executor:** Claude (autônomo, via Playwright + WebSocket)
**App rodando:** frontend `:3002` · ws-server `:5003` · backend Petri `:8001` · banco `clinia_ops`
**Modelo dos agentes:** qwen2.5-coder-32b (LM Studio local) · **nunca DeepSeek cloud**

> Objetivo: **provar a aplicação funcionando** — cadastros, triagem agêntica que **classifica o
> problema do paciente e roteia para o especialista**, e uma **consulta com cada agente especialista**
> (várias interações). Ao final, os **erros encontrados a corrigir**.

---

## 1. Cadastros (dados reais no banco)

As telas de cadastro funcionam com dados reais do `clinia_ops`. **Gestão de Pacientes** mostra a
tabela (ID, Nome, CPF, Nascimento, Contato) com busca e ações **Ver / Editar / Excluir**, e
**Cadastro de Pacientes** o formulário (Nome, CPF, Data de Nascimento, Contato, Convênio, Salvar).

![Gestão de Pacientes — CRUD com dados reais](D2)

## 2. Triagem agêntica AO VIVO (na tela) — classifica e roteia

Na tela **Triagem Agentiva**, preenchi a queixa e os sinais vitais da paciente **Maria Silva** e
cliquei **"Executar com IA"**. O agente `triagem_hub_agent` respondeu **no painel Resultado**, lendo
os dados reais informados:

> `classificacao_urgencia: "vermelho"` · justificativa: *"…dor forte no peito e falta de ar… sinais
> vitais (PA 150/95 mmHg e FC 118 bpm)… possível angina ou infarto agudo do miocárdio…"* ·
> `area_destino: "Cardiologia"`

![Triagem Agentiva — resultado do agente na UI](D6)

## 3. Roteamento + consulta com cada especialista (3 pacientes, cadeia completa)

Rodei a **cadeia agêntica completa** para 3 pacientes de perfis diferentes. Cada um passou por
**Triagem → Pré-atendimento com o especialista roteado → Encaminhamento → Prontuário** (4 interações).
Os agentes **classificaram e produziram pré-diagnósticos diferenciados e medicamente plausíveis**:

| Paciente | Queixa | Triagem (urgência → área) | Pré-diagnóstico do especialista |
|---|---|---|---|
| **Maria Silva** | Dor no peito, falta de ar, sudorese | 🔴 **vermelho → Cardiologia** | **Infarto Agudo do Miocárdio (0.85)**, Angina Instável (0.15); confiança **alta**; exames: **ECG, troponina sérica**, angiografia |
| **Pedro Santos (6a)** | Febre 39°C, tosse, dor de garganta (3 dias) | 🟡 **amarelo → Pediatria** | **Gripe (Influenza)**, Faringite viral, Infecção respiratória aguda; confiança média; exames: teste rápido de influenza, hemograma, RX tórax |
| **Ana Costa** | Dor abdominal à direita, náuseas, vômitos (6h) | 🔴 **vermelho → Emergência** | **Apendicite**, colite ulcerativa, gastroenterite; exames de imagem/laboratório abdominais |

**Prova das interações reais** (extraído das transcrições `demo-transcripts.json`):
- **Triagem**: cada paciente recebeu classificação de urgência **coerente com a queixa** (o cardíaco e
  o abdominal agudo → vermelho; o quadro respiratório infantil → amarelo) e uma **área de destino**.
- **Especialista**: cada agente especialista (`pre_atendimento_cardiologia` / `_pediatria` /
  `_gastroenterologia`) devolveu **hipóteses diagnósticas, nível de confiança e exames sugeridos**
  específicos da área — **diferentes entre si** (cardíaco ≠ pediátrico ≠ gastro), o que prova que os
  agentes leem o caso real e não respondem genérico.

## 4. 🐞 Bug crítico encontrado E CORRIGIDO durante a demonstração

**Sintoma:** ao rodar a triagem, **todos os pacientes** retornavam o **mesmo** quadro cardíaco
(alucinação), ignorando a queixa real.
**Causa:** as descrições das tasks geradas descrevem o *schema de input em prosa* ("Input Schema:
paciente_id, queixa_inicial, sinais_vitais…"), **sem placeholders `{campo}`** — então o ws-server
formatava a descrição mas **não injetava os dados do paciente** no prompt; o agente respondia sem o caso.
**Correção:** o ws-server agora **anexa os DADOS DE ENTRADA reais** ao final da descrição do agente.
Aplicado no **gerador** (`_template_websocket_server_py`) — commit `FIX: ws-server injeta input_data…`.
**Efeito comprovado:** após o fix, o caso pediátrico passou a classificar **amarelo/respiratório**
(antes: cardíaco), e cada especialista passou a dar um pré-diagnóstico do caso real.

---

## 5. ❌ Erros encontrados a corrigir (próximos passos)

1. **Persistência do Encaminhamento falha** — `criar_encaminhamento` retorna
   `Column 'atendimento_id' cannot be null`. O fluxo **não cria um registro de `atendimento`** antes do
   encaminhamento (o encaminhamento depende de um atendimento existente). Falta a etapa "abrir
   atendimento" (persistir triagem → atendimento) que gere o `atendimento_id`.
2. **Persistência do Prontuário falha** — `registrar_prontuario` retorna
   `Column 'paciente_id' cannot be null`. As telas/tasks passam **nome** do paciente, mas o adapter
   determinístico exige o **`paciente_id` (FK)**. Falta resolver nome → id (ou a UI enviar o id).
3. **`area_destino` é texto livre** — a triagem devolveu "Cardiologia", "Pediatra Infectologista",
   "Emergência" (variações). Para rotear automaticamente ao agente especialista certo, a triagem
   deveria escolher de uma **lista fechada** de especialidades cadastradas.
4. **Uma tela só de Pré-atendimento (fixa em Cardiologia)** — a UI tem uma única
   "Pré-atendimento por Especialista" ligada a `pre_atendimento_cardiologia`; não roteia
   dinamicamente para pediatria/gastro conforme a triagem. Idealmente a tela recebe a área da triagem.
5. **Contenção sob concorrência** — o modelo local processa **uma execução por vez**; requisições
   agênticas simultâneas **serializam** e podem estourar o timeout de 120s do cliente. Aceitável em
   uso sequencial; para concorrência real, precisaria de fila/instâncias.

## 6. Conclusão

A **ClinIA está funcionando**: cadastros com dados reais, e — após o fix de injeção de input — a
**triagem agêntica classifica a urgência e roteia por especialidade**, com cada **agente especialista
produzindo um pré-diagnóstico diferenciado e plausível** (cardiologia → IAM/troponina; pediatria →
gripe/faringite; gastro → apendicite). O núcleo agêntico (triagem + especialistas) está **provado**.
Faltam corrigir as **etapas de persistência** (encaminhamento/prontuário exigem FKs que o fluxo não
gera) e **fechar o roteamento** (área da triagem → tela/agente do especialista) — os erros listados na
seção 5, que atacaremos em seguida.

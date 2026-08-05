# Validação das Correções F5–F7 — ClinIA regenerada (com prova)

**Data:** 2026-08-05 · **Método:** corrigir o gerador → regenerar SÓ o Código (v3) → rodar a app →
provar. Cada fix com commit+push "ANTES de…".

> As 3 falhas residuais foram corrigidas no gerador e **provadas na app v3 rodando**, sem patches.

## F6 — Import inválido `crewai_tools.base_tool` ✅

- **Problema:** o LLM às vezes gera `from crewai_tools.base_tool import BaseTool` (submódulo
  inexistente) → `ModuleNotFoundError` no ws-server (na v2 precisei corrigir à mão).
- **Correção:** `_fix_common_tool_imports` agora também troca a variante submódulo por
  `from crewai.tools import BaseTool`.
- **Prova (v3):** nenhum `crewai_tools.base_tool` no código gerado; o **ws-server subiu direto, sem
  correção manual**.

## F5 — Fiação de task da tela agêntica ✅

- **Problema:** a Triagem disparava `cadastrar_paciente`. O alvo inventado pelo ui_spec
  (`classificar_urgencia_paciente`) não casava com o tasks.yaml (`triagem_agentiva`), e o matcher caía
  em `cadastrar_paciente` (via o token "paciente").
- **Correção:** `_resolve_task_target` agora considera **também o NOME da tela** ("Triagem Agentiva"
  → casa exatamente com `triagem_agentiva`) e escolhe o melhor casamento.
- **Prova (v3):** a tela **Triagem Agentiva** mostra **"Dispara o agente `triagem_agentiva`"**
  (era `cadastrar_paciente`).

![Triagem — dispara triagem_agentiva (F5) no formato Entrada→Ação→Resultado (F1)](W1)

## F7 — Tela/rota CRUD duplicada ("Pre Diagnosticos") ✅

- **Problema:** "Gestão de Pré-Diagnósticos" vinha mal-rotulada (entity=`atendimentos`), deixando
  `pre_diagnosticos` descoberto → o auto-CRUD por entidade gerava uma **terceira tela** "Pre
  Diagnosticos".
- **Correção:** a inferência de entidade ficou **acento-normalizada** e passou a **corrigir** a
  entidade quando a do ui_spec não aparece no nome mas outra tabela aparece → "Gestão de
  Pré-Diagnósticos" vira `pre_diagnosticos`; todas as 9 entidades cobertas; sem auto-CRUD.
- **Prova (v3):** o menu tem só **2 itens** de pré-diagnóstico — "Geração de Pré-Diagnóstico"
  (agêntica) e "Gestão de Pré-Diagnósticos" (CRUD). A duplicata sumiu.

## Conclusão

**As 7 falhas priorizadas (F1–F7) foram corrigidas no gerador do LangNet e comprovadas na ClinIA
regenerada e rodando**, sem patches manuais. A app v3 sobe com os 3 serviços (backend :8001,
ws-server :5003, frontend :3002), telas de cadastro com dados reais, telas agênticas no formato
Entrada→Ação→Resultado disparando a **task correta**, e a Rede de Petri visualizável com os 12
agentes da triagem.

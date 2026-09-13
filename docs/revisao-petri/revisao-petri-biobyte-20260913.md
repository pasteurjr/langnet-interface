# Revisão crítica da Rede de Petri — BioByte Sentinela

Pedida pela interface do LangNet (etapa Rede de Petri, botão Revisar), julgada pelo DeepSeek.
Data: 13/09/2026. Rede: 17 posições, 21 transições, 44 arcos.

A revisão só ficou possível depois de a rede passar a **declarar os dados**: o que cada tarefa
entrega e de onde vem cada entrada. Antes disso o revisor só podia dizer que faltava informação.

---

## Achados

### Nomes
- **[GRAVE]** `T_authenticate_user_mfa` e `T_execute_surveillance_cycle` — têm `task_id` válido, mas estão sem arcos de entrada/saída. Logo, `authenticate_user_mfa` e `execute_surveillance_cycle` existem no `tasks.yaml`, mas não são executadas na rede. **O que fazer:** conectar essas transições ao fluxo.
- **[LEVE]** `T_start`, `T_join_cycle`, `T_fim_cycle`, `T_fim_audit`, `T_fim_dashboard`, `T_fim_report` — não correspondem a tarefas do `tasks.yaml`; são transições de controle. **O que fazer:** documentar como infraestrutura ou validar se o gerador as aceita.

### Dono
- Nenhuma divergência de dono encontrada nas transições de tarefa. Todos os `agente_id` batem com o `tasks.yaml`.

### Fluxo de dados
- **[GRAVE]** `P_auth`/`authenticate_user_mfa` — entradas `nome`, `data_nascimento`, `sexo`, `prontuario`, `id_medico_responsavel`, `idade`, `tempo_cateter_dias`, `apache_ii`, `sitio_insercao`, `comorbidades` estão como externas, mas não são dados de autenticação; `output_data` está vazio. **O que fazer:** auth deve ler apenas `email`, `senha`, `totp_code` e produzir `id_usuario`/sessão; mover dados clínicos para `register_patient_case`.
- **[GRAVE]** `id_usuario` — aparece como entrada externa em `import_microbiology`, `classify_case_nhsn`, `detect_mdr`, `fetch_external_cox_score`, `calculate_cox_score`, `recommend_treatment_bundle`, `estimate_risk_reduction`, `register_audit_log`, `view_surveillance_dashboard`, `export_surveillance_report`, `execute_surveillance_cycle`. Ninguém produz. **O que fazer:** `authenticate_user_mfa` deve outputar `id_usuario` e essas tarefas devem consumi-lo.
- **[GRAVE]** `register_patient_case` — `id_paciente` e `id_caso` estão como entrada externa e também como saída. Se a tarefa cria o caso, não deve exigi-los como entrada. **O que fazer:** removê-los das entradas ou declarar a origem real; caso contrário, gerar e outputar.
- **[GRAVE]** `register_patient_case` — `output_data` não traz `idade`, `tempo_cateter_dias`, `apache_ii`, `sitio_insercao`, `comorbidades`, mas `fetch_external_cox_score` os consome como externos. **O que fazer:** `register_patient_case` deve declarar esses campos na saída para o Cox.
- **[GRAVE]** `fetch_external_microbiology` — `registros` está como entrada externa e é saída da própria tarefa. **O que fazer:** remover `registros` das entradas; ele deve ser produzido por `fetch_external_microbiology`.
- **[MÉDIO]** `import_microbiology` — `id_micro` está como entrada externa e nenhuma tarefa anterior o produz. Se a importação é do lote buscado, deve vir de `P_fetch_micro`; se é seleção de tela, documentar. **O que fazer:** `fetch_external_microbiology` outputar os IDs/registros e `import_microbiology` consumi-los.
- **[GRAVE]** `detect_mdr` — `id_alerta`, `destinatarios`, `canais`, `mensagem`, `id_bundle_override` estão como entradas externas e são inadequadas: `id_alerta` é saída de `detect_mdr`; `destinatarios`/`canais`/`mensagem` pertencem a `notify_critical_mdr_alert`; `id_bundle_override` pertence a `recommend_treatment_bundle`/`classify_case_nhsn`. **O que fazer:** mover esses campos para as tarefas corretas.
- **[MÉDIO]** `notify_critical_mdr_alert` — `destinatarios`, `canais`, `mensagem` estão externos. Se não forem escolha manual do operador, devem vir de configuração/alerta/`detect_mdr`. **O que fazer:** definir se são entrada de tela ou produzidos pelo fluxo.
- **[GRAVE]** `calculate_cox_score` — `cox_response` está externo, mas deveria vir de `fetch_external_cox_score`. **O que fazer:** `fetch_external_cox_score` deve outputar `cox_response` ou `calculate_cox_score` deve ler `valor_escore`/`faixa_risco`/`intervalo_confianca`/`versao_modelo`.
- **[GRAVE]** `recommend_treatment_bundle` — `nhsn_result` e `mdr_result` estão externos. Deveriam vir de `classify_case_nhsn` (`resultado`/`classificacoes_nhsn_id`) e `detect_mdr` (`multirresistente`/`classes_resistentes`). **O que fazer:** mapear as saídas anteriores para esses campos.
- **[GRAVE]** `estimate_risk_reduction` — `bundle_data` está externo, mas deveria vir de `recommend_treatment_bundle` (`tratamento_id`/`bundle_nome`/`justificativa`). Além disso, `id_caso` diz vir de `P_registry`, mas `T_estimate_risk_reduction` não tem arco de `P_registry` e os lugares que o alimentam não outputam `id_caso`. **O que fazer:** propagar `id_caso` e `bundle_data` nos lugares de entrada.
- **[MÉDIO]** `estimate_risk_reduction` — `acao`, `entidade`, `id_entidade`, `filtros` são campos de auditoria, não de estimativa, e não são produzidos antes. **O que fazer:** movê-los para `register_audit_log` ou gerá-los pelo orquestrador.
- **[GRAVE]** `register_audit_log` — `id_usuario`, `acao`, `entidade`, `id_entidade`, `filtros` estão todos externos. A transição é alimentada por `P_estimate_risk`, mas não consome nenhuma saída dela. **O que fazer:** registrar ação/entidade a partir da tarefa auditada e `id_usuario` da autenticação.
- **[MÉDIO]** `view_surveillance_dashboard` e `export_surveillance_report` — `id_usuario` está externo (deveria vir da auth) e não consomem saídas de `P_calc_cox`/`P_dashboard`; se os relatórios dependem desses dados, falta mapeamento. **O que fazer:** conectar dados ou assumir consulta ao banco com período/filtros.
- **[GRAVE]** `execute_surveillance_cycle`/`P_cycle` — `id_caso` diz vir de `P_registry`, mas `T_join_cycle` (único a produzir `P_cycle`) não tem arco de `P_registry`; nenhum dos lugares de entrada do join carrega `id_caso`. **O que fazer:** propagar `id_caso` até o join ou conectar `P_registry`/`T_join`.
- **[MÉDIO]** Saídas não consumidas — `P_import_micro` (`validos`/`invalidos`/`duplicados`/`erros`), `P_notify_mdr` (`notificacoes_enviadas`/`latencia_s`/`status`), `P_dashboard` (agregados), `P_export_report` (`arquivo_nome`/`url_download`), `P_audit_log` (`registros`/`id_log`) não alimentam nenhuma transição. **O que fazer:** conectar ou documentar como efeito colateral.

### Estrutura
- **[GRAVE]** `T_authenticate_user_mfa` — sem arco de entrada e sem arco de saída. **O que fazer:** conectar ao fluxo.
- **[GRAVE]** `T_execute_surveillance_cycle` — sem arco de entrada e sem arco de saída. **O que fazer:** conectar ao fluxo.
- **[GRAVE]** Conflitos de token — `P_registry` alimenta `T_fetch_external_microbiology` e `T_fetch_external_cox_score`; `P_import_micro` alimenta `T_classify_case_nhsn`, `T_detect_mdr` e `T_join_cycle`; `P_classify_nhsn` alimenta `T_recommend_treatment_bundle` e `T_join_cycle`; `P_detect_mdr` alimenta `T_notify_critical_mdr_alert`, `T_recommend_treatment_bundle` e `T_join_cycle`; `P_calc_cox` alimenta `T_estimate_risk_reduction`, `T_view_surveillance_dashboard` e `T_join_cycle`; `P_recommend_bundle` alimenta `T_estimate_risk_reduction` e `T_join_cycle`; `P_dashboard` alimenta `T_export_surveillance_report` e `T_fim_dashboard`. Com um único token, só um ramo consome, bloqueando os demais. **O que fazer:** usar fork/duplicação de tokens ou lugares separados.
- **[GRAVE]** `T_join_cycle` — exige tokens simultâneos de `P_import_micro`, `P_classify_nhsn`, `P_detect_mdr`, `P_calc_cox` e `P_recommend_bundle`, mas esses lugares são consumidos por transições downstream. Sem arcos de leitura/teste, o join nunca fica habilitado. **O que fazer:** sincronizar em lugares de conclusão de cada ramo, não nos intermediários.
- **[MÉDIO]** `P_dashboard` — alimenta `T_export_surveillance_report` e `T_fim_dashboard`. Se ambos devem ocorrer, falta fork; se é escolha, falta guard.
- **[LEVE]** Bipartição — todos os arcos são lugar→transição ou transição→lugar; não há lugar-lugar nem transição-transição.

### Marcação
- **[GRAVE]** Há início claro (`P0` com 1 ficha), mas `P_fim` não é alcançável para o fluxo completo devido aos conflitos/join impossível. Apenas ramos parciais podem chegar a `P_fim`. **O que fazer:** corrigir conflitos e join para permitir que todas as tarefas do ciclo convirjam.

### Paralelismo
- **[GRAVE]** Os ramos que deveriam correr em paralelo (`fetch_micro` vs `fetch_cox`; `classify` vs `detect`; `estimate` vs `dashboard`/`export`) competem por um único token nos lugares de origem. **O que fazer:** criar lugares de fork/AND-split para duplicar fichas.
- **[GRAVE]** `T_recommend_treatment_bundle`, `T_estimate_risk_reduction` e `T_join_cycle` exigem sincronização, mas os tokens necessários são consumidos por outros ramos. **O que fazer:** redesenhar sincronização com lugares de conclusão e sem conflito.
- **[MÉDIO]** `T_notify_critical_mdr_alert` pode rodar em paralelo com `T_recommend_treatment_bundle` após `detect_mdr`, mas hoje disputam `P_detect_mdr`. **O que fazer:** fork após `detect_mdr`.

## Conferências que passaram
- NOMES: todas as 15 tarefas do `tasks.yaml` têm uma transição com `task_id` correspondente.
- DONO: todos os `agente_id` de transições de tarefa batem com o responsável no `tasks.yaml`.
- ESTRUTURA: todos os arcos são lugar→transição ou transição→lugar (bipartição correta).
- FLUXO: `P_registry -> T_fetch_external_microbiology` usa `id_caso`/`id_paciente` produzidos por `register_patient_case`; `P_fetch_micro -> T_import_microbiology` usa `registros` produzidos por `fetch_external_microbiology`; `P_detect_mdr -> T_notify_critical_mdr_alert` usa `alerta_id` produzido por `detect_mdr`.
- MARCAÇÃO: `P0` tem 1 ficha inicial e é o início claro.
- ENTRADAS EXTERNAS LEGÍTIMAS: `email`, `senha`, `totp_code` em autenticação; filtros de dashboard/exportação; flags `sobrescrita`/`recalcular`/`justificativa_override` quando são decisões de tela.

## Veredito
A rede não está pronta para gerar código: faltam conexões das transições de autenticação e ciclo, correção dos contratos de dados/entradas externas e redesenho de forks/sincronização para eliminar conflitos e permitir que o ciclo completo alcance o fim.

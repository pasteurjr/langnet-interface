# Validação por Caso de Uso (template do pipeline)

Processo de validação da aplicação gerada pelo LangNet, no formato padrão
UC → passos → casos de teste → esperado vs obtido → evidência → status.

## Scripts
- `uc_validation_runner.py` — navega a app gerada (Playwright), executa o fluxo
  de cada UC, verifica delta no banco, captura screenshots. Gera `uc-results.json`.
- `ws_exec_tasks.py` — dispara cada task real via WebSocket (ws-server) e registra
  resultado (completed/error/timeout) + tempo. Gera `ws-exec-results.json`.
- `gerar_doc_validacao.py` — consolida os dois em um PDF de validação por UC.

## Como virar etapa do pipeline
Após a Geração de Código: parsear os UCs da spec → gerar casos de teste →
executar contra a app (UI + servidor + banco) → emitir o PDF como artefato de
aceitação. Insumos: specification_document (UCs+passos), ui_spec (telas),
tasks.yaml (tasks reais), app gerada em execução.

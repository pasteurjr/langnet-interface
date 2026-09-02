# E2E do app gerado BioByte Sentinela (prova de geração limpa)

- `deploy_v6.sh <code_generation_session_id>` — baixa o ZIP da sessão de Geração de Código
  (mesmo endpoint do botão da interface), extrai em `/tmp/biobyte-app3`, escreve o `.env`
  (DeepSeek + banco `biobyte_app` + porta 5031), verifica que o gerador aplicou tudo sozinho
  (classificação, traduções MCP, alinhamento de nomes, busca externa, repasse de contexto),
  sobe o servidor e roda o teste encadeado.
- `petri_flow.py` — replica a orquestração da Rede de Petri: processa os lugares em ordem
  topológica (`petri_chain.json`), mesclando os resultados anteriores no dado de entrada,
  exatamente como a lógica dos lugares faz. Placar por tarefa. (porta 5030; use `sed` p/ 5031)
- `one_task.py <task> '<json>'` — dispara uma tarefa isolada (diagnóstico).

Resultado (02/09/2026, sessão 1d4cd924): **12/13** — a 13ª (administração de usuário) passa
quando recebe seus próprios dados (nome/email); o SEED do teste é clínico.

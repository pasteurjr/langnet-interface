# {{PROJECT_NAME}}

Sistema agêntico gerado pelo **LangNet** no padrão **visualtasksexec**.

## Arquitetura

```
+---------------+   HTTP/REST   +-----------+
|   frontend    +-------------->+  backend  |
|  (React :3001)|               |  (FastAPI |
|               |               |   :8001)  |
|               |               +-----------+
|               |
|               |   WebSocket
|               +----+
|               |    |
+---------------+    |          +------------+
                     +--------->+ ws-server  |
                                | (CrewAI    |
                                |  :{{WS_PORT}})    |
                                +------------+
```

- **frontend** — React + 5 abas (Execução · Operação · Inputs · Outputs · Logs)
- **backend** — FastAPI servindo `/api/projects`, `/api/projects/{id}` (lê `project.json`)
- **ws-server** — WebSocket genérico que recebe `execute_task` e dispara CrewAI

## Como rodar

```bash
# Setup
cp ws-server/.env.example ws-server/.env  # adicione DEEPSEEK_API_KEY
docker compose up -d

# Acesse
http://localhost:{{FRONTEND_PORT}}
```

## Estrutura do projeto

```
{{PROJECT_SLUG}}/
├── frontend/         # React app (5 abas)
├── backend/          # FastAPI REST + project.json embarcado
├── ws-server/        # CrewAI + WebSocket
├── docker-compose.yml
└── README.md
```

## Fluxo de execução

1. Frontend carrega `project.json` do backend
2. Aba **Execução** mostra os places + transições; usuário clica "▶ Executar tudo"
3. Engine JS no browser avança token por token, e para cada place dispara o JS armazenado em `place.logica`
4. O JS abre WebSocket pro ws-server, envia `{type:"execute_task", data:{task_name, input_data}}`
5. ws-server roda CrewAI, retorna `task_completed`
6. Frontend agrega outputs e atualiza aba **Outputs** + **Logs** em tempo real

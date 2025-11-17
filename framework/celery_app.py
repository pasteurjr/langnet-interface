
from celery import Celery
import os

# Configura o Celery
celery_app = Celery(
    "servertropicalagents",  # Nome do módulo onde as tarefas estão definidas
    broker="sqla+sqlite:///celery.db",  # Usa SQLite como broker
    backend="db+sqlite:///celery_results.db",  # Usa SQLite como backend
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Cria os arquivos de banco de dados, se não existirem
if not os.path.exists("celery.db"):
    open("celery.db", "w").close()
if not os.path.exists("celery_results.db"):
    open("celery_results.db", "w").close()

# Importa o módulo servertropicalagents para registrar as tarefas
from servertropicalagents import agente_teste, agente_monitoramento_eficiencia, agente_teamanalysisuser,teamanalysisdbuser,agente_monitoramento_emails
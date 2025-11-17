# Verificação de Dependências - WebSocket API Tropical

## Status das Dependências

### ✅ Arquivos .env encontrados:
- `/home/pasteurjr/progpython/valep1/framework/.env` - **OK**
- `/home/pasteurjr/progpython/valep1/agentes/.env` - **OK**  
- `/home/pasteurjr/progpython/valep1/petri-net-server/.env` - **OK**

### ✅ Configurações de Email (framework/.env):
```
SMTP_HOST = smtp.gmail.com
SMTP_PORT = 465 
IMAP_HOST = imap.gmail.com
IMAP_PORT = 993  
EMAIL_USERNAME=pasteurjr@gmail.com
EMAIL_PASSWORD=sixw lprd gkma ksuq
```

### ❌ PROBLEMA CRÍTICO: MindsDB Configuration

**Problema identificado:**
```python
# Em frameworkagentsadapter.py
server = mindsdb_sdk.connect()  # Conecta em localhost por padrão
```

**Servidor real:** `192.168.1.115:47334`

## Correções Necessárias

### 1. Atualizar configuração MindsDB no .env:
```bash
# Adicionar ao framework/.env
MINDSDB_HOST=192.168.1.115
MINDSDB_PORT=47334
MINDSDB_USER=admin
MINDSDB_PASSWORD=password123
```

### 2. Corrigir frameworkagentsadapter.py:
```python
def MindsDbQuery(question: str) -> str:
    server = mindsdb_sdk.connect(
        url=f"http://{os.getenv('MINDSDB_HOST', 'localhost')}:{os.getenv('MINDSDB_PORT', '47334')}",
        login=os.getenv('MINDSDB_USER', 'admin'),
        password=os.getenv('MINDSDB_PASSWORD', 'password123')
    )
    # resto do código...

def MindsDbProductStock(question: str) -> str:
    server = mindsdb_sdk.connect(
        url=f"http://{os.getenv('MINDSDB_HOST', 'localhost')}:{os.getenv('MINDSDB_PORT', '47334')}",
        login=os.getenv('MINDSDB_USER', 'admin'), 
        password=os.getenv('MINDSDB_PASSWORD', 'password123')
    )
    # resto do código...
```

### 3. Instalar dependências Python:
```bash
cd /home/pasteurjr/progpython/valep1/framework
pip install -r requirements.txt

# Se requirements.txt não existir, instalar manualmente:
pip install websockets mindsdb-sdk crewai crewai-tools pydantic python-dotenv
```

### 4. Verificar agents.yaml e tasks.yaml:
- ✅ `framework/agents.yaml` - **EXISTE**
- ✅ `framework/tasks.yaml` - **EXISTE**

### 5. Verificar disponibilidade do servidor MindsDB:
```bash
# Testar conectividade
curl -I http://192.168.1.115:47334
```

## Próximos Passos para Teste

1. **Corrigir MindsDB configuration**
2. **Instalar dependências**
3. **Testar conexão MindsDB**
4. **Executar WebSocket API:**
   ```bash
   cd framework
   python websocket_api_tropical.py --mode server --port 5002
   ```
5. **Testar cliente:**
   ```bash
   python websocket_api_tropical.py --mode test --port 5002
   ```

## Dependências Completas Necessárias

```
websockets>=11.0
mindsdb-sdk>=0.8.0
crewai>=0.30.0
crewai-tools>=0.1.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
asyncio
json
logging
traceback
datetime
threading
```

## Status Final
- 🔴 **MindsDB Configuration** - PRECISA CORREÇÃO
- 🟡 **Dependências Python** - VERIFICAR INSTALAÇÃO
- 🟢 **Configurações Email** - OK
- 🟢 **Arquivos YAML** - OK
- 🟢 **WebSocket API** - PRONTA PARA TESTE (após correções)
#!/usr/bin/env bash
# Implanta a Geração de Código LIMPA do BioByte (sessão $1) em /tmp/biobyte-app3 e roda o E2E.
set -u
SID="$1"; APP=/tmp/biobyte-app3; PORT=5031
TOKEN=$(cat /tmp/langnet_token.txt)
BENV=/home/pasteurjr/progreact/langnet-interface/backend/.env
DSK=$(grep -E '^DEEPSEEK_API_KEY=' $BENV | cut -d= -f2-)
echo "== 1) download ZIP da sessão $SID"
rm -rf $APP $APP.zip; mkdir -p $APP
HTTP=$(curl -s -o $APP.zip -w '%{http_code}' -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8003/api/code-generation/$SID/download")
echo "   http=$HTTP tipo=$(file -b $APP.zip | cut -c1-40)"
if [ "$HTTP" = "200" ] && file -b $APP.zip | grep -qi zip; then
  unzip -o -q $APP.zip -d $APP
else
  echo "   fallback: extraindo generated_files do banco"
  source ~/miniforge3/etc/profile.d/conda.sh && conda activate langnet
  python3 - "$SID" "$APP" <<'PY'
import sys,re,json,os,mysql.connector as mc
sid,app=sys.argv[1],sys.argv[2]
env={m.group(1):m.group(2).strip() for ln in open(".env") for m in [re.match(r'\s*([A-Z_]+)\s*=\s*(.*)',ln)] if m}
cn=mc.connect(host="127.0.0.1",port=3308,user="producao",password=env.get("DB_PASSWORD","112358123"),database="langnet");cur=cn.cursor()
cur.execute("SELECT generated_files FROM code_generation_sessions WHERE id=%s",(sid,)); files=json.loads(cur.fetchone()[0] or "[]")
for f in files:
    p=os.path.join(app,f["path"]); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,"w",encoding="utf-8").write(f.get("content",""))
print(f"   {len(files)} arquivos escritos")
PY
fi
WS=$(dirname "$(find $APP -name websocket_server.py | head -1)"); echo "   ws-server em: $WS ($(find $APP -type f | wc -l) arquivos)"
echo "== 2) .env do app (DeepSeek, banco biobyte_app, porta $PORT)"
cat > $WS/.env <<ENV
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=$PORT
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=$DSK
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_MODEL_NAME=deepseek/deepseek-v4-flash
DEEPSEEK_MAX_TOKENS=32768
CREWAI_TESTING=true
OTEL_SDK_DISABLED=true
DB_HOST=127.0.0.1
DB_PORT=3308
DB_USER=producao
DB_PASSWORD=112358123
DB_NAME=biobyte_app
ENV
echo "== 3) o GERADOR aplicou tudo sozinho? (zero edição manual)"
python3 - "$WS" <<'PY'
import sys,yaml,re; ws=sys.argv[1]
t=yaml.safe_load(open(f"{ws}/tasks.yaml"))
for n in ["classify_case_nhsn","recommend_treatment_bundle","estimate_risk_reduction","fetch_and_persist_microbiology","calculate_cox_risk_score"]:
    c=t.get(n,{}); print(f"   tasks.yaml {n:32} execution={c.get('execution')}" + ("  [portão]" if c.get("execution_reason") else ""))
m=open(f"{ws}/mcp_tools.py").read()
print("   mcp_tools.py  ARG_ALIASES vazio?", "MCP_ARG_ALIASES = {}" in m, "| OUT_ALIASES vazio?", "MCP_OUT_ALIASES = {}" in m)
a=open(f"{ws}/adapters.py").read()
print("   adapters.py   alinhamento is_icsac→classificacao_nhsn:", "input_data.get('classificacao_nhsn', input_data.get('is_icsac'))" in a)
print("   adapters.py   alinhamento admin_id→usuario_id:", "input_data.get('usuario_id', input_data.get('admin_id'))" in a)
w=open(f"{ws}/websocket_server.py").read()
print("   ws-server     prefetch MCP:", "_mcp_prefetch" in w, "| carry-forward:", w.count("Carry-forward de CONTEXTO"), "vias")
PY
echo "== 4) sobe o app na :$PORT"
OLD=$(ss -ltnp 2>/dev/null | grep ":$PORT " | grep -oE "pid=[0-9]+" | head -1 | cut -d= -f2); [ -n "$OLD" ] && kill $OLD && sleep 1
cd "$WS" && source ~/miniforge3/etc/profile.d/conda.sh && conda activate langnet
rm -f /tmp/biobyte-ws-$PORT.log
setsid nohup python -u main.py > /tmp/biobyte-ws-$PORT.log 2>&1 < /dev/null & disown
for i in $(seq 1 40); do ss -ltn | grep -q ":$PORT " && { echo "   ws UP em ~${i}s"; break; }; sleep 1; done
grep -E "tool\(s\)|Traceback|Error" /tmp/biobyte-ws-$PORT.log | tail -4 | sed 's/^/   /'
echo "== 5) E2E encadeado pela Rede de Petri (:$PORT)"
cd /home/pasteurjr/progreact/langnet-interface && timeout 900 python /tmp/petri_flow_5031.py 2>&1 | tail -16

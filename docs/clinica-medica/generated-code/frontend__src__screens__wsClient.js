const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:5003";

// Dispara uma task no ws-server e resolve com o resultado (task_completed).
export function runTask(taskName, inputData) {
  return new Promise((resolve, reject) => {
    let ws;
    try { ws = new WebSocket(WS_URL); } catch (e) { reject(e); return; }
    const timer = setTimeout(() => { try { ws.close(); } catch (e) {} reject(new Error("timeout")); }, 120000);
    ws.onopen = () => ws.send(JSON.stringify({ type: "execute_task", data: { task_name: taskName, input_data: inputData || {} } }));
    ws.onmessage = (ev) => {
      let m; try { m = JSON.parse(ev.data); } catch (e) { return; }
      if (m.type === "task_completed" || m.type === "task_result") {
        clearTimeout(timer); ws.close(); resolve(m.data && m.data.result !== undefined ? m.data.result : (m.data || {}));
      } else if (m.type === "error") {
        clearTimeout(timer); ws.close(); reject(new Error((m.data && m.data.error) || "erro na task"));
      }
    };
    ws.onerror = () => { clearTimeout(timer); reject(new Error("WebSocket error")); };
  });
}

// Converte "a, b, c" em ["a","b","c"] (campos de lista → tabela filha)
export function splitList(v) {
  if (Array.isArray(v)) return v;
  if (!v) return [];
  return String(v).split(",").map((x) => x.trim()).filter(Boolean);
}

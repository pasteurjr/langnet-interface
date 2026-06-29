import { useState, useCallback, useRef } from "react";

const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:{{WS_PORT}}";

/**
 * Engine de execução da Petri Net no browser.
 * - Avança transição habilitada → executa place.logica (JS) do(s) lugar(es) de saída
 * - place.logica abre WebSocket para o agente, envia execute_task e recebe task_completed
 * - Mantém marking, outputs por place, eventos consolidados
 */
const usePetriNetExecution = (project) => {
  const petri = project?.petriNet || project?.project_data || {};
  const places = petri.lugares || [];
  const transitions = petri.transicoes || [];
  const arcs = petri.arcos || [];

  // marking inicial: tokens definidos no JSON
  const initialMarking = () => Object.fromEntries(places.map((p) => [p.id, p.tokens || 0]));

  const [marking, setMarking] = useState(initialMarking);
  const [outputs, setOutputs] = useState({}); // {placeId: outputObject}
  const [events, setEvents] = useState([]);   // [{ts, type, place, task_name, data}]
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(0);
  const outputsRef = useRef({});

  const pushEvent = useCallback((evt) => {
    const e = { ts: new Date().toISOString(), ...evt };
    setEvents((prev) => [...prev, e]);
  }, []);

  // Pré-arcos de cada transição (lugar → transição)
  const preArcsOf = (transId) => arcs.filter((a) => a.destino === transId);
  // Pós-arcos de cada transição (transição → lugar)
  const postArcsOf = (transId) => arcs.filter((a) => a.origem === transId);

  const isTransitionEnabled = useCallback((trans, m) => {
    const pre = preArcsOf(trans.id);
    return pre.every((a) => (m[a.origem] || 0) >= (a.peso || 1));
  }, [arcs]);

  const getEnabledTransitions = useCallback((m = marking) =>
    transitions.filter((t) => isTransitionEnabled(t, m)),
    [transitions, marking, isTransitionEnabled]
  );

  // Executa o JS de logica de um place. Retorna o output.
  const runPlaceLogic = useCallback(async (place, input) => {
    if (!place.logica || !place.logica.includes("WebSocket")) {
      return { ...input, place_id: place.id, status: "skipped" };
    }
    // utils disponível dentro do JS do place
    const utils = {
      clone: (o) => JSON.parse(JSON.stringify(o || {})),
      now: () => new Date().toISOString(),
      getPlaceOutput: (pid) => outputsRef.current[pid] || null,
    };
    pushEvent({ type: "place_start", place: place.id, task_name: extractTaskName(place.logica) });
    try {
      // Cria função async a partir do código JS armazenado em place.logica
      // eslint-disable-next-line no-new-func
      const fn = new Function("input", "utils", "WebSocket", `return (async () => { ${place.logica} })();`);
      const out = await fn(input || {}, utils, WebSocket);
      pushEvent({ type: "place_done", place: place.id, data: out });
      return out;
    } catch (err) {
      pushEvent({ type: "place_error", place: place.id, data: { error: err.message } });
      return { ...input, error: err.message, status: "error" };
    }
  }, [pushEvent]);

  const fireTransition = useCallback(async (trans) => {
    pushEvent({ type: "transition_fired", place: trans.id });
    // remove tokens dos predecessores e adiciona aos sucessores
    const newMarking = { ...marking };
    for (const a of preArcsOf(trans.id)) newMarking[a.origem] = (newMarking[a.origem] || 0) - (a.peso || 1);
    for (const a of postArcsOf(trans.id)) newMarking[a.destino] = (newMarking[a.destino] || 0) + (a.peso || 1);
    setMarking(newMarking);
    setStep((s) => s + 1);

    // Para cada lugar de saída, executa a lógica JS — usando ref pra evitar stale state
    for (const a of postArcsOf(trans.id)) {
      const place = places.find((p) => p.id === a.destino);
      if (!place) continue;
      // Input agrega outputs dos lugares de entrada da transição
      const inputData = {};
      for (const preA of preArcsOf(trans.id)) {
        Object.assign(inputData, outputsRef.current[preA.origem] || {});
      }
      const result = await runPlaceLogic(place, inputData);
      outputsRef.current[place.id] = result;
      // Force re-render com o estado mais recente
      setOutputs({ ...outputsRef.current });
    }
    return newMarking;
  }, [marking, places, arcs, runPlaceLogic, pushEvent]);

  const runOneStep = useCallback(async () => {
    const enabled = getEnabledTransitions();
    if (enabled.length === 0) {
      pushEvent({ type: "no_transitions" });
      return false;
    }
    // Estratégia: dispara a primeira habilitada (priorizando ordem)
    await fireTransition(enabled[0]);
    return true;
  }, [getEnabledTransitions, fireTransition, pushEvent]);

  const runAll = useCallback(async (maxSteps = 50) => {
    setRunning(true);
    pushEvent({ type: "run_started" });
    let s = 0;
    while (s < maxSteps) {
      const ok = await runOneStep();
      if (!ok) break;
      s++;
    }
    pushEvent({ type: "run_finished", data: { steps: s } });
    setRunning(false);
  }, [runOneStep, pushEvent]);

  const reset = useCallback(() => {
    setMarking(initialMarking());
    setOutputs({});
    outputsRef.current = {};
    setEvents([]);
    setStep(0);
    setRunning(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [places]);

  // Dispara 1 task isolada (sem avançar tokens) — útil pro debug manual
  const runTask = useCallback(async (taskName, inputData) => {
    pushEvent({ type: "manual_task_start", task_name: taskName, data: inputData });
    try {
      const ws = new WebSocket(WS_URL);
      const result = await new Promise((resolve, reject) => {
        const t = setTimeout(() => { ws.close(); reject(new Error("timeout")); }, 120000);
        ws.onopen = () => ws.send(JSON.stringify({ type: "execute_task", data: { task_name: taskName, input_data: inputData || {} } }));
        ws.onmessage = (e) => {
          const r = JSON.parse(e.data);
          if (r.type === "task_completed" || r.type === "task_result") {
            clearTimeout(t); ws.close();
            resolve(r.data?.result ?? r.data ?? {});
          } else if (r.type === "error") {
            clearTimeout(t); ws.close();
            reject(new Error(r.data?.error || "task error"));
          }
        };
        ws.onerror = () => { clearTimeout(t); reject(new Error("WebSocket error")); };
      });
      pushEvent({ type: "manual_task_done", task_name: taskName, data: result });
      return result;
    } catch (err) {
      pushEvent({ type: "manual_task_error", task_name: taskName, data: { error: err.message } });
      throw err;
    }
  }, [pushEvent]);

  return {
    marking, outputs, events, running, step,
    enabledTransitions: getEnabledTransitions(),
    runOneStep, runAll, reset, runTask,
  };
};

function extractTaskName(logica) {
  const m = /TASK_NAME\s*=\s*['"]([^'"]+)['"]/.exec(logica || "");
  return m ? m[1] : "";
}

export default usePetriNetExecution;

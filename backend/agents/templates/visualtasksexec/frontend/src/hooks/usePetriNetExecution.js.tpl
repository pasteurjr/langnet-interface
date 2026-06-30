import { useState, useEffect, useRef, useCallback } from "react";
import { PetriNetSimulator } from "../petri-engine/PetriNetSimulator";

/**
 * Hook que orquestra a execução da Petri Net usando o motor REAL importado
 * do petri-net-editor:
 *   - PetriNetSimulator: matrizes de incidência + disparo + log
 *   - PlaceProcessor: executa place.logica em sandbox com utils.{merge,getPlaceOutput,...}
 *   - GuardEvaluator: guards JS com escopo isolado
 *
 * O contrato de UI:
 *   - exec.marking          → tokens por place (cópia do markingVector)
 *   - exec.outputs          → place.output_data agregados
 *   - exec.events           → [{ts, type, ...}] consolidados
 *   - exec.enabledTransitions
 *   - exec.runOneStep()
 *   - exec.runAll(maxSteps?)
 *   - exec.reset()
 *   - exec.runTask(name, input)  → dispara 1 task WS isolada (manual, sem petri)
 */
const usePetriNetExecution = (project) => {
  const petri = project?.petriNet || project?.project_data || {};

  // Simulator vive em ref pra sobreviver re-renders
  const simulatorRef = useRef(null);
  const [tick, setTick] = useState(0); // força re-render quando muda estado interno

  const [events, setEvents] = useState([]);
  const [running, setRunning] = useState(false);

  const pushEvent = useCallback((evt) => {
    const e = { ts: new Date().toISOString(), ...evt };
    setEvents((prev) => [...prev, e]);
  }, []);

  // Inicializa o simulator quando o projeto chegar
  useEffect(() => {
    if (!petri || !petri.lugares || petri.lugares.length === 0) return;
    const sim = new PetriNetSimulator(petri);
    sim.placeProcessor.setCallbacks({
      onPlaceProcessed: (placeId, inputData, outputData) => {
        pushEvent({ type: "place_done", place: placeId, data: outputData });
        setTick((t) => t + 1);
      },
      onError: (placeId, error) => {
        pushEvent({
          type: "place_error",
          place: placeId,
          data: { error: error?.message || String(error) },
        });
        setTick((t) => t + 1);
      },
    });
    simulatorRef.current = sim;
    setTick((t) => t + 1);
    return () => {
      try { sim.cancelAllProcessing(); } catch {}
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [project]);

  const fireOne = useCallback(async (transitionId) => {
    const sim = simulatorRef.current;
    if (!sim) return false;
    if (!sim.isTransitionEnabled(transitionId)) return false;
    pushEvent({ type: "transition_fired", place: transitionId });
    try {
      sim.fireTransition(transitionId);
      sim.updatePetriNetTokens();
      setTick((t) => t + 1);
      return true;
    } catch (err) {
      pushEvent({ type: "fire_error", place: transitionId, data: { error: err.message } });
      return false;
    }
  }, [pushEvent]);

  const runOneStep = useCallback(async () => {
    const sim = simulatorRef.current;
    if (!sim) return false;
    const enabled = sim.getEnabledTransitions();
    if (enabled.length === 0) {
      pushEvent({ type: "no_transitions" });
      return false;
    }
    // Estratégia: primeira habilitada (poderia ser por prioridade)
    return await fireOne(enabled[0].id);
  }, [fireOne, pushEvent]);

  const runAll = useCallback(async (maxSteps = 50) => {
    setRunning(true);
    pushEvent({ type: "run_started" });
    let s = 0;
    while (s < maxSteps) {
      const ok = await runOneStep();
      if (!ok) break;
      // Aguarda os places em processamento (place.logica async)
      await new Promise((r) => setTimeout(r, 800));
      s++;
    }
    pushEvent({ type: "run_finished", data: { steps: s } });
    setRunning(false);
  }, [runOneStep, pushEvent]);

  const reset = useCallback(() => {
    const sim = simulatorRef.current;
    if (sim) {
      sim.cancelAllProcessing();
      sim.resetSimulation();
    }
    setEvents([]);
    setTick((t) => t + 1);
  }, []);

  // ===== Disparo de task isolada (manual, sem passar pela Petri) =====
  const WS_URL = process.env.REACT_APP_WS_URL || "ws://localhost:{{WS_PORT}}";
  const runTask = useCallback(async (taskName, inputData) => {
    pushEvent({ type: "manual_task_start", task_name: taskName, data: inputData });
    try {
      const ws = new WebSocket(WS_URL);
      const result = await new Promise((resolve, reject) => {
        const t = setTimeout(() => { ws.close(); reject(new Error("timeout")); }, 120000);
        ws.onopen = () => ws.send(JSON.stringify({
          type: "execute_task",
          data: { task_name: taskName, input_data: inputData || {} },
        }));
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
  }, [WS_URL, pushEvent]);

  // Snapshot do estado pro UI consumir
  const sim = simulatorRef.current;
  const marking = sim ? { ...sim.markingVector } : {};
  const outputs = {};
  if (sim) {
    sim.petriNet.lugares.forEach((p) => {
      if (p.output_data && Object.keys(p.output_data).length > 0) {
        outputs[p.id] = p.output_data;
      }
    });
  }
  const enabledTransitions = sim ? sim.getEnabledTransitions() : [];
  const step = sim ? sim.simulationLog.length : 0;

  return {
    marking,
    outputs,
    events,
    running,
    step,
    enabledTransitions,
    runOneStep,
    runAll,
    reset,
    runTask,
    // expostos pra debug / abas
    _tick: tick,
    _simulator: sim,
  };
};

export default usePetriNetExecution;

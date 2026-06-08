/**
 * Smoke runtime real: usa uma sessão completed do SPRINT4, clica
 * ▶ Executar, aguarda o servidor agêntico subir em ws://localhost:5002,
 * conecta via WebSocket, manda get_task_info e confirma que o servidor
 * gerado responde com a lista de tasks. Depois para o run.
 */
import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'runtime');
let stepIdx = 1;
const ts = (label: string) => path.join(OUT, `${String(stepIdx++).padStart(2, '0')}-${label}.png`);

async function login(page: Page) {
  const res = await page.request.post(`${API_BASE}/auth/login`, {
    data: { email: EMAIL, password: PASSWORD },
    headers: { 'Content-Type': 'application/json' },
  });
  const body = await res.json();
  await page.goto(`${APP_BASE}/login`);
  await page.evaluate(([t, u]) => {
    localStorage.setItem('accessToken', t);
    localStorage.setItem('token', t);
    localStorage.setItem('user', JSON.stringify(u));
  }, [body.access_token, body.user]);
}

test.beforeAll(() => { fs.mkdirSync(OUT, { recursive: true }); });

test('Runtime real: ▶ Executar → servidor sobe → WS responde get_task_info', async ({ page }) => {
  test.setTimeout(180_000);
  page.on('dialog', async (d) => { await d.accept().catch(() => {}); });

  await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  // Seleciona primeira sessão completed
  await page.evaluate(() => {
    const sess = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .find((el) => /completed/i.test(el.textContent || ''));
    (sess as HTMLElement)?.click();
  });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('session-loaded'), fullPage: true });

  // Clica ▶ Executar
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /^▶ Executar$/.test((b.textContent || '').trim())) as HTMLButtonElement | undefined;
    btn?.click();
  });

  // Aguarda status do run virar RUNNING via API
  console.log('Aguardando status RUNNING via /runs API...');
  const token = await page.evaluate(() => localStorage.getItem('accessToken') || localStorage.getItem('token'));
  const sessionId = await page.evaluate(() => {
    const m = window.location.pathname.match(/code-generation/);
    return m ? null : null;
  });
  // Pega session id atual da UI (sessão selecionada — primeira completed)
  const currentSessionId = await page.evaluate(async (api) => {
    const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
    const r = await fetch(`${api}/code-generation?project_id=422027f1-9e89-4f84-9474-adb67f43c8ff`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const body = await r.json();
    return (body.sessions || []).find((s: any) => s.status === 'completed')?.id;
  }, API_BASE);
  console.log('session:', currentSessionId);

  // Polling manual (mais simples que waitForFunction com truthy/null)
  let runningRunId = '';
  const deadline = Date.now() + 150_000;
  while (Date.now() < deadline) {
    const res = await page.request.get(`${API_BASE}/code-generation/${currentSessionId}/runs`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok()) {
      const body = await res.json();
      const last = (body.runs || []).slice(-1)[0];
      console.log(`  → run status: ${last?.status}`);
      if (last?.status === 'running') { runningRunId = last.run_id; break; }
      if (last?.status === 'crashed') {
        const stat = await page.request.get(`${API_BASE}/code-generation/run/${last.run_id}/status`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const s = await stat.json();
        throw new Error(`Run crashed antes de ficar running: tail=${(s.stdout_tail || []).slice(-10).join(' | ')}`);
      }
    }
    await page.waitForTimeout(3000);
  }
  console.log('run id rodando:', runningRunId);
  expect(runningRunId, 'Nenhum run em status running em 150s').toBeTruthy();

  // Servidor websockets.serve() pode demorar ~3-5s para bindar a porta após status=running.
  // Poll TCP open antes do handshake WS.
  console.log('Aguardando bind em :5002...');
  let portOpen = false;
  const portDeadline = Date.now() + 30_000;
  while (Date.now() < portDeadline) {
    portOpen = await page.evaluate(() => new Promise<boolean>((resolve) => {
      try {
        const ws = new WebSocket('ws://localhost:5002');
        const t = setTimeout(() => { try { ws.close(); } catch {}; resolve(false); }, 1500);
        ws.onopen = () => { clearTimeout(t); try { ws.close(); } catch {}; resolve(true); };
        ws.onerror = () => { clearTimeout(t); resolve(false); };
      } catch { resolve(false); }
    }));
    if (portOpen) break;
    await page.waitForTimeout(2000);
  }
  console.log('porta :5002 aceita conexões:', portOpen);
  expect(portOpen, 'ws://localhost:5002 não aceita conexões em 30s').toBeTruthy();
  await page.waitForTimeout(500);
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('status-running'), fullPage: true });

  // Confirma via WebSocket que o servidor agêntico responde
  // (conecta direto, manda get_task_info, espera task_info ou connected)
  const wsResult = await page.evaluate(async () => {
    return new Promise<any>((resolve) => {
      const events: any[] = [];
      const ws = new WebSocket('ws://localhost:5002');
      const timeout = setTimeout(() => {
        ws.close();
        resolve({ ok: false, error: 'timeout 20s', events });
      }, 20000);
      ws.onopen = () => {
        events.push({ type: 'open' });
        ws.send(JSON.stringify({ type: 'get_task_info' }));
      };
      ws.onmessage = (e) => {
        try {
          const p = JSON.parse(e.data);
          events.push({ type: p.type, dataKeys: p.data ? Object.keys(p.data) : [] });
          if (p.type === 'task_info' || p.type === 'connected') {
            clearTimeout(timeout);
            const tasks = p.data?.tasks || p.data?.available_tasks || [];
            ws.close();
            resolve({ ok: true, tasksCount: tasks.length, sample: tasks.slice(0, 5), events });
          }
        } catch {
          events.push({ raw: e.data });
        }
      };
      ws.onerror = () => {
        clearTimeout(timeout);
        resolve({ ok: false, error: 'ws error', events });
      };
    });
  });
  console.log('WS result:', JSON.stringify(wsResult, null, 2));
  await page.screenshot({ path: ts('after-ws-check'), fullPage: true });

  expect((wsResult as any).ok, `WebSocket falhou: ${JSON.stringify(wsResult)}`).toBeTruthy();
  expect((wsResult as any).tasksCount, 'Nenhuma task disponível no servidor agêntico').toBeGreaterThan(0);
  console.log(`✅ Servidor agêntico expõe ${(wsResult as any).tasksCount} tasks (sample: ${JSON.stringify((wsResult as any).sample)})`);

  // Para a execução via UI (botão Parar)
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /parar/i.test(b.textContent || '')) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('after-stop'), fullPage: true });
});

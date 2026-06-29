/**
 * Teste e2e do transit (corrigido): 4 passos + interceptor que hookou onmessage setter.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

test('Transit completo v2: 4 passos, P1+P2 → JOIN', async ({ page }) => {
  test.setTimeout(600_000);

  const events: string[] = [];
  page.on('console', (m) => {
    const t = m.text();
    if (t.includes('[trace]')) events.push(t);
  });

  await page.goto('http://localhost:3001');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]') as HTMLElement | null;
    card?.click();
  });
  await page.waitForTimeout(2500);

  // Interceptor melhorado: hooka onmessage setter
  await page.evaluate(() => {
    const origWS = window.WebSocket;
    (window as any).WebSocket = function(url: string, ...args: any[]) {
      const ws = new origWS(url, ...args);
      const origSend = ws.send.bind(ws);
      ws.send = function(data: any) {
        try {
          const obj = JSON.parse(data);
          if (obj.type === 'execute_task') {
            const tn = obj.data.task_name;
            const input = obj.data?.input_data || {};
            const keys = Object.keys(input);
            console.log(`[trace] SEND ${tn} keys=[${keys.join(',')}] size=${JSON.stringify(input).length}`);
            // Detail truncado
            const inputStr = JSON.stringify(input);
            const preview = inputStr.length > 600 ? inputStr.slice(0,600) + '...' : inputStr;
            console.log(`[trace] INPUT ${tn}: ${preview}`);
          }
        } catch {}
        return origSend(data);
      };
      // Hook do onmessage setter
      let origOnMsg: any = null;
      Object.defineProperty(ws, 'onmessage', {
        set(fn) {
          origOnMsg = function(ev: MessageEvent) {
            try {
              const r = JSON.parse(ev.data);
              if (r.type === 'task_completed' || r.type === 'task_result') {
                const tn = r.data?.task_name || '?';
                const res = r.data?.result || r.data || {};
                const rstr = JSON.stringify(res);
                const resPreview = rstr.length > 400 ? rstr.slice(0, 400) + '...' : rstr;
                console.log(`[trace] DONE ${tn} size=${rstr.length} preview=${resPreview}`);
              }
            } catch {}
            return fn(ev);
          };
          // Aplica direto
          (ws as any)._userOnMessage = fn;
          (ws as any).addEventListener('message', origOnMsg);
        },
        get() {
          return (ws as any)._userOnMessage;
        }
      });
      return ws;
    };
    (window as any).WebSocket.prototype = origWS.prototype;
    Object.assign((window as any).WebSocket, origWS);
    console.log('[trace] interceptor v2 instalado');
  });

  async function clickNext(label: string, waitMs: number) {
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button')).find((b) =>
        /próximo passo/i.test((b.textContent || '').trim())
      ) as HTMLButtonElement | undefined;
      btn?.click();
    });
    console.log(`>>> ${label} (aguardando ${waitMs/1000}s)`);
    await page.waitForTimeout(waitMs);
  }

  // P1: T_start_editorial → P_T001 chama WS (45s) → P_T002 chama WS (30s). Sequencial.
  await clickNext('Passo 1 — T_start_editorial (P1+P2 sequencial)', 90_000);
  // P2: T_process001 → P_T001_out (intermediário, sem WS) — quase instantâneo
  await clickNext('Passo 2 — T_process001', 5_000);
  // P3: T_process002 → P_T002_out — quase instantâneo
  await clickNext('Passo 3 — T_process002', 5_000);
  // P4: T_join003 → P_T003_in (integrate_suggested_themes) ~60s
  await clickNext('Passo 4 — T_join003 (JOIN, integrate_suggested_themes)', 90_000);

  console.log('=== EVENTOS ===');
  for (const e of events) console.log(e);

  fs.writeFileSync('/tmp/state-final-trace2.txt', events.join('\n'));
});

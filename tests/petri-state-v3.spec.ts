import { test } from '@playwright/test';
import * as fs from 'fs';

test('State flow REAL — Petri v3 (com sequenciamento)', async ({ page }) => {
  test.setTimeout(420_000);

  const events: string[] = [];
  page.on('console', (m) => {
    const t = m.text();
    if (t.includes('[trace]')) events.push(t);
  });

  await page.goto('http://localhost:3001');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  // Auto-seleciona projeto
  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]') as HTMLElement | null;
    card?.click();
  });
  await page.waitForTimeout(2500);

  // Intercepta WebSocket pra logar inputs
  await page.evaluate(() => {
    const origWS = window.WebSocket;
    (window as any).WebSocket = function(url: string, ...args: any[]) {
      const ws = new origWS(url, ...args);
      const origSend = ws.send.bind(ws);
      ws.send = function(data: any) {
        try {
          const obj = JSON.parse(data);
          if (obj.type === 'execute_task') {
            const keys = Object.keys(obj.data?.input_data || {});
            const sz = JSON.stringify(obj.data?.input_data || {}).length;
            console.log(`[trace] SEND ${obj.data.task_name} input_keys=[${keys.join(',')}] input_size=${sz}`);
            if (sz > 50) {
              console.log(`[trace] DETAIL ${obj.data.task_name}: ${JSON.stringify(obj.data.input_data).slice(0,400)}`);
            }
          }
        } catch {}
        return origSend(data);
      };
      return ws;
    };
    (window as any).WebSocket.prototype = origWS.prototype;
    Object.assign((window as any).WebSocket, origWS);
    console.log('[trace] WS interceptor instalado');
  });

  // Roda 1 passo (T_start_editorial → P_T001 + P_T002 paralelos)
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /próximo passo/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  console.log('Passo 1 clicado, aguardando 60s pra DeepSeek processar P_T001 + P_T002...');
  await page.waitForTimeout(90000);

  // Roda passo 2 (T_process001 → P_T001_out e T_process002 → P_T002_out)
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /próximo passo/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  console.log('Passo 2 clicado, aguardando 30s (places intermediários)...');
  await page.waitForTimeout(30000);

  // Roda passo 3 (T_join003: P_T001_out + P_T002_out → P_T003_in)
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /próximo passo/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  console.log('Passo 3 clicado (JOIN), aguardando 30s...');
  await page.waitForTimeout(30000);

  // Roda passo 4 (T_process003: P_T003_in → P_T003_out, AQUI invoca integrate_suggested_themes)
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /próximo passo/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  console.log('Passo 4 clicado (P_T003_in dispara integrate_suggested_themes), aguardando 90s...');
  await page.waitForTimeout(90000);

  console.log('=== EVENTOS CAPTURADOS ===');
  for (const e of events) console.log(e);

  fs.writeFileSync('/tmp/state-trace.txt', events.join('\n'));
});

/**
 * Teste end-to-end do transit de estado: P1 + P2 → JOIN → P_T003_in (integrate_suggested_themes).
 * Captura input completo de TODAS as chamadas WS para confirmar passagem de dados.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

test('Transit completo: P1+P2 → JOIN → integrate_suggested_themes', async ({ page }) => {
  test.setTimeout(540_000);  // 9 min

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

  // Intercepta WebSocket — loga input COMPLETO de cada execute_task
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
            console.log(`[trace] SEND ${tn} keys=[${keys.join(',')}]`);
            // Log detalhado do input (truncado)
            const inputStr = JSON.stringify(input);
            const preview = inputStr.length > 800 ? inputStr.slice(0,800) + '...[+' + (inputStr.length-800) + 'chars]' : inputStr;
            console.log(`[trace] INPUT ${tn}: ${preview}`);
          }
        } catch {}
        return origSend(data);
      };
      // Hooka onmessage pra logar respostas
      const origAddListener = ws.addEventListener.bind(ws);
      ws.addEventListener = function(type: string, listener: any, ...rest: any[]) {
        if (type === 'message') {
          const wrap = function(ev: MessageEvent) {
            try {
              const r = JSON.parse(ev.data);
              if (r.type === 'task_completed') {
                const res = r.data?.result || {};
                const rstr = JSON.stringify(res);
                console.log(`[trace] DONE ${r.data?.task_name} result_size=${rstr.length} preview=${rstr.slice(0,300)}`);
              }
            } catch {}
            return listener(ev);
          };
          return origAddListener(type, wrap, ...rest);
        }
        return origAddListener(type, listener, ...rest);
      };
      return ws;
    };
    (window as any).WebSocket.prototype = origWS.prototype;
    Object.assign((window as any).WebSocket, origWS);
    console.log('[trace] interceptor instalado');
  });

  async function clickNext(label: string) {
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button')).find((b) =>
        /próximo passo/i.test((b.textContent || '').trim())
      ) as HTMLButtonElement | undefined;
      btn?.click();
    });
    console.log(`>>> ${label} clicado`);
  }

  // Passo 1: T_start_editorial → P_T001 + P_T002 (paralelo)
  await clickNext('Passo 1 — T_start_editorial');
  await page.waitForTimeout(70_000);  // DeepSeek processar P1 e P2

  // Passo 2: T_process001 + T_process002 → P_T001_out + P_T002_out (intermediário, sem WS)
  await clickNext('Passo 2 — T_process001/002 (intermediários)');
  await page.waitForTimeout(8_000);

  // Passo 3: T_join003 → P_T003_in (consume P_T001_out + P_T002_out, dispara integrate_suggested_themes)
  await clickNext('Passo 3 — T_join003 (JOIN: P_T001_out + P_T002_out)');
  await page.waitForTimeout(90_000);  // DeepSeek processar integrate_suggested_themes

  console.log('=== EVENTOS CAPTURADOS ===');
  for (const e of events) console.log(e);

  fs.writeFileSync('/tmp/state-final-trace.txt', events.join('\n'));
  console.log(`Total eventos: ${events.length}. Salvo em /tmp/state-final-trace.txt`);
});

// Roda no browser via Playwright — testa state flow real entre places
import { test, expect } from '@playwright/test';

test('Petri Net: estado flui entre places', async ({ page }) => {
  test.setTimeout(300_000);

  const events = [];
  page.on('console', (m) => {
    const t = m.text();
    if (t.includes('[state-test]')) events.push(t);
  });

  await page.goto('http://localhost:3001');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  // Auto-seleciona projeto
  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]');
    card?.click();
  });
  await page.waitForTimeout(2500);

  // Injeta um observer no window que captura tudo que entra/sai dos places
  await page.evaluate(() => {
    // Hooka WebSocket pra logar os payloads enviados pro ws-server
    const origWS = window.WebSocket;
    window.WebSocket = function(url, ...args) {
      const ws = new origWS(url, ...args);
      const origSend = ws.send.bind(ws);
      ws.send = function(data) {
        try {
          const obj = JSON.parse(data);
          if (obj.type === 'execute_task') {
            const inputKeys = Object.keys(obj.data?.input_data || {});
            console.log(`[state-test] EXECUTE ${obj.data.task_name} input_keys=[${inputKeys.join(',')}]`);
            if (obj.data.task_name === 'sincronização_para_t-003' || inputKeys.includes('sugestoes') || inputKeys.includes('outputs')) {
              console.log(`[state-test] DETAIL ${obj.data.task_name} input=${JSON.stringify(obj.data.input_data).slice(0,600)}`);
            }
          }
        } catch {}
        return origSend(data);
      };
      return ws;
    };
    console.log('[state-test] WS interceptor instalado');
  });

  // Step 1: T0 → dispara 8 places paralelos
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /próximo passo/i.test((b.textContent || '').trim())
    );
    btn?.click();
  });
  console.log('clicou T0, aguardando 60s pra DeepSeek processar P1...');
  await page.waitForTimeout(60000);

  // Step 2: T1 → P3 (sync). Aqui é o teste — P3 vai aguardar P1 (e P2)
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /próximo passo/i.test((b.textContent || '').trim())
    );
    btn?.click();
  });
  console.log('clicou T1 (P3 sync), aguardando 90s...');
  await page.waitForTimeout(90000);

  // Reporta eventos relevantes
  console.log('=== EVENTOS CAPTURADOS ===');
  for (const e of events) console.log(e);
});

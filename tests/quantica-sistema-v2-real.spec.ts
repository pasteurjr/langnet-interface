/**
 * V2 — captura com tempo suficiente pro WebSocket responder (~25s/task DeepSeek).
 */
import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const APP_BASE = 'http://localhost:3001';
const OUT = '/home/pasteurjr/comercial-quantica/sistema/v2/screenshots';

async function clickTab(page: Page, needle: string) {
  await page.evaluate((n: string) => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find((b) => (b.textContent || '').toLowerCase().includes(n.toLowerCase())) as
      | HTMLButtonElement
      | undefined;
    btn?.click();
  }, needle);
  await page.waitForTimeout(900);
}

test.beforeAll(() => { fs.mkdirSync(OUT, { recursive: true }); });

test('Sistema v2: aguarda task completar + outputs reais', async ({ page }) => {
  test.setTimeout(180_000);
  page.on('console', (m) => { if (m.type() === 'error') console.log('[err]', m.text().slice(0, 250)); });

  let step = 10;
  const shot = (label: string) => path.join(OUT, `${String(step++).padStart(2, '0')}-${label}.png`);

  await page.goto(APP_BASE);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  // Auto-seleciona (1 projeto)
  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]') as HTMLElement | null;
    card?.click();
  });
  await page.waitForTimeout(2500);

  // Próximo passo
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /próximo passo/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });

  // Espera o place_done aparecer no log (até 90s)
  let placeDone = false;
  for (let i = 0; i < 30; i++) {
    await page.waitForTimeout(3000);
    const txt = await page.evaluate(() => document.body.textContent || "");
    if (txt.includes("place_done") || txt.includes("place_error")) {
      placeDone = true;
      break;
    }
  }
  console.log('place_done achado:', placeDone);

  await clickTab(page, 'logs');
  await page.screenshot({ path: shot('logs-completo'), fullPage: true });

  await clickTab(page, 'outputs');
  await page.screenshot({ path: shot('outputs-real'), fullPage: true });

  await clickTab(page, 'execução');
  await page.screenshot({ path: shot('execucao-step1-completo'), fullPage: true });
});

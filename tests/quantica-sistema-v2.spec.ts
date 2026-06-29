/**
 * Captura o sistema Quântica v2 (pacote visualtasksexec) rodando.
 * Acessa http://localhost:3001 e percorre as 5 abas.
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

test('Sistema Quântica gerado: tela inicial + 5 abas + executa task', async ({ page }) => {
  test.setTimeout(180_000);
  page.on('console', (m) => { if (m.type() === 'error') console.log('[err]', m.text().slice(0, 200)); });

  let step = 1;
  const shot = (label: string) => path.join(OUT, `${String(step++).padStart(2, '0')}-${label}.png`);

  await page.goto(APP_BASE);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: shot('selector'), fullPage: true });

  // Clica no card do projeto
  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]') as HTMLElement | null;
    card?.click();
  });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: shot('execucao-default'), fullPage: true });

  // Aba Execução: clica "Próximo passo" — vai disparar P1 (que tem token inicial)
  // Mas como P0 (Início do Fluxo) tem 1 token, primeira transição habilitada vai pra P1
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /próximo passo/i.test((b.textContent || '').trim())
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(8000); // espera execução do JS (que faz WS)
  await page.screenshot({ path: shot('apos-step-1'), fullPage: true });

  // Outputs
  await clickTab(page, 'outputs');
  await page.screenshot({ path: shot('outputs'), fullPage: true });

  // Logs
  await clickTab(page, 'logs');
  await page.screenshot({ path: shot('logs'), fullPage: true });

  // Operação (fire isolado)
  await clickTab(page, 'operação');
  await page.screenshot({ path: shot('operacao'), fullPage: true });

  // Inputs
  await clickTab(page, 'inputs');
  await page.screenshot({ path: shot('inputs'), fullPage: true });
});

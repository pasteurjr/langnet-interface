/**
 * Etapa 5 (rerun) — Regenerar Petri Net Quântica usando os YAMLs novos:
 * - agents.yaml session 2d639bdc (15 agentes granulares)
 * - tasks.yaml  session d18d0cb1 (15 tasks com agent: correto)
 */
import { test } from '@playwright/test';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const AGENTS_SESSION_ID = '2d639bdc-1be2-479e-83cf-344d665329c1';
const TASKS_SESSION_ID = 'd18d0cb1-bd0d-4169-aaa2-28fcab716c01';

test('Regenerar Petri Net Quântica (Etapa 5-rerun)', async ({ page }) => {
  test.setTimeout(2400_000);
  await page.setViewportSize({ width: 1920, height: 1080 });

  await page.goto(APP);
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('[1] login OK');

  await page.goto(`${APP}/project/${PROJECT_ID}/petri-net`);
  await page.waitForTimeout(8000);
  await page.screenshot({ path: `${OUT}/etapa5-rerun-01-antes.png`, fullPage: true });

  // Clica em "Gerar Rede"
  const genBtn = page.locator('button:has-text("Gerar Rede")').first();
  await genBtn.waitFor({ state: 'visible', timeout: 15000 });
  await genBtn.click({ force: true });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa5-rerun-02-modal.png`, fullPage: true });
  console.log('[2] modal Gerar Rede aberto');

  // 2 selects — agents.yaml e tasks.yaml
  const selects = page.locator('select');
  const count = await selects.count();
  console.log(`  selects encontrados: ${count}`);

  // Escolhe o session ID por VALUE nos selects
  for (let i = 0; i < count; i++) {
    const sel = selects.nth(i);
    const opts = await sel.locator('option').all();
    for (const opt of opts) {
      const val = await opt.getAttribute('value');
      if (val === AGENTS_SESSION_ID) {
        await sel.selectOption(val);
        console.log(`  [select ${i}] agents.yaml selecionado`);
        break;
      }
      if (val === TASKS_SESSION_ID) {
        await sel.selectOption(val);
        console.log(`  [select ${i}] tasks.yaml selecionado`);
        break;
      }
    }
  }
  await page.waitForTimeout(1000);
  await page.screenshot({ path: `${OUT}/etapa5-rerun-03-selecionados.png`, fullPage: true });

  // Confirma
  const confirmBtn = page.locator('button:has-text("Gerar"), button:has-text("Confirmar")').last();
  await confirmBtn.click({ timeout: 5000, force: true });
  console.log('[3] disparou geração');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa5-rerun-04-gerando.png`, fullPage: true });

  // Aguarda backend
  for (let i = 0; i < 240; i++) {
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => ({
      hasModal: !!document.querySelector('[role="dialog"], .modal-overlay'),
      len: (document.body.textContent || '').length,
    }));
    if (!state.hasModal) {
      console.log(`  ${(i+1)*10}s: modal fechou (LLM terminou)`);
      break;
    }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: aguardando (modal aberto, len=${state.len})`);
  }

  await page.waitForTimeout(5000);
  await page.screenshot({ path: `${OUT}/etapa5-rerun-05-final.png`, fullPage: true });
  console.log('[FIM]');
});

/**
 * Etapa 6 — Code Generation Quântica.
 * Usa agents.yaml (2d639bdc), tasks.yaml corrigido (d18d0cb1) e a Petri
 * Net v2 (persistida em projects.project_data) pra gerar o ws-server
 * completo em Python.
 */
import { test } from '@playwright/test';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const AGENTS_ID = '2d639bdc-1be2-479e-83cf-344d665329c1';
const TASKS_ID = 'd18d0cb1-bd0d-4169-aaa2-28fcab716c01';

test('Gerar Código Quântica (Etapa 6)', async ({ page }) => {
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

  await page.goto(`${APP}/project/${PROJECT_ID}/code-generation`);
  await page.waitForTimeout(8000);
  await page.screenshot({ path: `${OUT}/etapa6-01-inicial.png`, fullPage: true });

  // Clica "⚡ Gerar Código" ou o botão que abre o modal (o texto do botão q abre o modal)
  const genCandidates = ['button:has-text("Gerar Código")', 'button:has-text("Nova Geração")', 'button:has-text("Gerar")'];
  let clicked = false;
  for (const sel of genCandidates) {
    const b = page.locator(sel).first();
    if (await b.count() > 0 && await b.isVisible().catch(() => false)) {
      await b.click({ force: true });
      console.log(`  clicou em ${sel}`);
      clicked = true;
      break;
    }
  }
  if (!clicked) console.log('  ⚠ nenhum botão Gerar encontrado');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa6-02-modal.png`, fullPage: true });
  console.log('[2] modal aberto');

  // Selects: agents/tasks
  const selects = page.locator('select');
  const count = await selects.count();
  console.log(`  selects: ${count}`);
  for (let i = 0; i < count; i++) {
    const sel = selects.nth(i);
    const opts = await sel.locator('option').all();
    for (const opt of opts) {
      const val = await opt.getAttribute('value');
      if (val === AGENTS_ID) { await sel.selectOption(val); console.log(`  [${i}] agents.yaml`); break; }
      if (val === TASKS_ID)  { await sel.selectOption(val); console.log(`  [${i}] tasks.yaml`);  break; }
    }
  }
  await page.waitForTimeout(1000);
  await page.screenshot({ path: `${OUT}/etapa6-03-selecionados.png`, fullPage: true });

  // Confirma
  const confirmBtn = page.locator('button:has-text("Gerar"), button:has-text("Confirmar"), button:has-text("OK")').last();
  await confirmBtn.click({ force: true, timeout: 5000 });
  console.log('[3] disparou geração');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa6-04-gerando.png`, fullPage: true });

  // Aguarda até 30 min pelo modal fechar E árvore de arquivos aparecer
  for (let i = 0; i < 240; i++) {
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const txt = document.body.textContent || '';
      const hasFile = /main\.py|websocket_server\.py|adapters\.py|tools\.py/.test(txt);
      const busy = /⏳ Gerando|Gerando\.\.\./i.test(txt);
      return { hasFile, busy };
    });
    if (state.hasFile && !state.busy) {
      console.log(`  ${(i+1)*10}s: código gerado`);
      break;
    }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: aguardando (busy=${state.busy})`);
  }
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa6-05-final.png`, fullPage: true });
  console.log('[FIM]');
});

/**
 * Etapa 3 do pipeline LangNet — Data Model da Quântica Comercial.
 * A partir da spec gerada na Etapa 2 (73k chars), gera schema SQL,
 * models.py (SQLAlchemy+Pydantic) e migrations Alembic via UI.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const TARGET_SPEC_ID = 'fbc45992-2900-40b5-8867-fc0639f959bc';

test('Gerar Data Model Quântica (Etapa 3)', async ({ page }) => {
  test.setTimeout(2400_000);
  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('[1] login OK');

  await page.goto(`${APP}/project/${PROJECT_ID}/data-model`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/etapa3-01-dm-inicial.png`, fullPage: true });
  console.log('[2] tela Data Model carregada');

  // Tela já tem session ativa: aparece "Regenerar do zero"
  const regBtn = page.locator('button:has-text("Regenerar do zero"), button:has-text("Regenerar")').first();
  const hasRegBtn = await regBtn.count() > 0 && await regBtn.isVisible().catch(() => false);
  console.log(`  tem "Regenerar do zero": ${hasRegBtn}`);

  if (hasRegBtn) {
    // Confirma que quer regenerar (pode abrir modal ou confirm)
    page.once('dialog', d => d.accept());
    await regBtn.click();
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `${OUT}/etapa3-02-regenerar.png`, fullPage: true });
    console.log('[3a] clicou Regenerar');

    // Se abriu select de spec, selecionar a nova
    const specSelect = page.locator('select').first();
    if (await specSelect.count() > 0 && await specSelect.isVisible().catch(() => false)) {
      // Tenta pegar TARGET_SPEC_ID
      const opts = await specSelect.locator('option').all();
      let picked = false;
      for (const opt of opts) {
        const val = await opt.getAttribute('value');
        if (val === TARGET_SPEC_ID) {
          await specSelect.selectOption(val);
          picked = true;
          console.log(`  spec nova selecionada: ${TARGET_SPEC_ID.slice(0,8)}`);
          break;
        }
      }
      if (!picked) {
        const first = await opts[0]?.getAttribute('value');
        if (first) { await specSelect.selectOption(first); console.log(`  (fallback) spec ${first.slice(0,8)}`); }
      }
      await page.waitForTimeout(1000);
      // Clica em Gerar
      const gen = page.locator('button:has-text("Gerar")').first();
      if (await gen.count() > 0 && await gen.isEnabled().catch(() => false)) {
        await gen.click();
        console.log('[3b] clicou Gerar');
      }
    }
  } else {
    // Tela sem session — select direto
    const specSelect = page.locator('select').first();
    if (await specSelect.count() > 0) {
      const opts = await specSelect.locator('option').all();
      for (const opt of opts) {
        const val = await opt.getAttribute('value');
        if (val === TARGET_SPEC_ID) { await specSelect.selectOption(val); break; }
      }
    }
    const gen = page.locator('button:has-text("Gerar")').first();
    await gen.click({ timeout: 5000 });
  }
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa3-03-gerando.png`, fullPage: true });

  // Aguarda até 30 min pra data model completar
  let done = false;
  for (let i = 0; i < 240; i++) {
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const txt = document.body.textContent || '';
      const hasEnts = /entidade|Entidades|Schema SQL|CREATE TABLE/i.test(txt);
      const hasErr = /error|erro no processo|falhou/i.test(txt);
      const geraBtnDisabled = document.querySelector('.dm-btn-primary[disabled]') !== null;
      return { hasEnts, hasErr, geraBtnDisabled, len: txt.length };
    });
    if (state.hasEnts && !state.geraBtnDisabled) {
      done = true;
      console.log(`  ${(i+1)*10}s: data model gerado`);
      break;
    }
    if (state.hasErr && !state.geraBtnDisabled) {
      console.log(`  ${(i+1)*10}s: erro detectado`);
      break;
    }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: aguardando (btn disabled=${state.geraBtnDisabled}, body=${state.len})`);
  }

  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa3-04-gerado.png`, fullPage: true });

  // Screenshots das 5 abas
  const tabs = ['Entidades', 'Schema SQL', 'models.py', 'Alembic', 'YAML'];
  for (let i = 0; i < tabs.length; i++) {
    const tab = page.locator(`button:has-text("${tabs[i]}"), [role="tab"]:has-text("${tabs[i]}")`).first();
    if (await tab.count() > 0 && await tab.isVisible().catch(() => false)) {
      await tab.click().catch(() => {});
      await page.waitForTimeout(1500);
      await page.screenshot({ path: `${OUT}/etapa3-05-aba-${i+1}-${tabs[i].replace(/[^\w]/g,'_')}.png`, fullPage: true });
      console.log(`  screenshot aba: ${tabs[i]}`);
    }
  }

  console.log('[FIM]');
});

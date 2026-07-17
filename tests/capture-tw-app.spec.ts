import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3001';
const OUT = '/tmp/quantica-tw-app/shots';

test.use({ viewport: { width: 1500, height: 950 } });

test('App Quântica Tailwind — captura + cadastro', async ({ page }) => {
  test.setTimeout(120_000);
  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForTimeout(4000);
  await page.screenshot({ path: `${OUT}/01-home-persona.png`, fullPage: true });

  // Dashboard de métricas
  const metricas = page.locator('text=/Métricas/').first();
  if (await metricas.count() > 0) {
    await metricas.click().catch(() => {});
    await page.waitForTimeout(2500);
    await page.screenshot({ path: `${OUT}/02-metricas.png`, fullPage: true });
  }

  // Volta pra Cadastro de Persona e submete
  const personas = page.locator('aside >> text=/Persona/').first();
  if (await personas.count() > 0) {
    await personas.click().catch(() => {});
    await page.waitForTimeout(1500);
  }
  const nome = page.locator('input').first();
  await nome.fill(`Persona Tailwind ${Date.now()} — CMO`);
  const fillLabel = async (l: string, v: string) => {
    const lab = page.locator(`label:has-text("${l}")`).first();
    if (await lab.count() > 0) {
      const el = lab.locator('xpath=following-sibling::*[self::input or self::textarea][1]').first();
      if (await el.count() > 0) await el.fill(v);
    }
  };
  await fillLabel('Canais', 'linkedin, instagram');
  await fillLabel('Problemas', 'aquisição cara');
  await fillLabel('Palavras', 'growth, brand');
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT}/03-form-preenchido.png`, fullPage: true });

  const salvar = page.locator('button:has-text("Salvar")').first();
  await salvar.click();
  await page.waitForTimeout(4000);
  await page.screenshot({ path: `${OUT}/04-resultado.png`, fullPage: true });
});

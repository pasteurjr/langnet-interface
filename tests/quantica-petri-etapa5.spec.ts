/**
 * Etapa 5 do pipeline LangNet — Petri Net da Quântica Comercial.
 * Abre a tela do Petri Net Editor, aguarda o canvas renderizar, captura
 * screenshots do editor com o diagrama, das listas de places/transitions
 * e do painel lateral se houver.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

test('Petri Net Quântica (Etapa 5)', async ({ page }) => {
  test.setTimeout(180_000);
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

  await page.goto(`${APP}/project/${PROJECT_ID}/petri-net`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(10000); // dá tempo pro canvas/JointJS renderizar
  await page.screenshot({ path: `${OUT}/etapa5-01-petri-inicial.png`, fullPage: true });
  console.log('[2] tela Petri carregada');

  // Zoom out se o diagrama for grande
  const zoomOut = page.locator('button[title*="zoom" i], button:has-text("−"), button:has-text("-")').first();
  if (await zoomOut.count() > 0) {
    for (let i = 0; i < 3; i++) {
      await zoomOut.click().catch(() => {});
      await page.waitForTimeout(500);
    }
  }
  await page.screenshot({ path: `${OUT}/etapa5-02-petri-overview.png`, fullPage: true });
  console.log('[3] screenshot com zoom out');

  // Se tem "Fit to screen" ou similar
  const fitBtn = page.locator('button[title*="fit" i], button:has-text("Fit"), button:has-text("Ajustar")').first();
  if (await fitBtn.count() > 0) {
    await fitBtn.click().catch(() => {});
    await page.waitForTimeout(1500);
  }
  await page.screenshot({ path: `${OUT}/etapa5-03-petri-fit.png`, fullPage: true });

  // Se tem painel de detalhes ou sidebar
  const sidebar = page.locator('[class*="sidebar"], [class*="panel"], aside').first();
  if (await sidebar.count() > 0 && await sidebar.isVisible().catch(() => false)) {
    await page.screenshot({ path: `${OUT}/etapa5-04-sidebar.png`, fullPage: true });
  }

  // Screenshot do documento se houver botão para vê-lo
  const docBtn = page.locator('button:has-text("Documento"), button:has-text("Detalhes"), button:has-text("Descrição"), button:has-text("Info")').first();
  if (await docBtn.count() > 0 && await docBtn.isVisible().catch(() => false)) {
    await docBtn.click().catch(() => {});
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${OUT}/etapa5-05-documento.png`, fullPage: true });
    console.log('[4] documento aberto');
  }

  // Scroll pra ver tudo
  await page.evaluate(() => window.scrollBy(0, 500));
  await page.waitForTimeout(1000);
  await page.screenshot({ path: `${OUT}/etapa5-06-scroll1.png`, fullPage: true });
  await page.evaluate(() => window.scrollBy(0, 1000));
  await page.waitForTimeout(1000);
  await page.screenshot({ path: `${OUT}/etapa5-07-scroll2.png`, fullPage: true });

  console.log('[FIM]');
});

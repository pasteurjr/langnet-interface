/**
 * Abre a spec do Uso do Solo (session 652cd1ef) via UI e baixa o PDF
 * usando o botão real de exportação. Salva o PDF no OUT.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/uso-solo';
const PROJECT_ID = 'a1391183-f348-4a78-8773-8046b90a7676';
const SPEC_SESSION_ID = '652cd1ef-20ff-47a9-b9b3-4cbadf53149f';

test('Baixa PDF da spec Uso do Solo via UI', async ({ page, context }) => {
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

  // Vai pra spec
  await page.goto(`${APP}/project/${PROJECT_ID}/spec`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/spec-01-lista.png`, fullPage: true });
  console.log('[2] tela spec');

  // Tenta abrir a session específica se aparecer lista
  const sessionLoc = page.locator(`text=${SPEC_SESSION_ID.substring(0,8)}`).first();
  const clickTargets = [
    page.locator('button:has-text("Ver documento")'),
    page.locator('button:has-text("Visualizar")'),
    page.locator('button:has-text("Abrir")'),
    page.locator('a:has-text("Ver")'),
  ];
  for (const t of clickTargets) {
    if (await t.count() > 0 && await t.first().isVisible().catch(() => false)) {
      await t.first().click().catch(() => {});
      await page.waitForTimeout(3000);
      break;
    }
  }

  await page.screenshot({ path: `${OUT}/spec-02-conteudo.png`, fullPage: true });
  const chars = await page.evaluate(() => (document.body.textContent || '').length);
  console.log(`[3] body ${chars} chars`);

  // Procura botão PDF
  const pdfBtnSelectors = [
    'button:has-text("PDF")',
    'button:has-text("Baixar PDF")',
    'button:has-text("Download PDF")',
    'button:has-text("Exportar PDF")',
    'button:has-text("📄")',
  ];

  // Aguarda evento download
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 120_000 }).catch(() => null),
    (async () => {
      for (const sel of pdfBtnSelectors) {
        const btn = page.locator(sel).first();
        if (await btn.count() > 0 && await btn.isVisible().catch(() => false)) {
          console.log(`  clicou em: ${sel}`);
          await btn.click();
          return;
        }
      }
      console.log('  nenhum botão PDF direto — vou printar HTML do topo');
      const html = await page.evaluate(() => document.body.innerHTML.substring(0, 3000));
      console.log(html);
    })(),
  ]);

  if (download) {
    const dest = path.join(OUT, 'especificacao-uso-solo.pdf');
    await download.saveAs(dest);
    console.log(`[4] PDF salvo em ${dest}`);
  } else {
    console.log('[4] sem download detectado');
  }

  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${OUT}/spec-03-final.png`, fullPage: true });
});

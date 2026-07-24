/**
 * Capturas panorâmicas do editor de Petri Net da Quântica.
 * Faz zoom out máximo + screenshots + pan pra cobrir a rede toda.
 */
import { test } from '@playwright/test';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

test('Petri Net - captura panorâmica', async ({ page }) => {
  test.setTimeout(180_000);
  // Viewport maior pra caber mais no screenshot
  await page.setViewportSize({ width: 1920, height: 1080 });

  await page.goto(APP);
  await page.waitForTimeout(2500);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);

  await page.goto(`${APP}/project/${PROJECT_ID}/petri-net`);
  await page.waitForTimeout(10000);

  // Screenshot 1: viewport ampla, sem zoom
  await page.screenshot({ path: `${OUT}/etapa5-01-inicial.png`, fullPage: true });

  // Zoom out — atalho de teclado ou wheel
  const canvas = page.locator('svg, canvas, .joint-paper').first();
  if (await canvas.count() > 0) {
    const box = await canvas.boundingBox().catch(() => null);
    if (box) {
      const cx = box.x + box.width/2, cy = box.y + box.height/2;
      // 8× ctrl+wheel down (zoom out)
      for (let i = 0; i < 8; i++) {
        await page.mouse.move(cx, cy);
        await page.keyboard.down('Control');
        await page.mouse.wheel(0, 300);
        await page.keyboard.up('Control');
        await page.waitForTimeout(200);
      }
    }
  }
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${OUT}/etapa5-02-zoom-out.png`, fullPage: true });

  // Pan pro início (canto superior esquerdo)
  await page.keyboard.press('Home').catch(() => {});
  // Ou usa drag do canvas se possível
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${OUT}/etapa5-03-overview.png`, fullPage: true });

  // Se tem botão "Fit" ou zoom-fit
  const fitBtn = page.locator('button[title*="Fit" i], button[title*="Ajustar" i], button:has-text("Fit"), button:has-text("⛶")').first();
  if (await fitBtn.count() > 0) {
    await fitBtn.click().catch(() => {});
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${OUT}/etapa5-04-fit.png`, fullPage: true });
  }
});

import { test } from '@playwright/test';
const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

test('Screenshot final Etapa 4', async ({ page }) => {
  test.setTimeout(120_000);
  await page.goto(APP);
  await page.waitForTimeout(2500);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  await page.goto(`${APP}/project/${PROJECT_ID}/agent-task`);
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/etapa4-05-final.png`, fullPage: true });
  // Scroll pra pegar mais
  await page.evaluate(() => window.scrollBy(0, 1000));
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${OUT}/etapa4-06-agents.png`, fullPage: true });
  await page.evaluate(() => window.scrollBy(0, 2000));
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${OUT}/etapa4-07-tasks.png`, fullPage: true });
  await page.evaluate(() => window.scrollBy(0, 3000));
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${OUT}/etapa4-08-rastreabilidade.png`, fullPage: true });
});

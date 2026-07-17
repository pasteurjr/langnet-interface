import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/tmp/uso-solo-pipeline/uispec-page-shots';
const PROJ = 'b55ef718-0073-44d4-b279-11df89403e92';

test('Captura UISpecPage no LangNet', async ({ page }) => {
  test.setTimeout(120_000);
  await page.setViewportSize({ width: 1600, height: 1000 });
  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(2000);

  // Vai direto pra etapa nova
  await page.goto(`${APP}/project/${PROJ}/ui-spec`);
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/01-uispec-page.png`, fullPage: true });

  // Clica em algumas telas da lista para mostrar preview do mockup
  const items = page.locator('.uispec-item');
  const n = await items.count();
  for (let i = 0; i < Math.min(n, 4); i++) {
    await items.nth(i).click().catch(() => {});
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${OUT}/02-preview-${i}.png`, fullPage: true });
  }
});

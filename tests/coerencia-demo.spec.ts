import { test } from '@playwright/test';
const OUT='/tmp/uso-solo-pipeline/shots-coerencia';
test('coerencia', async ({ page }) => {
  test.setTimeout(60000);
  await page.setViewportSize({ width: 1500, height: 1000 });
  await page.goto('http://localhost:3001', { waitUntil:'networkidle', timeout:45000 }).catch(()=>{});
  await page.waitForTimeout(5000);
  await page.screenshot({ path:`${OUT}/01-personas-com-dados.png` });
  console.log('[shot] home');
});

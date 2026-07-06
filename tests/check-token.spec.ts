import { test } from '@playwright/test';

test('check localStorage token key após login', async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForTimeout(4000);

  const storage = await page.evaluate(() => {
    const all: any = {};
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i)!;
      const v = localStorage.getItem(k) || '';
      all[k] = v.length > 60 ? v.slice(0, 60) + '...' : v;
    }
    return all;
  });
  console.log('localStorage keys/values:', JSON.stringify(storage, null, 2));
});

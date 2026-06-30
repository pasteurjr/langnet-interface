import { test } from '@playwright/test';
import * as fs from 'fs';

test('debug visual', async ({ page }) => {
  test.setTimeout(60_000);

  page.on('console', (m) => {
    console.log(`[${m.type()}]`, m.text().slice(0, 300));
  });
  page.on('pageerror', (e) => {
    console.log('[PAGE ERROR]', e.message.slice(0, 400));
  });

  await page.goto('http://localhost:3001');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  await page.screenshot({ path: '/tmp/debug-1.png', fullPage: true });

  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]') as HTMLElement | null;
    card?.click();
  });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/debug-2.png', fullPage: true });

  // Verifica se há erro visível
  const txt = await page.evaluate(() => document.body.textContent || '');
  console.log('=== Body text (first 500) ===');
  console.log(txt.slice(0, 500));
});

import { test } from '@playwright/test';

test('inspecionar tela de login', async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(4000);
  const inspect = await page.evaluate(() => {
    const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
      type: i.type, name: i.name, id: i.id, placeholder: i.placeholder, cls: i.className.slice(0, 60)
    }));
    const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
      text: (b.textContent||'').trim().slice(0,50), cls: b.className.slice(0,60)
    }));
    return { url: location.href, title: document.title, inputs, buttons, body_preview: (document.body.textContent||'').slice(0, 400) };
  });
  console.log(JSON.stringify(inspect, null, 2));
});

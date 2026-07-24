import { test } from '@playwright/test';

test('login debug', async ({ page }) => {
  test.setTimeout(60_000);

  // captura requests XHR
  page.on('response', r => {
    if (r.url().includes('/api/')) {
      console.log(`  [${r.status()}] ${r.request().method()} ${r.url()}`);
    }
  });

  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  console.log('URL antes login:', page.url());

  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.screenshot({ path: '/tmp/login-preenchido.png' });

  // Múltiplas estratégias de click
  const btn = page.locator('button:has-text("Entrar")').first();
  await btn.click();
  console.log('Click 1 feito');
  await page.waitForTimeout(3500);
  console.log('URL após click 1:', page.url());
  await page.screenshot({ path: '/tmp/login-apos-click1.png' });

  // Se ainda estiver na tela de login, tenta pressionar Enter
  if (page.url().includes('/login')) {
    console.log('Ainda no login, tentando Enter…');
    await page.locator('#password').press('Enter');
    await page.waitForTimeout(3500);
    console.log('URL após Enter:', page.url());
    await page.screenshot({ path: '/tmp/login-apos-enter.png' });
  }

  // Verifica localStorage
  const storage = await page.evaluate(() => ({
    keys: Object.keys(localStorage),
    token: localStorage.getItem('access_token') || localStorage.getItem('token'),
  }));
  console.log('localStorage:', JSON.stringify(storage));

  // Se logou, tenta ir pro projeto
  if (!page.url().includes('/login')) {
    await page.goto('http://localhost:3000/projects/b55ef718-0073-44d4-b279-11df89403e92');
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(4000);
    await page.screenshot({ path: '/tmp/projeto-quantica.png' });
    const preview = await page.evaluate(() => (document.body.textContent || '').slice(0, 500));
    console.log('Preview projeto:', preview);
  }
});

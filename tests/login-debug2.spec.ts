import { test } from '@playwright/test';

test('login debug 2', async ({ page }) => {
  test.setTimeout(60_000);

  page.on('console', m => console.log('  [console]', m.type(), m.text().slice(0,200)));
  page.on('pageerror', e => console.log('  [pageerror]', e.message));
  page.on('request', r => {
    if (r.url().includes('/api/') || r.url().includes(':8000')) console.log(`  [→] ${r.method()} ${r.url()}`);
  });

  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);

  // Inspeção do form
  const inspect = await page.evaluate(() => {
    const email = document.querySelector('#email') as HTMLInputElement;
    const pw = document.querySelector('#password') as HTMLInputElement;
    const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent?.includes('Entrar')) as HTMLButtonElement;
    const form = btn?.closest('form') as HTMLFormElement | null;
    return {
      email_id: email?.id, email_name: email?.name,
      pw_id: pw?.id,
      btn_type: btn?.type, btn_disabled: btn?.disabled, btn_form: btn?.form?.id,
      form_action: form?.action, form_method: form?.method, form_onsubmit: form?.getAttribute('onsubmit'),
    };
  });
  console.log('form inspect:', JSON.stringify(inspect, null, 2));

  // Preenchimento via evento nativo (não só .fill que envia via node)
  await page.locator('#email').click();
  await page.keyboard.type('teste@teste.com', { delay: 30 });
  await page.locator('#password').click();
  await page.keyboard.type('buceta123', { delay: 30 });
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/tmp/login-typed.png' });

  // Confirma valor atual
  const values = await page.evaluate(() => ({
    email: (document.querySelector('#email') as HTMLInputElement).value,
    pw: (document.querySelector('#password') as HTMLInputElement).value,
  }));
  console.log('valores nos campos:', JSON.stringify(values));

  // Click Entrar
  await page.locator('button:has-text("Entrar")').first().click();
  console.log('Click Entrar OK');
  await page.waitForTimeout(6000);
  console.log('URL após click:', page.url());
  const storage = await page.evaluate(() => ({
    keys: Object.keys(localStorage),
    session_keys: Object.keys(sessionStorage),
  }));
  console.log('storage após:', JSON.stringify(storage));
});

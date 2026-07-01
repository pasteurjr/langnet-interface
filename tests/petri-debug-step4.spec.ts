import { test } from '@playwright/test';

test('debug step 4: T_join003 apta?', async ({ page }) => {
  test.setTimeout(360_000);
  page.on('console', (m) => {
    const t = m.text();
    if (t.includes('🛡️') || t.includes('✅') || t.includes('❌') || t.includes('🔥') ||
        t.includes('place_done') || t.includes('place_start') || t.includes('🔍') ||
        t.includes('ERROR') || t.includes('Error')) {
      console.log(`[${m.type()}]`, t.slice(0, 250));
    }
  });
  page.on('pageerror', (e) => console.log('[PAGE ERR]', e.message.slice(0,300)));

  await page.goto('http://localhost:3001');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]') as HTMLElement | null;
    card?.click();
  });
  await page.waitForTimeout(2500);

  async function clickNext() {
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button')).find((b) =>
        /próximo passo/i.test((b.textContent || '').trim())
      ) as HTMLButtonElement | undefined;
      btn?.click();
    });
  }

  console.log('>>> Passo 1');
  await clickNext();
  await page.waitForTimeout(100000); // 100s pra P_T001+P_T002 terminarem WS

  console.log('>>> Passo 2 (T_process001)');
  await clickNext();
  await page.waitForTimeout(8000);

  console.log('>>> Passo 3 (T_process002)');
  await clickNext();
  await page.waitForTimeout(8000);

  // Checa quem está apta
  const enabled = await page.evaluate(() => {
    const ml = document.body.textContent || '';
    const m = ml.match(/Habilitadas:\s*(\d+)/);
    return m ? m[1] : '?';
  });
  console.log('Habilitadas antes do passo 4:', enabled);

  console.log('>>> Passo 4 (T_join003?)');
  await clickNext();
  await page.waitForTimeout(120000);

  const finalState = await page.evaluate(() => {
    const m1 = (document.body.textContent || '').match(/Eventos:\s*(\d+)/);
    const m2 = (document.body.textContent || '').match(/Step:\s*(\d+)/);
    return `Eventos=${m1?.[1]} Step=${m2?.[1]}`;
  });
  console.log('Estado final:', finalState);
});

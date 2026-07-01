import { test } from '@playwright/test';

test('Inspect place outputs via _petriSim', async ({ page }) => {
  test.setTimeout(500_000);

  await page.goto('http://localhost:3001');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    const card = document.querySelector('div[style*="cursor: pointer"]') as HTMLElement | null;
    card?.click();
  });
  await page.waitForTimeout(3000);

  async function clickNext() {
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button')).find((b) =>
        /próximo passo/i.test((b.textContent || '').trim())
      ) as HTMLButtonElement | undefined;
      btn?.click();
    });
  }

  // Confirma simulator exposto
  const has = await page.evaluate(() => Boolean((window as any)._petriSim));
  console.log('_petriSim disponível:', has);

  console.log('>>> Passo 1');
  await clickNext();
  await page.waitForTimeout(100000);

  // Snapshot 1: output_data de P_T001 e P_T002
  const snap1 = await page.evaluate(() => {
    const sim = (window as any)._petriSim;
    const p1 = sim.petriNet.lugares.find((p: any) => p.id === 'P_T001');
    const p2 = sim.petriNet.lugares.find((p: any) => p.id === 'P_T002');
    return {
      P_T001: { tokens: sim.markingVector.P_T001, out_keys: Object.keys(p1?.output_data || {}), has_suggest: 'outputs' in (p1?.output_data || {}) },
      P_T002: { tokens: sim.markingVector.P_T002, out_keys: Object.keys(p2?.output_data || {}), has_cal: 'outputs' in (p2?.output_data || {}) },
    };
  });
  console.log('SNAP após P1:', JSON.stringify(snap1));

  console.log('>>> Passo 2 (T_process001)');
  await clickNext();
  await page.waitForTimeout(15000);

  const snap2 = await page.evaluate(() => {
    const sim = (window as any)._petriSim;
    const p = sim.petriNet.lugares.find((p: any) => p.id === 'P_T001_out');
    return {
      P_T001_out_tokens: sim.markingVector.P_T001_out,
      P_T001_out_out_keys: Object.keys(p?.output_data || {}),
      P_T001_out_has_outputs: !!(p?.output_data?.outputs),
      P_T001_out_outputs_keys: Object.keys(p?.output_data?.outputs || {}),
    };
  });
  console.log('SNAP após P2:', JSON.stringify(snap2));

  console.log('>>> Passo 3');
  await clickNext();
  await page.waitForTimeout(15000);

  console.log('>>> Passo 4 (T_join003)');
  await clickNext();
  await page.waitForTimeout(180000);

  const snap4 = await page.evaluate(() => {
    const sim = (window as any)._petriSim;
    const p = sim.petriNet.lugares.find((p: any) => p.id === 'P_T003_in');
    const p2 = sim.petriNet.lugares.find((p: any) => p.id === 'P_T002_out');
    return {
      P_T002_out_outputs_keys: Object.keys((p2?.output_data?.outputs) || {}),
      P_T003_in_input_keys: Object.keys(p?.input_data || {}),
      P_T003_in_output_keys: Object.keys(p?.output_data || {}),
      P_T003_in_output_outputs: Object.keys((p?.output_data?.outputs) || {}),
    };
  });
  console.log('SNAP após P4:', JSON.stringify(snap4));
});

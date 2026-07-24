import { test } from '@playwright/test';
const APP='http://localhost:3000';
const OUT='/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const P='b55ef718-0073-44d4-b279-11df89403e92';
const AG='74c29bb8-3dae-4cfd-b7a2-c9f14aea47f1';
const TK='80c8044c-f9ab-4612-b984-b8ccca380a00';
test('CodeGen v2', async ({page})=>{
  test.setTimeout(1800_000);
  await page.setViewportSize({width:1920,height:1080});
  await page.goto(APP); await page.waitForTimeout(2500);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(()=>!location.pathname.includes('/login'),{timeout:15000});
  await page.waitForTimeout(3000);
  await page.goto(`${APP}/project/${P}/code-generation`);
  await page.waitForTimeout(8000);
  const gb = page.locator('button:has-text("Gerar Código")').first();
  await gb.click({force:true, timeout:5000});
  await page.waitForTimeout(3000);
  const sel = page.locator('select');
  const n = await sel.count();
  for (let i=0; i<n; i++) {
    const s = sel.nth(i);
    const opts = await s.locator('option').all();
    for (const o of opts) {
      const v = await o.getAttribute('value');
      if (v === AG || v === TK) { await s.selectOption(v); break; }
    }
  }
  await page.waitForTimeout(1500);
  const conf = page.locator('button:has-text("Gerar")').last();
  await conf.click({force:true, timeout:5000});
  console.log('disparado');
  await page.waitForTimeout(120000);
});

import { test } from '@playwright/test';
const APP='http://localhost:3000';
const OUT='/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const P='b55ef718-0073-44d4-b279-11df89403e92';
test('Gerar agents.yaml v2', async ({page})=>{
  test.setTimeout(1800_000);
  await page.setViewportSize({width:1920,height:1080});
  await page.goto(APP); await page.waitForTimeout(2500);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(()=>!location.pathname.includes('/login'),{timeout:15000});
  await page.waitForTimeout(3000);
  await page.goto(`${APP}/project/${P}/yaml-generation`);
  await page.waitForTimeout(6000);
  const abaAg = page.locator('button:has-text("Agents YAML")').first();
  if (await abaAg.count() > 0) { await abaAg.click(); await page.waitForTimeout(1500); }
  await page.locator('button:has-text("Doc MD")').first().click();
  await page.waitForTimeout(2500);
  await page.screenshot({path:`${OUT}/4b-v2-01-modal.png`,fullPage:true});
  // Nova session é a primeira (mais recente)
  const verVer = page.locator('text=/Clique para ver vers/i').first();
  await verVer.click({force:true, timeout:15000});
  await page.waitForTimeout(2500);
  const v1 = page.locator('text=/Versão\\s*1/').first();
  await v1.click({force:true, timeout:15000});
  await page.waitForTimeout(3000);
  const genBtn = page.locator('button:has-text("Gerar agents.yaml")').first();
  await genBtn.click({force:true, timeout:5000});
  console.log('disparado');
  await page.waitForTimeout(3000);
  for (let i=0; i<180; i++) {
    await page.waitForTimeout(10000);
    const busy = await page.evaluate(()=> /⏳ Gerando/i.test(document.body.textContent||''));
    if (!busy) { console.log(`${(i+1)*10}s: pronto`); break; }
  }
  await page.screenshot({path:`${OUT}/4b-v2-02-final.png`,fullPage:true});
});

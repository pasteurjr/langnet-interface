import { test } from '@playwright/test';
const APP='http://localhost:3000';
const OUT='/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const P='b55ef718-0073-44d4-b279-11df89403e92';
test('scr tasks', async ({page})=>{
  test.setTimeout(120_000);
  await page.goto(APP); await page.waitForTimeout(2500);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(()=>!location.pathname.includes('/login'),{timeout:15000});
  await page.waitForTimeout(3000);
  await page.goto(`${APP}/project/${P}/yaml-generation`);
  await page.waitForTimeout(4000);
  const abaTasks = page.locator('button:has-text("Tasks YAML")').first();
  if (await abaTasks.count() > 0) { await abaTasks.click(); await page.waitForTimeout(2500); }
  await page.screenshot({path:`${OUT}/etapa4c-06-final-fixed.png`,fullPage:true});
});

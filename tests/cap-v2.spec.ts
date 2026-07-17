import { test } from '@playwright/test';
const APP='http://localhost:3001'; const OUT='/tmp/quantica-v2/shots';
import * as fs from 'fs';
test.use({viewport:{width:1440,height:900}});
test('v2 crud botoes + view + menu', async ({page})=>{
  test.setTimeout(90000);
  fs.mkdirSync(OUT,{recursive:true});
  await page.goto(APP); await page.waitForTimeout(4500);
  await page.screenshot({path:`${OUT}/01-lista-botoes.png`, fullPage:false});
  // clica Ver na primeira linha
  const ver=page.locator('button:has-text("Ver")').first();
  if(await ver.count()>0){ await ver.click(); await page.waitForTimeout(2500); await page.screenshot({path:`${OUT}/02-visualizar.png`, fullPage:false}); }
});

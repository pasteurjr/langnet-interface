import { test } from '@playwright/test';
const APP='http://localhost:3001'; const OUT='/tmp/quantica-v2/shots';
import * as fs from 'fs';
test.use({viewport:{width:1440,height:900}});
test('v2 lista+ver', async ({page})=>{
  test.setTimeout(90000);
  fs.mkdirSync(OUT,{recursive:true});
  await page.goto(APP); await page.waitForTimeout(5000);
  await page.screenshot({path:`${OUT}/01-lista-botoes.png`, fullPage:false});
  const ver=page.locator('button', {hasText:'Ver'}).first();
  if(await ver.count()>0){ await ver.click(); await page.waitForTimeout(2500); await page.screenshot({path:`${OUT}/02-visualizar.png`, fullPage:false}); }
  else { await page.screenshot({path:`${OUT}/02-nover.png`, fullPage:false}); }
});

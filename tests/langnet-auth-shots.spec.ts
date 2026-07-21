import { test } from '@playwright/test';
const BASE='http://localhost:3000';
const OUT='/tmp/uso-solo-pipeline/shots-app';
test('auth shots', async ({ page }) => {
  await page.setViewportSize({ width: 1600, height: 1000 });
  for (const [n,p] of [['g_login','/login'],['g_register','/register']] as [string,string][]) {
    await page.goto(BASE+p,{waitUntil:'networkidle',timeout:30000}).catch(()=>{});
    await page.waitForTimeout(2500);
    await page.screenshot({path:`${OUT}/${n}.png`,fullPage:true}).catch(()=>{});
    console.log('[shot]',n);
  }
});

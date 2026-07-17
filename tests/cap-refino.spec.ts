import { test } from '@playwright/test';
const APP='http://localhost:3000';
const PROJ='b55ef718-0073-44d4-b279-11df89403e92';
test.use({viewport:{width:1600,height:1000}});
test('refino visivel', async ({page}) => {
  test.setTimeout(60000);
  await page.goto(APP); await page.waitForTimeout(2500);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(()=>!location.pathname.includes('/login'),{timeout:15000});
  await page.goto(`${APP}/project/${PROJ}/ui-spec`); await page.waitForTimeout(6000);
  // clica na primeira tela (persona)
  await page.locator('.uispec-item').first().click().catch(()=>{});
  await page.waitForTimeout(2500);
  await page.screenshot({path:'/tmp/uso-solo-pipeline/refino-langnet.png',fullPage:true});
});

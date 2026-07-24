import { test } from '@playwright/test';
import * as fs from 'fs';
const TOK = fs.readFileSync('/tmp/uso-solo-pipeline/tok.txt','utf8').trim();
const PID='b55ef718-0073-44d4-b279-11df89403e92';
test('mcp proj', async ({ page }) => {
  test.setTimeout(60000);
  await page.addInitScript((t)=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOK);
  await page.setViewportSize({ width: 1500, height: 1200 });
  await page.goto(`http://localhost:3000/project/${PID}/mcp`, { waitUntil:'networkidle', timeout:45000 }).catch(()=>{});
  await page.waitForTimeout(4000);
  // clica "Sugerir atribuições"
  await page.getByText('Sugerir atribuições', {exact:false}).first().click().catch(()=>{});
  await page.waitForTimeout(2500);
  await page.screenshot({ path:'/tmp/uso-solo-pipeline/shots-mcp/02-mcp-projeto.png' });
  console.log('[shot] mcp-projeto');
});

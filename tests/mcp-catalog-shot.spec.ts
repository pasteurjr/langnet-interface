import { test } from '@playwright/test';
import * as fs from 'fs';
const TOK = fs.readFileSync('/tmp/uso-solo-pipeline/tok.txt','utf8').trim();
test('mcp cat', async ({ page }) => {
  test.setTimeout(60000);
  await page.addInitScript((t)=>{ localStorage.setItem('accessToken',t); localStorage.setItem('token',t); }, TOK);
  await page.setViewportSize({ width: 1500, height: 1300 });
  await page.goto('http://localhost:3000/mcp/config', { waitUntil:'networkidle', timeout:45000 }).catch(()=>{});
  await page.waitForTimeout(4500);
  await page.screenshot({ path:'/tmp/uso-solo-pipeline/shots-mcp/03-catalogo.png' });
  console.log('[shot] catalogo');
});

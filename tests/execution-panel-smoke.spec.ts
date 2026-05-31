import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';

const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'execution-panel');

let stepIdx = 1;
const ts = (label: string) => path.join(OUT, `${String(stepIdx++).padStart(2, '0')}-${label}.png`);

async function login(page: Page) {
  const res = await page.request.post(`${API_BASE}/auth/login`, {
    data: { email: EMAIL, password: PASSWORD },
    headers: { 'Content-Type': 'application/json' },
  });
  const body = await res.json();
  await page.goto(`${APP_BASE}/login`);
  await page.evaluate(([t, u]) => {
    localStorage.setItem('accessToken', t);
    localStorage.setItem('token', t);
    localStorage.setItem('user', JSON.stringify(u));
  }, [body.access_token, body.user]);
}

test.beforeAll(() => { fs.mkdirSync(OUT, { recursive: true }); });

test('ExecutionPanel: monta 5 abas e tenta conexão (sem servidor real)', async ({ page }) => {
  test.setTimeout(120_000);
  page.on('dialog', async (d) => { await d.accept().catch(() => {}); });

  await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4000);
  await page.screenshot({ path: ts('petri-net-page'), fullPage: true });

  // 1) Clica botão "Execução Real"
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /execu[çc][ãa]o real/i.test(b.textContent || '')) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: ts('panel-opened'), fullPage: true });

  // 2) Confere as 5 abas
  const tabsFound = await page.evaluate(() => {
    const labels = Array.from(document.querySelectorAll('button')).map(b => (b.textContent || '').trim());
    return {
      operacao: labels.some(l => /opera[çc][ãa]o/i.test(l)),
      execucao: labels.some(l => /execu[çc][ãa]o/i.test(l) && !/real/i.test(l)),
      inputs: labels.some(l => /inputs/i.test(l)),
      outputs: labels.some(l => /outputs/i.test(l)),
      logs: labels.some(l => /logs/i.test(l)),
    };
  });
  console.log('Abas encontradas:', tabsFound);
  expect(tabsFound.operacao, 'aba Operação').toBeTruthy();
  expect(tabsFound.execucao, 'aba Execução').toBeTruthy();
  expect(tabsFound.inputs, 'aba Inputs').toBeTruthy();
  expect(tabsFound.outputs, 'aba Outputs').toBeTruthy();
  expect(tabsFound.logs, 'aba Logs').toBeTruthy();

  // 3) Confere botão Conectar e badge DESCONECTADO
  const hasConnect = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button'))
      .some((b) => /^conectar$/i.test((b.textContent || '').trim()));
  });
  expect(hasConnect, 'botão Conectar').toBeTruthy();

  const hasBadge = await page.evaluate(() => {
    return (document.body.textContent || '').includes('DESCONECTADO');
  });
  expect(hasBadge, 'badge DESCONECTADO').toBeTruthy();

  // 4) Tenta conectar — vai falhar (sem servidor), mas confirma o fluxo
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /^conectar$/i.test((b.textContent || '').trim())) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('after-connect-attempt'), fullPage: true });

  const finalStatus = await page.evaluate(() => {
    const txt = document.body.textContent || '';
    return {
      hasError: txt.includes('ERRO'),
      hasDisconnected: txt.includes('DESCONECTADO'),
      hasConnected: txt.includes('CONECTADO') && !txt.includes('DESCONECTADO'),
    };
  });
  console.log('Status after connect attempt:', finalStatus);
  // sem servidor o status fica em error ou disconnected
  expect(finalStatus.hasConnected, 'não deveria conectar sem servidor').toBeFalsy();

  // 5) Troca para cada aba e tira screenshot
  for (const tab of ['Operação', 'Inputs', 'Outputs', 'Logs', 'Execução']) {
    await page.evaluate((label) => {
      const re = new RegExp(label, 'i');
      const tabBtn = Array.from(document.querySelectorAll('button'))
        .filter((b) => !/real|conectar|desconectar|×|executar/i.test(b.textContent || ''))
        .find((b) => re.test(b.textContent || '')) as HTMLButtonElement | undefined;
      tabBtn?.click();
    }, tab);
    await page.waitForTimeout(400);
    await page.screenshot({ path: ts(`tab-${tab.toLowerCase().replace(/[çã]/g,'')}`), fullPage: true });
  }
});

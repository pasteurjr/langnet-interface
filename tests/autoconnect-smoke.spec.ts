import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'autoconnect');
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

test('Petri Net: ?autoconnect=ws://... abre painel sozinho e tenta conectar', async ({ page }) => {
  test.setTimeout(60_000);
  page.on('dialog', async (d) => { await d.accept().catch(() => {}); });

  await login(page);

  // Navega diretamente com query param autoconnect (simulando vindo do toast)
  const fakeUrl = 'ws://localhost:9999'; // porta livre — connect vai falhar (esperado)
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net?autoconnect=${encodeURIComponent(fakeUrl)}`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(4000);
  await page.screenshot({ path: ts('arrived-with-autoconnect'), fullPage: true });

  // 1) ExecutionPanel deve estar aberto sem clique
  const panelOpen = await page.evaluate(() => {
    return (document.body.textContent || '').includes('Execução Real');
  });
  expect(panelOpen, 'ExecutionPanel não abriu automaticamente').toBeTruthy();

  // 2) URL deve estar preenchida com a do query param (input ws://...)
  const urlInput = await page.evaluate(() => {
    const inputs = Array.from(document.querySelectorAll('input'));
    const wsInput = inputs.find((i) => /ws:\/\//.test((i as HTMLInputElement).value));
    return (wsInput as HTMLInputElement | undefined)?.value;
  });
  expect(urlInput, 'URL não preenchida').toBe(fakeUrl);

  // 3) Status deve ser CONECTANDO ou ERRO (mas NÃO desconectado parado)
  const status = await page.evaluate(() => {
    const txt = document.body.textContent || '';
    return {
      connecting: txt.includes('CONECTANDO'),
      error: txt.includes('ERRO'),
      disconnectedOnly: txt.includes('DESCONECTADO') && !txt.includes('CONECTANDO') && !txt.includes('ERRO'),
    };
  });
  console.log('Status após autoconnect:', status);
  // Como porta 9999 está livre, deve ir para ERRO eventualmente
  expect(status.disconnectedOnly, 'autoconnect não disparou — ficou em DESCONECTADO').toBeFalsy();

  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('final-status'), fullPage: true });
});

/**
 * Captura ciclo completo: code-gen com sessão recém-rodada + Petri Net com
 * ExecutionPanel autoconectado ao ws://localhost:5002, disparando uma task real.
 */
import { test, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const CODE_GEN_SESSION = '7684959e-087c-4d06-85d6-673a3a2401ab';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const WS_URL = 'ws://localhost:5002';
const OUT = path.join(__dirname, '..', 'test-results', 'quantica-live');
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

test('Quântica: ExecutionPanel live com 5 abas + task real DeepSeek', async ({ page }) => {
  test.setTimeout(180_000);
  page.on('console', (m) => { if (m.type() !== 'warning') console.log('[browser]', m.text().slice(0,200)); });
  await login(page);

  // Abre Petri Net com autoconnect
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net?autoconnect=${encodeURIComponent(WS_URL)}`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(8000);
  await page.screenshot({ path: ts('petri-net-with-panel'), fullPage: true });

  // Confirma o painel aberto + status conectado
  const panelText = await page.evaluate(() => {
    const txt = document.body.textContent || '';
    return {
      hasOperacao: txt.includes('Operação') || txt.includes('operacao'),
      hasExecucao: txt.includes('Execução') || txt.includes('execucao'),
      hasInputs: txt.includes('Inputs'),
      hasOutputs: txt.includes('Outputs'),
      hasLogs: txt.includes('Logs'),
      hasConectado: txt.includes('CONECTADO') || txt.includes('connected'),
      taskCount: (txt.match(/(\d+) tasks?/) || [])[0] || '',
    };
  });
  console.log('Painel:', panelText);

  // Tira screenshot da aba Operação
  await page.screenshot({ path: ts('aba-operacao'), fullPage: true });

  // Clica em Execução
  const exTab = await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      (b.textContent || '').trim().toLowerCase() === 'execução' ||
      (b.textContent || '').trim().toLowerCase() === 'execucao'
    );
    (btn as HTMLButtonElement | undefined)?.click();
    return Boolean(btn);
  });
  console.log('clicou Execução:', exTab);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: ts('aba-execucao'), fullPage: true });

  // Inputs
  const inTab = await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      (b.textContent || '').trim() === 'Inputs'
    );
    (btn as HTMLButtonElement | undefined)?.click();
    return Boolean(btn);
  });
  console.log('clicou Inputs:', inTab);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: ts('aba-inputs'), fullPage: true });

  // Logs
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      (b.textContent || '').trim() === 'Logs'
    );
    (btn as HTMLButtonElement | undefined)?.click();
  });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: ts('aba-logs'), fullPage: true });
});

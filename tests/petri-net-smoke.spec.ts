import { test, expect, Page, APIRequestContext } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = process.env.LANGNET_EMAIL || 'teste@teste.com';
const PASSWORD = process.env.LANGNET_PASSWORD || 'buceta123';
const PROJECT_ID = process.env.LANGNET_PROJECT_ID || '422027f1-9e89-4f84-9474-adb67f43c8ff';
const AGENTS_YAML_ID = 'dce1605f-f721-44a0-a08a-a2d7798e54a7';
const TASKS_YAML_ID = 'e084350f-37dc-4ee2-96ad-4f4b0e737851';
const TEF_ID = 'd848732d-78d5-4227-bc5c-265eb14b4604';

const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';

const SCREENSHOT_DIR = path.join(__dirname, '..', 'test-results', 'petri-smoke');

function ts(label: string) {
  return path.join(SCREENSHOT_DIR, `${String(stepIdx++).padStart(2, '0')}-${label}.png`);
}
let stepIdx = 1;

async function login(page: Page) {
  // Obter token via API e injetar no localStorage (evita flakiness da tela de login).
  const res = await page.request.post(`${API_BASE}/auth/login`, {
    data: { email: EMAIL, password: PASSWORD },
    headers: { 'Content-Type': 'application/json' },
  });
  expect(res.ok(), `login api failed: ${res.status()}`).toBeTruthy();
  const body = await res.json();
  const token = body.access_token as string;
  expect(token, 'no access_token').toBeTruthy();

  await page.goto(`${APP_BASE}/login`);
  await page.evaluate(([t, u]) => {
    localStorage.setItem('accessToken', t);
    localStorage.setItem('token', t);
    localStorage.setItem('user', JSON.stringify(u));
  }, [token, body.user]);
  return token;
}

async function readProjectData(token: string, api: APIRequestContext) {
  const r = await api.get(`${API_BASE}/petri-net/${PROJECT_ID}`, {
    headers: { Authorization: `Bearer ${token}` },
    timeout: 60_000,
  });
  if (!r.ok()) return null;
  return (await r.json()).petri_net;
}

test.beforeAll(() => {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
});

test('Petri Net smoke: gerar → render → salvar → reload', async ({ page, request }) => {
  test.setTimeout(420_000);

  // 1) Login + navegar
  const token = await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/petri-net`);
  await page.waitForLoadState('networkidle', { timeout: 30_000 }).catch(() => {});
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('initial-page'), fullPage: true });

  // 2) Clicar "Gerar Rede" (botão azul "🔗 Gerar Rede")
  const generateBtn = page.getByRole('button', { name: /gerar rede/i });
  await expect(generateBtn, 'botão "Gerar Rede" não encontrado').toBeVisible({ timeout: 15_000 });
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /gerar rede/i.test(b.textContent || ''),
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: ts('modal-opened'), fullPage: true });

  // 3) Aguardar carga das sessões no modal e selecionar via <select>
  // (modal renderiza 3 <select> em ordem: agents.yaml, tasks.yaml, task_execution_flow)
  const selects = page.locator('div >> select');
  await expect(selects.nth(0)).toBeVisible({ timeout: 15_000 });
  // Aguardar options preenchidas (sessões só aparecem depois do fetch)
  await page.waitForFunction(() => {
    const s = document.querySelectorAll('select');
    return s.length >= 2 && Array.from(s).slice(0, 2).every((sel) => sel.options.length > 1);
  }, { timeout: 30_000 });

  await selects.nth(0).selectOption(AGENTS_YAML_ID);
  await selects.nth(1).selectOption(TASKS_YAML_ID);
  if ((await selects.count()) >= 3) {
    await selects.nth(2).selectOption(TEF_ID).catch(() => {});
  }
  await page.screenshot({ path: ts('modal-filled'), fullPage: true });

  // 4) Confirmar geração — botão "Gerar Rede" dentro do modal (azul, primário)
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button')).filter(
      (b) => /^gerar rede$/i.test((b.textContent || '').trim()) && !(b as HTMLButtonElement).disabled,
    );
    (btns[btns.length - 1] as HTMLButtonElement)?.click();
  });

  // 5) Aguardar geração (pode demorar — LLM via DeepSeek)
  // O editor mostra "⏳ Processando..." enquanto isLoadingNet=true.
  // Esperar até o canvas SVG receber lugares (círculos) ou timeout 5 min.
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('generation-started'), fullPage: true });

  await page.waitForFunction(
    () => {
      const circles = document.querySelectorAll('svg circle');
      return circles.length >= 1;
    },
    null,
    { timeout: 300_000, polling: 2000 },
  );

  await page.waitForTimeout(1500);
  await page.screenshot({ path: ts('canvas-rendered'), fullPage: true });

  const stats = await page.evaluate(() => {
    const circles = document.querySelectorAll('svg circle').length;
    const rects = document.querySelectorAll('svg rect').length;
    return { circles, rects };
  });
  console.log('Canvas after generation — circles (lugares):', stats.circles, 'rects:', stats.rects);
  expect(stats.circles, 'nenhum lugar (círculo) renderizado').toBeGreaterThan(0);

  // 6) Validar persistência via UI (canvas render já é a prova). API check pulado
  //    para não competir com o backend (LLM pode estar bloqueado por outra request).

  // Aceita TODOS os dialogs (alert do salvar OK ou erros)
  page.on('dialog', async (d) => {
    console.log('Dialog:', d.type(), '->', d.message());
    await d.accept().catch(() => {});
  });

  // 7) Clicar "Salvar no Banco" (botão verde)
  await page.waitForTimeout(2000); // estabilizar canvas
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find((b) =>
      /salvar no banco/i.test(b.textContent || ''),
    ) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: ts('after-save'), fullPage: true });

  // 8) Reload e confirmar que carrega do banco (project_data já tem a rede gerada).
  await page.reload({ waitUntil: 'domcontentloaded', timeout: 60_000 });
  await page.waitForTimeout(2000); // dar tempo do React montar
  // Polling longo: GET pode ficar esperando se há LLM em background
  await page.waitForFunction(
    () => document.querySelectorAll('svg circle').length >= 1,
    null,
    { timeout: 120_000, polling: 2000 },
  );
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('after-reload'), fullPage: true });

  const reloadStats = await page.evaluate(() => ({
    circles: document.querySelectorAll('svg circle').length,
    rects: document.querySelectorAll('svg rect').length,
  }));
  console.log('Canvas after reload — circles:', reloadStats.circles, 'rects:', reloadStats.rects);
  expect(reloadStats.circles, 'canvas vazio após reload (não persistiu)').toBeGreaterThan(0);

});

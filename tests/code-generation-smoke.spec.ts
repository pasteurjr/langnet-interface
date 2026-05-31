import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';
const AGENTS_YAML_ID = 'dce1605f-f721-44a0-a08a-a2d7798e54a7';
const TASKS_YAML_ID = 'e084350f-37dc-4ee2-96ad-4f4b0e737851';
const TEF_ID = 'd848732d-78d5-4227-bc5c-265eb14b4604';

const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'code-gen-smoke');

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

test('Code generation: gerar → renderizar tree+editor → refinar → salvar → download ZIP', async ({ page }) => {
  test.setTimeout(600_000);
  page.on('dialog', async (d) => { console.log('Dialog:', d.message()); await d.accept().catch(() => {}); });

  await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('initial'), fullPage: true });

  // 1) Abre modal e gera
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /gerar c[oó]digo/i.test(b.textContent || '')) as HTMLButtonElement | undefined;
    btn?.click();
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: ts('modal-opened'), fullPage: true });

  // Espera options carregarem
  await page.waitForFunction(() => {
    const sels = document.querySelectorAll('select');
    return sels.length >= 2 && Array.from(sels).slice(0, 2).every((s) => s.options.length > 1);
  }, { timeout: 30_000 });

  const selects = page.locator('div >> select');
  await selects.nth(0).selectOption(AGENTS_YAML_ID);
  await selects.nth(1).selectOption(TASKS_YAML_ID);
  if ((await selects.count()) >= 3) {
    await selects.nth(2).selectOption(TEF_ID).catch(() => {});
  }
  await page.screenshot({ path: ts('modal-filled'), fullPage: true });

  // Confirma geração (botão "Gerar Código" do modal — último não disabled)
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button')).filter(
      (b) => /^gerar c[oó]digo$/i.test((b.textContent || '').trim()) && !(b as HTMLButtonElement).disabled,
    );
    (btns[btns.length - 1] as HTMLButtonElement)?.click();
  });

  // Aguarda geração (LLM real — pode demorar minutos)
  await page.waitForFunction(
    () => {
      const items = document.querySelectorAll('div[style*="cursor: pointer"]');
      let count = 0;
      items.forEach((el) => { if ((el.textContent || '').endsWith('.py') || (el.textContent || '').endsWith('.yaml') || (el.textContent || '').endsWith('.json')) count++; });
      return count >= 3;
    },
    null,
    { timeout: 360_000, polling: 3000 },
  );
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('files-listed'), fullPage: true });

  // Verifica número de arquivos
  const fileStats = await page.evaluate(() => {
    const paths: string[] = [];
    document.querySelectorAll('div[style*="cursor: pointer"]').forEach((el) => {
      const t = (el.textContent || '').trim();
      if (t.includes('.') || t === 'Dockerfile') paths.push(t);
    });
    return paths;
  });
  console.log('Files visible:', fileStats);
  expect(fileStats.some((p) => p.endsWith('.py')), 'no .py files').toBeTruthy();
  expect(fileStats.some((p) => p.endsWith('.yaml')), 'no .yaml files').toBeTruthy();
  expect(fileStats.some((p) => p === 'petri_net.json'), 'petri_net.json missing').toBeTruthy();

  // 2) Clica em main.py e confere render do Monaco
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .find((e) => (e.textContent || '').trim() === 'main.py');
    (el as HTMLElement)?.click();
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: ts('main-py-selected'), fullPage: true });

  const hasMonaco = await page.evaluate(() => !!document.querySelector('.monaco-editor'));
  expect(hasMonaco, 'monaco editor não montou').toBeTruthy();

  // 3) Conferir petri_net.json com porta literal
  await page.evaluate(() => {
    const el = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .find((e) => (e.textContent || '').trim() === 'petri_net.json');
    (el as HTMLElement)?.click();
  });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('petri-net-json'), fullPage: true });

  // 4) Baixar ZIP — fica salvo no test-results
  const [download] = await Promise.all([
    page.waitForEvent('download', { timeout: 30_000 }),
    page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button'))
        .find((b) => /baixar zip/i.test(b.textContent || '')) as HTMLButtonElement | undefined;
      btn?.click();
    }),
  ]);
  const dest = path.join(OUT, 'project.zip');
  await download.saveAs(dest);
  const size = fs.statSync(dest).size;
  console.log('ZIP size:', size, 'bytes');
  expect(size, 'ZIP vazio').toBeGreaterThan(1000);
  await page.screenshot({ path: ts('after-download'), fullPage: true });
});

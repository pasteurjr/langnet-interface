/**
 * Smoke fase F: botão "🚀 Corrigir e enviar" deve estar presente ao lado
 * do "🔧 Corrigir" e disparar uma chamada POST /refine quando clicado.
 * Interceptamos a chamada — não esperamos a LLM completar.
 */
import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const EMAIL = 'teste@teste.com';
const PASSWORD = 'buceta123';
const PROJECT_ID = '422027f1-9e89-4f84-9474-adb67f43c8ff';
const API_BASE = 'http://localhost:8000/api';
const APP_BASE = 'http://localhost:3000';
const OUT = path.join(__dirname, '..', 'test-results', 'autofix');
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

test('Auto-fix: botão "Corrigir e enviar" dispara POST /refine imediatamente', async ({ page }) => {
  test.setTimeout(60_000);

  await login(page);
  await page.goto(`${APP_BASE}/project/${PROJECT_ID}/code-generation`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(3000);

  // Carrega sessão completed (terá warnings)
  await page.evaluate(() => {
    const sess = Array.from(document.querySelectorAll('div[style*="cursor: pointer"]'))
      .find((el) => /completed/i.test(el.textContent || ''));
    (sess as HTMLElement)?.click();
  });
  await page.waitForTimeout(2500);

  // Confere que botão "Corrigir e enviar" existe ao lado de "Corrigir"
  const buttonsFound = await page.evaluate(() => {
    const txts = Array.from(document.querySelectorAll('button')).map(b => b.textContent || '');
    return {
      fix: txts.some(t => /^🔧 Corrigir$/.test(t.trim())),
      autoFix: txts.some(t => /^🚀 Corrigir e enviar$/.test(t.trim())),
    };
  });
  console.log('Botões:', buttonsFound);
  expect(buttonsFound.fix, 'Botão "🔧 Corrigir" não encontrado').toBeTruthy();
  expect(buttonsFound.autoFix, 'Botão "🚀 Corrigir e enviar" não encontrado').toBeTruthy();
  await page.screenshot({ path: ts('banner-with-buttons'), fullPage: true });

  // Intercepta a chamada de refine (não deixa chegar no LLM real — substituímos resposta)
  let refineCalled = false;
  let refinePayload: any = null;
  await page.route(`${API_BASE}/code-generation/*/refine`, async (route) => {
    refineCalled = true;
    refinePayload = JSON.parse(route.request().postData() || '{}');
    // Mock response com diff vazio
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        has_diff: false,
        message: 'mocked',
        validation_warnings: [],
      }),
    });
  });

  // Clica no primeiro botão "🚀 Corrigir e enviar"
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button'))
      .find((b) => /^🚀 Corrigir e enviar$/.test((b.textContent || '').trim())) as HTMLButtonElement | undefined;
    btn?.click();
  });

  // Aguarda chamada
  await page.waitForTimeout(2500);
  await page.screenshot({ path: ts('after-auto-fix'), fullPage: true });

  expect(refineCalled, 'POST /refine não foi chamado pelo botão auto-fix').toBeTruthy();
  expect(refinePayload?.message, 'Payload sem campo message').toBeTruthy();
  expect(refinePayload.message.length, 'Mensagem muito curta').toBeGreaterThan(40);
  console.log(`✅ Auto-fix dispara refine com prompt de ${refinePayload.message.length} chars`);
  console.log('Prompt enviado:', refinePayload.message.substring(0, 150));
});

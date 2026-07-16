/**
 * Demo ao vivo Quântica Comercial — grava vídeo navegando a UI e executando
 * a task cadastrar_persona_alvo (deterministic bypass) contra o MySQL real.
 */
import { test } from '@playwright/test';

const APP = 'http://localhost:3000';
const PROJ = 'b55ef718-0073-44d4-b279-11df89403e92';

test.use({
  video: 'on',
  viewport: { width: 1600, height: 900 },
});

test('Demo Quântica — navegação + execução deterministic', async ({ page }) => {
  test.setTimeout(300_000);

  // ─────────────────────── Login ───────────────────────
  await page.goto(APP);
  await page.waitForTimeout(2500);
  await page.locator('#email').fill('teste@teste.com');
  await page.waitForTimeout(800);
  await page.locator('#password').fill('buceta123');
  await page.waitForTimeout(800);
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(2500);

  // ─────────────────────── Projetos ───────────────────────
  await page.goto(`${APP}/projects`);
  await page.waitForTimeout(3500);

  // ─────────────────────── Requirements ───────────────────────
  await page.goto(`${APP}/project/${PROJ}/requirements`);
  await page.waitForTimeout(5000);
  await page.mouse.wheel(0, 400);
  await page.waitForTimeout(2000);
  await page.mouse.wheel(0, 400);
  await page.waitForTimeout(2000);

  // ─────────────────────── Spec ───────────────────────
  await page.goto(`${APP}/project/${PROJ}/spec`);
  await page.waitForTimeout(5000);
  await page.mouse.wheel(0, 400);
  await page.waitForTimeout(2000);

  // ─────────────────────── Data Model ───────────────────────
  await page.goto(`${APP}/project/${PROJ}/data-model`);
  await page.waitForTimeout(5000);
  // Tenta clicar nas abas Entidades / Schema SQL
  for (const tab of ['Entidades', 'Schema SQL', 'models.py']) {
    const btn = page.locator(`button:has-text("${tab}"), [role="tab"]:has-text("${tab}")`).first();
    if (await btn.count() > 0) {
      await btn.click().catch(() => {});
      await page.waitForTimeout(3000);
    }
  }

  // ─────────────────────── Agent-Task ───────────────────────
  await page.goto(`${APP}/project/${PROJ}/agent-task`);
  await page.waitForTimeout(5000);
  await page.mouse.wheel(0, 400);
  await page.waitForTimeout(2000);

  // ─────────────────────── YAMLs ───────────────────────
  await page.goto(`${APP}/project/${PROJ}/yaml-generation`);
  await page.waitForTimeout(5000);
  const tasksTab = page.locator('button:has-text("Tasks YAML"), button:has-text("tasks.yaml")').first();
  if (await tasksTab.count() > 0) {
    await tasksTab.click().catch(() => {});
    await page.waitForTimeout(3500);
  }

  // ─────────────────────── Petri Net ───────────────────────
  await page.goto(`${APP}/project/${PROJ}/petri-net`);
  await page.waitForTimeout(7000);

  // ─────────────────────── Code Gen ───────────────────────
  await page.goto(`${APP}/project/${PROJ}/code-generation`);
  await page.waitForTimeout(5000);

  // Clica na sessão mais recente
  const session = page.locator('text=/^code_gen_20260716_162910/').first();
  if (await session.count() > 0) {
    await session.click().catch(() => {});
    await page.waitForTimeout(3500);
  }

  // Abre adapters.py
  const adaptersLink = page.locator('text=/adapters\\.py/').first();
  if (await adaptersLink.count() > 0) {
    await adaptersLink.click().catch(() => {});
    await page.waitForTimeout(3500);
    // scroll no editor até o final (deterministic fica no fim)
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press('PageDown');
      await page.waitForTimeout(200);
    }
    await page.waitForTimeout(3000);
  }

  // Abre tasks.yaml
  const tasksYaml = page.locator('text=/^ws-server\\/tasks\\.yaml/').first();
  if (await tasksYaml.count() > 0) {
    await tasksYaml.click().catch(() => {});
    await page.waitForTimeout(3500);
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press('PageDown');
      await page.waitForTimeout(200);
    }
    await page.waitForTimeout(3000);
  }

  // final rest
  await page.waitForTimeout(2000);
});

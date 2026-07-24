/**
 * Captura screenshots de TODAS as etapas do pipeline pro manual completo.
 */
import { test } from '@playwright/test';
const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/manual/screens';
const P = 'b55ef718-0073-44d4-b279-11df89403e92';
const REQ = '9670f599-c0f3-40d2-bb4f-8f989198f082';

import * as fs from 'fs';

test('Screenshots do manual', async ({ page }) => {
  test.setTimeout(600_000);
  await page.setViewportSize({ width: 1920, height: 1080 });
  fs.mkdirSync(OUT, { recursive: true });

  // Login
  await page.goto(APP);
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/00-login-ok.png`, fullPage: true });

  // Projeto (dashboard/lista)
  await page.goto(`${APP}/projects`);
  await page.waitForTimeout(4000);
  await page.screenshot({ path: `${OUT}/01-projetos.png`, fullPage: true });

  // Etapa 1 — Requirements
  await page.goto(`${APP}/project/${P}/requirements/${REQ}`);
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/02-requirements-tela.png`, fullPage: true });

  // Etapa 2 — Specification
  await page.goto(`${APP}/project/${P}/spec`);
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/03-specification-tela.png`, fullPage: true });

  // Etapa 3 — Data Model
  await page.goto(`${APP}/project/${P}/data-model`);
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/04-datamodel-tela.png`, fullPage: true });
  // Abas: Entidades, Schema SQL, models.py, Alembic, YAML
  for (const tab of ['Entidades','Schema SQL','models.py','Alembic','YAML']) {
    const t = page.locator(`button:has-text("${tab}"), [role="tab"]:has-text("${tab}")`).first();
    if (await t.count() > 0) {
      await t.click().catch(() => {});
      await page.waitForTimeout(1500);
      await page.screenshot({ path: `${OUT}/04-datamodel-${tab.replace(/[^\w]/g,'_')}.png`, fullPage: true });
    }
  }

  // Etapa 4a — Agent-Task
  await page.goto(`${APP}/project/${P}/agent-task`);
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/05-agenttask-tela.png`, fullPage: true });

  // Etapa 4b/4c — YAMLs
  await page.goto(`${APP}/project/${P}/yaml-generation`);
  await page.waitForTimeout(5000);
  await page.screenshot({ path: `${OUT}/06-yamls-tela.png`, fullPage: true });
  // Aba Tasks
  const tabTasks = page.locator('button:has-text("Tasks YAML")').first();
  if (await tabTasks.count() > 0) {
    await tabTasks.click().catch(() => {});
    await page.waitForTimeout(1500);
    await page.screenshot({ path: `${OUT}/06-yamls-tab-tasks.png`, fullPage: true });
  }

  // Etapa 5 — Petri Net
  await page.goto(`${APP}/project/${P}/petri-net`);
  await page.waitForTimeout(10000);
  await page.screenshot({ path: `${OUT}/07-petri-tela.png`, fullPage: true });
  // Zoom out
  const canvas = page.locator('svg, canvas, .joint-paper').first();
  if (await canvas.count() > 0) {
    const box = await canvas.boundingBox().catch(() => null);
    if (box) {
      const cx = box.x + box.width/2, cy = box.y + box.height/2;
      for (let i = 0; i < 8; i++) {
        await page.mouse.move(cx, cy);
        await page.keyboard.down('Control');
        await page.mouse.wheel(0, 300);
        await page.keyboard.up('Control');
        await page.waitForTimeout(150);
      }
    }
  }
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${OUT}/07-petri-overview.png`, fullPage: true });

  // Etapa 6 — Code Gen
  await page.goto(`${APP}/project/${P}/code-generation`);
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/08-codegen-tela.png`, fullPage: true });
});

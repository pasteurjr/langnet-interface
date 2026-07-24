/**
 * Etapa 4 do pipeline LangNet — Agentes & Tarefas da Quântica Comercial.
 * A partir da spec da Etapa 2 (fbc45992..., 73k chars), define lista de
 * agentes CrewAI e decomposição de tarefas.
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';
const TARGET_SPEC_ID = 'fbc45992-2900-40b5-8867-fc0639f959bc';

test('Gerar Agents & Tasks Quântica (Etapa 4)', async ({ page }) => {
  test.setTimeout(2400_000);
  fs.mkdirSync(OUT, { recursive: true });

  await page.goto(APP);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('[1] login OK');

  await page.goto(`${APP}/project/${PROJECT_ID}/agent-task`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(5000);
  await page.screenshot({ path: `${OUT}/etapa4-01-inicial.png`, fullPage: true });
  console.log('[2] tela Agent-Task carregada');

  // Botão "Especificação" abre modal
  const specBtn = page.locator('button:has-text("Especificação"), button:has-text("Espec")').first();
  await specBtn.click({ timeout: 5000 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/etapa4-02-modal-spec.png`, fullPage: true });
  console.log('[3] modal de spec aberto');

  // Clica em "Clique para ver versões →" da spec de 06/07/2026 (primeiro card)
  await page.waitForTimeout(2000);
  const verLink = page.locator('text=/Clique para ver vers/i').first();
  await verLink.click();
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/etapa4-02b-versoes.png`, fullPage: true });

  // Escolhe a versão mais recente (Versão 2 se existir, senão Versão 1) — "Clique para carregar →"
  const carregarLinks = page.locator('text=/Clique para carregar/i');
  const nCarreg = await carregarLinks.count();
  console.log(`  links "carregar" no modal: ${nCarreg}`);
  if (nCarreg > 0) {
    await carregarLinks.first().click(); // versão 2 (topo, mais recente)
    console.log('  clicou em Carregar (Versão 2 mais recente)');
    await page.waitForTimeout(3000);
  }
  await page.screenshot({ path: `${OUT}/etapa4-03-spec-selecionada.png`, fullPage: true });
  console.log('[4] spec selecionada');

  // Instruções customizadas
  const customArea = page.locator('textarea[placeholder*="Priorizar" i], textarea[placeholder*="instru" i], textarea').first();
  if (await customArea.count() > 0 && await customArea.isVisible().catch(() => false)) {
    await customArea.fill('Gere agentes especializados por domínio (Editorial, Prospecção, Aprovação, Cadência, Relatório). Cada task deve rastrear pelo menos 1 UC ou FR do requirements. Priorizar CrewAI com ferramentas de database e web_search.');
    console.log('[4b] custom instructions preenchidas');
  }

  // Clica em Gerar
  const genBtn = page.locator('button:has-text("Gerar Agentes"), button.btn-start-analysis').first();
  const enabled = await genBtn.isEnabled().catch(() => false);
  console.log(`  botão Gerar enabled=${enabled}`);
  await genBtn.click({ timeout: 5000 });
  console.log('[5] clicou Gerar Agentes & Tarefas');
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa4-04-gerando.png`, fullPage: true });

  // Aguarda até 30 min
  let done = false;
  for (let i = 0; i < 240; i++) {
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const txt = document.body.textContent || '';
      const hasAgent = /Agente.*\d|agents?.*generated|Total.*Agentes/i.test(txt);
      const geraBtnBusy = /Gerando/i.test(document.body.textContent || '');
      return { hasAgent, geraBtnBusy, len: txt.length };
    });
    if (state.hasAgent && !state.geraBtnBusy) {
      done = true;
      console.log(`  ${(i+1)*10}s: agents & tasks gerados`);
      break;
    }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: aguardando (busy=${state.geraBtnBusy}, len=${state.len})`);
  }

  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa4-05-final.png`, fullPage: true });
  console.log('[FIM]');
});

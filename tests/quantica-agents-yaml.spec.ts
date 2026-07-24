/**
 * Etapa 4b — Geração do agents.yaml da Quântica a partir da Agent-Task Spec
 * de hoje (9e396ed7..., com 15 agentes granulares).
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/quantica-pipeline';
const PROJECT_ID = 'b55ef718-0073-44d4-b279-11df89403e92';

test('Gerar agents.yaml Quântica (Etapa 4b)', async ({ page }) => {
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

  await page.goto(`${APP}/project/${PROJECT_ID}/yaml-generation`);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/etapa4b-01-inicial.png`, fullPage: true });
  console.log('[2] tela Yaml-Generation carregada');

  // Confirma aba Agents ativa
  const abaAgents = page.locator('button:has-text("Agents YAML")').first();
  if (await abaAgents.count() > 0) {
    await abaAgents.click().catch(() => {});
    await page.waitForTimeout(1500);
  }

  // Botão Doc MD abre modal de seleção
  const docBtn = page.locator('button:has-text("Doc MD")').first();
  await docBtn.click({ timeout: 5000 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/etapa4b-02-modal-doc.png`, fullPage: true });
  console.log('[3] modal doc aberto');

  // Clicar em "Clique para ver versões →" da primeira card (topo = mais recente, 15 agentes)
  const verVersoes = page.locator('text=/Clique para ver vers/i').first();
  await verVersoes.waitFor({ state: 'visible', timeout: 10000 });
  await verVersoes.scrollIntoViewIfNeeded();
  await verVersoes.click({ timeout: 15000, force: true });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/etapa4b-03-versoes.png`, fullPage: true });

  // Clicar direto na "Versão 1" (o próprio card é clicável)
  const versaoCard = page.locator('text=/Versão\\s*1/').first();
  await versaoCard.waitFor({ state: 'visible', timeout: 10000 });
  await versaoCard.click({ force: true });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa4b-04-carregada.png`, fullPage: true });
  console.log('[4] spec selecionada');

  // Custom instructions (agentes granulares)
  const customArea = page.locator('textarea[placeholder*="Priorizar" i], textarea').first();
  if (await customArea.count() > 0 && await customArea.isVisible().catch(() => false)) {
    await customArea.fill('Gere um agents.yaml com TODOS os 15 agentes especificados no documento MD (AG-01 a AG-15). Cada agente deve ter role, goal, backstory específicos, e o campo "tools" listando as ferramentas apropriadas (database_query para todos, web_search onde couber). Use nomes em snake_case (persona_manager_agent, pilar_content_manager_agent, etc.). Não consolide/agrupe agentes.');
  }
  await page.screenshot({ path: `${OUT}/etapa4b-05-antes-gerar.png`, fullPage: true });

  // Gerar
  const genBtn = page.locator('button:has-text("Gerar agents.yaml"), button.btn-start-analysis').first();
  console.log(`  botão enabled=${await genBtn.isEnabled().catch(() => false)}`);
  await genBtn.click({ timeout: 5000 });
  console.log('[5] clicou Gerar agents.yaml');
  await page.waitForTimeout(3000);

  // Aguarda até 20 min
  let done = false;
  for (let i = 0; i < 180; i++) {
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const busy = /⏳ Gerando|Gerando\.\.\./i.test(document.body.textContent || '');
      const hasYaml = /agents_yaml|role:|backstory:|goal:/.test(document.body.textContent || '');
      return { busy, hasYaml };
    });
    if (!state.busy && state.hasYaml) {
      done = true;
      console.log(`  ${(i+1)*10}s: agents.yaml gerado`);
      break;
    }
    if (i % 6 === 0) console.log(`  ${(i+1)*10}s: aguardando (busy=${state.busy})`);
  }

  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/etapa4b-06-final.png`, fullPage: true });
  console.log('[FIM]');
});

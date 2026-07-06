/**
 * Teste: refinar documento de requisitos do projeto "Uso do Solo" via UI real.
 * - Faz login
 * - Navega até o projeto
 * - Abre a aba Requisitos
 * - Envia instruções de alteração via chat
 * - Aguarda LLM processar (R1 local, LM Studio)
 * - Captura screenshots antes/depois pra comparação
 */
import { test } from '@playwright/test';
import * as fs from 'fs';

const APP = 'http://localhost:3000';
const OUT = '/home/pasteurjr/comercial-quantica/relatorio-testes/uso-solo';
const PROJECT_ID = 'a1391183-f348-4a78-8773-8046b90a7676';
const EXEC_ID = '197e89af-c360-4f0a-bee9-5ad767381e22';

const SUGESTOES = `Aplique estas 5 melhorias ao Documento de Requisitos do projeto Uso do Solo:

1. **Adicionar FR de Conformidade LGPD** (novo FR-027): O sistema deve implementar controles de LGPD para dados pessoais coletados (proprietários de imóveis, requerentes, técnicos). Incluir: consentimento explícito no cadastro, direito ao esquecimento com anonimização de dados de análises anteriores, base legal documentada para cada categoria de dado processado, e criptografia em repouso para CPF/CNPJ.

2. **Adicionar FR de Acessibilidade (WCAG 2.1 AA)** (novo FR-028): A interface web (mapa interativo, formulários e relatórios) deve seguir WCAG 2.1 nível AA. Inclui: navegação por teclado em todas as camadas do mapa, alt-text em ícones de zoneamento, contraste mínimo 4.5:1, e leitor de tela compatível para descrição textual das restrições espaciais.

3. **Adicionar FR de Auditoria de Consultas** (novo FR-029): Toda consulta a área (por polígono ou por endereço) deve ser registrada com: timestamp UTC, usuário autenticado, coordenadas ou endereço, camadas ativas na consulta, resultado retornado (hash), IP de origem. Retenção mínima de 5 anos para atender fiscalização ambiental.

4. **Adicionar FR de Exportação de Laudo em PDF assinado** (novo FR-030): O sistema deve gerar laudos técnicos em PDF/A-3 com assinatura digital (ICP-Brasil ou padrão CAdES) contendo: identificação do técnico responsável, análise de viabilidade, restrições aplicáveis, referências legais (com números de artigos), mapa temático da área, e QR-code para verificação online.

5. **Adicionar NFR de SLA e Performance** (novo NFR-011): SLA de disponibilidade mensal de 99.5%. Tempo de resposta: consulta de área simples ≤ 3s (P95), geração de laudo completo ≤ 30s (P95). Suportar 200 consultas simultâneas sem degradação. Rota crítica (mapa + consulta) deve funcionar em modo offline degradado usando cache local por até 24h.

Ao aplicar, atualize também: seção 12 (priorização/dependências), seção 17 (rastreabilidade — vincule os novos itens às Regras de Negócio existentes quando aplicável), seção 15 (adicione observação sobre as melhorias aplicadas), e o metadado versão para 1.1. Mantenha o resto do documento intacto.`;

test('Refinar requisitos Uso do Solo via UI', async ({ page }) => {
  test.setTimeout(1800_000); // 30 min
  fs.mkdirSync(OUT, { recursive: true });

  // Login
  await page.goto(APP);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(3000);
  await page.locator('#email').fill('teste@teste.com');
  await page.locator('#password').fill('buceta123');
  await page.locator('button:has-text("Entrar")').first().click();
  await page.waitForFunction(() => !location.pathname.includes('/login'), { timeout: 15000 });
  await page.waitForTimeout(3000);
  console.log('[1] login OK');

  // Navega para a página de requisitos do projeto
  const url = `${APP}/project/${PROJECT_ID}/requirements/${EXEC_ID}`;
  await page.goto(url);
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(6000);
  await page.screenshot({ path: `${OUT}/01-tela-inicial.png`, fullPage: true });
  console.log('[2] navegou pra tela de requisitos');

  // Verifica que o documento carregou
  const bodyText = await page.evaluate(() => document.body.textContent || '');
  const hasReq = bodyText.includes('Requisitos') || bodyText.includes('FR-');
  console.log(`  doc carregou? ${hasReq} (${bodyText.length} chars)`);

  // Clica em "Refine with Agent" pra abrir o painel
  await page.locator('button:has-text("Refine with Agent")').click({ timeout: 5000 });
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/01b-refine-panel.png`, fullPage: true });
  console.log('[2b] painel Refine aberto');

  // Procura input/textarea do chat
  const inputSelectors = [
    'textarea[placeholder*="mensagem" i]',
    'textarea[placeholder*="pergunta" i]',
    'textarea[placeholder*="refina" i]',
    'input[placeholder*="mensagem" i]',
    'input[placeholder*="pergunta" i]',
    '.chat-input textarea',
    '.chat-input input',
    'textarea',
  ];
  let chatInput = null;
  for (const sel of inputSelectors) {
    const loc = page.locator(sel).last();
    if (await loc.count() > 0 && await loc.isVisible().catch(() => false)) {
      chatInput = loc;
      console.log(`  chat input encontrado com seletor: ${sel}`);
      break;
    }
  }
  if (!chatInput) {
    console.log('  chat input NÃO encontrado — pesquisa por qualquer textarea');
    const all = await page.locator('textarea').all();
    for (let i = 0; i < all.length; i++) {
      const ph = await all[i].getAttribute('placeholder').catch(() => '');
      console.log(`    textarea[${i}] placeholder="${ph}"`);
    }
    throw new Error('chat input não encontrado');
  }

  // Digita sugestões e envia
  await chatInput.click();
  await chatInput.fill(SUGESTOES);
  await page.screenshot({ path: `${OUT}/02-sugestoes-digitadas.png`, fullPage: true });
  console.log('[3] sugestões digitadas');

  // Clica no botão de enviar/refinar
  const sendSelectors = [
    'button:has-text("Refinar")',
    'button:has-text("Enviar")',
    'button:has-text("Aplicar")',
    'button[type="submit"]',
    'button svg', // ícone
  ];
  let clicked = false;
  for (const sel of sendSelectors) {
    try {
      const btn = page.locator(sel).last();
      if (await btn.count() > 0 && await btn.isVisible().catch(() => false)) {
        await btn.click({ timeout: 3000 });
        console.log(`  clicou em: ${sel}`);
        clicked = true;
        break;
      }
    } catch {}
  }
  if (!clicked) {
    await chatInput.press('Enter');
    console.log('  fallback: Enter no input');
  }
  await page.waitForTimeout(2500);
  await page.screenshot({ path: `${OUT}/03-apos-submit.png`, fullPage: true });

  console.log('[4] aguardando LLM processar (pode levar minutos — R1 local)');
  // Poll até response chegar (procura texto novo de sucesso ou versão)
  let done = false;
  for (let i = 0; i < 240; i++) { // 240 × 10s = 40 min
    await page.waitForTimeout(10000);
    const state = await page.evaluate(() => {
      const bt = document.body.textContent || '';
      return {
        hasV11: bt.includes('v1.1') || bt.includes('Versão: 1.1') || bt.includes('Version 1.1'),
        hasFR27: bt.includes('FR-027'),
        hasFR28: bt.includes('FR-028'),
        hasError: /erro|error/i.test(bt) && bt.includes('processamento'),
      };
    });
    if (state.hasFR27 || state.hasFR28 || state.hasV11) {
      done = true;
      console.log(`  ✓ resposta chegou após ${(i+1)*10}s (v1.1=${state.hasV11}, FR-27=${state.hasFR27}, FR-28=${state.hasFR28})`);
      break;
    }
    if (i % 6 === 0) console.log(`  ... aguardando (${(i+1)*10}s)`);
  }
  if (!done) console.log('  ⚠ timeout no polling — pode ter completado mesmo assim');

  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${OUT}/04-versao-nova.png`, fullPage: true });
  console.log('[5] screenshot final capturado');
});

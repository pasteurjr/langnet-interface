import { test } from '@playwright/test';
const OUT='/tmp/uso-solo-pipeline/shots-dados';
const PERSONAS = [
  ["Head de Operações — Varejo omnichannel",
   "Diretora de operações de rede varejista que quer automatizar atendimento e pós-venda com agentes de IA.",
   "Alto volume de tickets repetitivos; custo de SAC; equipe sobrecarregada em picos",
   "WhatsApp, Telefone, E-mail",
   "Black Friday se aproximando; NPS em queda; meta de reduzir custo de atendimento em 30%",
   "Integração com ERP legado; medo de resposta errada ao cliente; treinamento da equipe",
   "agentes de IA, atendimento automatizado, RAG, integração ERP, omnichannel",
   "sim"],
  ["Fundador de Fintech — copiloto de crédito",
   "Founder de fintech de crédito que quer um copiloto de IA para análise de risco e onboarding.",
   "Análise de crédito manual e lenta; fraude; compliance do Banco Central",
   "LinkedIn, Eventos",
   "Escala de originação; exigência regulatória; concorrência de bancos digitais",
   "explicabilidade do modelo; auditoria regulatória; custo de inferência",
   "análise de crédito, scoring, explainable AI, compliance, LLM",
   "sim"],
];
test('seed personas', async ({ page }) => {
  test.setTimeout(120000);
  await page.setViewportSize({ width: 1500, height: 1000 });
  await page.goto('http://localhost:3001', { waitUntil:'networkidle', timeout:45000 }).catch(()=>{});
  await page.waitForTimeout(3000);
  for (const P of PERSONAS) {
    await page.getByText('＋ Novo', {exact:false}).first().click().catch(()=>{});
    await page.waitForTimeout(1200);
    const ctrls = page.locator('input:visible, textarea:visible');
    for (let i=0; i<P.length; i++) await ctrls.nth(i).fill(P[i]).catch(()=>{});
    await page.waitForTimeout(500);
    await page.getByRole('button', { name: /Salvar/i }).first().click().catch(()=>{});
    await page.waitForTimeout(3000);
  }
  // volta ao topo da lista e captura
  await page.evaluate(() => window.scrollTo(0,0));
  await page.waitForTimeout(1500);
  await page.screenshot({ path:`${OUT}/03-personas-lista-topo.png` });
  console.log('[shot] lista topo');
});

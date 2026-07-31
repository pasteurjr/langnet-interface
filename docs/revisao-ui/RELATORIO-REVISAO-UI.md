# Relatório de Revisão pela Interface — Quântica Comercial

**Data:** 2026-07-31 · **Revisor:** Claude, agindo no lugar do usuário (abrindo telas, pedindo revisão ao agente, lendo e criticando)
**Projeto:** Quântica Comercial (`b55ef718…`) · **Modelo que revisa:** qwen2.5-coder-32b (LM Studio, no ar)

> **Método:** em cada etapa do pipeline eu **abri a última versão na UI do LangNet**, pedi ao
> **agente do LangNet** que fizesse a revisão (botão 🔍 Revisar / chat Analisar / 🔎 Verificar
> coerência), **li o que ele produziu**, capturei as telas e registrei **minhas críticas e o que
> pode ser melhorado**. As análises de conteúdo são do modelo qwen (economiza meu processamento);
> eu conduzo, leio e comento.

> **Nota técnica importante (correção de um erro meu anterior):** a spec de 73KB = **~20K tokens**
> (não 73K). O modelo qwen-32b local **dá conta** dos documentos grandes — o pipeline os gera em
> *chunks*. Não há necessidade de trocar de modelo; o único custo é velocidade.

---

## Etapa 1 — Especificação Funcional ✅

**O que fiz:** abri a etapa → 📜 Histórico → carreguei a última versão (06/07/2026, 72KB, 200 seções)
→ chat "Conversa com Agente IA": *"análise crítica: lacunas, inconsistências, UCs faltantes,
coerência fluxo↔wireframe"* → **🔍 Analisar**.

**O agente (qwen) produziu:**
- **Lacunas fluxo↔wireframe:** UC-002 (gerar calendário), UC-019 (permissões), UC-020 (Google
  Calendar), UC-017 (exportar), UC-023 (prospecção), UC-025 (aprovação humana).
- **UCs faltantes:** UC-024 (classificação de respostas + notificar CEO), UC-035 (relatórios
  semanais por e-mail), UC-036 (conformidade LGPD: esquecimento + auditoria).
- **Incoerências:** UC-003 (fluxo cita drag-and-drop, wireframe não mostra), UC-005, UC-007.

**Minha crítica:** revisão **útil e específica** (cita UCs reais). LGPD e relatórios semanais
faltantes são pertinentes ao negócio. Aplicar por UC (refino em bloco é custoso no modelo local).

---

## Etapa 2 — Modelo de Dados ✅

**Estado carregado:** v2 · MySQL · 19 tabelas · validação **75/100**, 2 problemas já sinalizados
(colunas JSON `calendarios.slots`, `apresentacoes_conteudo.slides` ruins p/ busca). Cliquei **🔍 Revisar**.

**O agente produziu (rápido, ~50s):**
- `pilares_conteudo.nome` é `NULL` sem justificativa → `NOT NULL` + `UNIQUE` por pilar;
- Colunas **JSON** `slots`/`slides` → normalizar em tabelas-filha (deu o `CREATE TABLE calendario_slots` com FK);
- Índice ausente em `posts.tipo_conteudo` (se houver filtro);
- Renomear `apresentacoes_conteudo.slides` → `estrutura_slides`;
- `leads.status` (ENUM) → considerar `CHECK`.

**Minha crítica:** revisão **sólida e coerente com o próprio alerta de validação**. Acionável e de
baixo risco. Recomendo aplicar.

---

## Etapa 3 — Protótipo de Interface ✅

**O que fiz:** abri a etapa (18 telas, v1) → **🔎 Verificar coerência** (a "revisão" desta etapa).

**Resultado:**
- ✅ **0/24 vínculos quebrados** — **prova que a correção P2 funcionou na UI real** (antes eram 16/39).
- ✅ Branding **"Quântica Comercial"** na sidebar + navegação unificada (correções que apliquei).
- ✅ Telas ricas (form "Novo Persona" com chips de Canais) — confirma que **não é "só CRUD"**.
- 🟡 **3 tipos de tela incompatíveis:** UC-003 (edit renderizado como dashboard), UC-016 (list→form),
  UC-017 (dashboard→form).

**Minha crítica:** a etapa está **bem melhor** após as correções. Os 3 kind-mismatch são o que
resta — a heurística de tipo de tela erra em edição/exportação. A corrigir no gerador.

---

## Etapa 4 — Casos de Teste ✅

**Estado carregado:** v1 · DRAFT · **1 caso de uso, 4 casos de teste** (UC-001). Mecânica boa:
Grafo Causa-Efeito + Tabela de Decisão (C1-C4) + casos TC-UC-001-01..04. Cliquei **🔍 Revisar**.

**O agente produziu:** cobertura de causas/efeitos limitada; **restrições ausentes** (limites,
tipos); **casos de exceção não cobertos** (campo obrigatório vazio, valor fora do intervalo);
redundâncias possíveis; resultados esperados vagos ("aceitar cadastro" → especificar "mensagem X").

**Minha crítica (o que o agente NÃO viu):** 🔴 o problema **maior é meta** — a etapa gerou testes
para **1 de ~20 UCs**. O agente só critica o que está carregado (UC-001), então não percebe a
lacuna global. **É um bug de geração da etapa de Casos de Teste** (parou no primeiro UC).

---

## Etapa 5 — Sequência de Tarefas ⚠️ (não revisável pela UI)

**Achado:** a etapa **não carrega a última versão automaticamente** (existe a sessão `3a7b5a9b` de
20/07 no banco, mas a página mostra "Sequência de Tarefas não gerada"). Ela exige **reselecionar 3
documentos obrigatórios** (Especificação + Agent/Task Spec + Tasks YAML) antes de qualquer coisa —
então o botão **Revisar fica desabilitado**.

**Minha crítica:** 🔴 **inconsistência de padrão** — todas as outras etapas auto-carregam a última
versão; esta não. Quebra o fluxo de revisão e obriga retrabalho. A corrigir (alinhar ao padrão das
demais, com auto-load da sessão mais recente).

---

## Conclusão geral

**O agente do LangNet (qwen-32b local) revisa bem.** Nas 4 etapas revisáveis, produziu críticas
específicas e acionáveis — confirma que dá para usar o próprio modelo como revisor do pipeline.

**Ranking de qualidade das etapas (o que vi):**
1. 🟢 **Especificação** — a mais rica; revisão do agente muito boa.
2. 🟢 **Modelo de Dados** — sólido; revisão coerente com a validação embutida.
3. 🟢 **Protótipo** — bem melhor após P2/P3 (0 vínculos quebrados, branded); faltam 3 kind-mismatch.
4. 🟡 **Casos de Teste** — mecânica boa, mas **só cobre 1 de ~20 UCs** (bug de geração).
5. 🔴 **Sequência de Tarefas** — não auto-carrega a última versão (quebra o padrão de revisão).

**Melhorias priorizadas (no gerador LangNet):**
1. 🔴 Casos de Teste: gerar para **todos** os UCs, não parar no primeiro.
2. 🔴 Sequência de Tarefas: **auto-load** da última versão (padrão das demais etapas).
3. 🟡 Protótipo: corrigir a heurística de tipo de tela (edit/list/dashboard) — 3 mismatches.
4. 🟡 Especificação: virar UCs os faltantes (LGPD, relatórios semanais) — aplicar por UC.
5. 🟢 Modelo de Dados: aplicar as sugestões (NOT NULL/UNIQUE, normalizar JSON, índices).

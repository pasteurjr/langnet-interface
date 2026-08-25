# Notas de observação — Validação do Pipeline (uso do solo)

## 1. Requisitos (sessão 01d24064)
- **Carregado pela UI:** página Documentos → botão "Histórico" → modal "Histórico de Versões" → sessão → "Versão 1 (14.18 KB, Análise inicial)". Screenshots: req-02, req-03.
- **Revisão (v1):** 14.522 chars, 26 requisitos funcionais (FR) cobrindo os 3 eixos (urbanístico 51 / ambiental 38 / licenciamento-laudo 66 menções). **Lacuna observada:** só 1 NFR (não-funcional) — faltava tratar desempenho de consultas espaciais, precisão geométrica (SRID) e integridade referencial das geometrias.
- **Correção pedida (via chat de refino da UI):** "Adicionar seção de NFR cobrindo desempenho das consultas espaciais (< 2s), precisão SRID 4674 (SIRGAS 2000) e integridade referencial — SEM remover nenhum FR."
- **Resultado (v2):** 18.871 chars. **FRs: 26 → 26 (PRESERVADOS)**. NFRs: 1 → 4. Termos espaciais/NFR: 6 → 23. Screenshot req-07 (Histórico mostrando Versão 2 + Versão 1).
- **Veredito:** ✅ MELHOROU. O refino adicionou os NFRs sem remover requisitos (a regra de preservação funciona). Zero regressão.

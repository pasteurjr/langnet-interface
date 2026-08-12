# Persistência da Consulta Médica — Relatório

**Data:** 2026-08-12 · **Projeto:** ClinIA · **Executor:** Claude (features do gerador do LangNet)

> Fechamento do fluxo: a **Consulta Médica** (agente) agora **persiste** o diagnóstico final no
> prontuário do atendimento corrente — sem apagar o que já estava lá.

## 1. O que faltava e como foi resolvido

A Consulta gera `diagnostico_final`/`conduta`/`prescricao`, mas o Modelo de Dados **não tem tabela/coluna**
dedicada — só `prontuarios.resumo_medico`. Duas features no gerador:

- **`atualizar_<entidade>` PARCIAL:** o UPDATE agora só altera as colunas informadas (e substitui filhos
  só se enviados) — antes zerava todas as demais. Melhoria geral e segura.
- **`FINALIZE`:** tela agêntica que **finaliza uma entidade da cadeia já criada** (Consulta → prontuário)
  grava a saída do agente numa coluna de texto da entidade (`resumo_medico`), pelo **id herdado do
  atendimento corrente**. Trata tanto resultado em objeto quanto em **texto puro** (o agente às vezes
  devolve string).

## 2. Prova no banco `clinia_ops`

Disparei a Consulta sobre o prontuário do fluxo E2E anterior. O painel de Resultado exibiu
**`PERSISTIDO_EM: prontuarios.resumo_medico`**. No banco:

```
resumo_medico (DEPOIS):
  diagnostico_final: Sindrome coronariana aguda (SCA) confirmada
  conduta: Internacao em unidade coronariana; anticoagulacao
  prescricao: AAS 300mg VO; Enoxaparina SC; O2 se SpO2<94

Colunas INTACTAS (update parcial):
  triagem            = "Dor toracica opressiva, sudorese"
  pre_diagnostico_id = 3cc4023d-…   (inalterado)
  encaminhamento_id  = 424e6af6-…   (inalterado)
```

O diagnóstico final foi **gravado no prontuário** e o resto do registro permaneceu **intacto** — o UPDATE
parcial funcionou.

## 3. Conclusão

- **Consulta persiste o diagnóstico final** no prontuário do atendimento corrente (via `FINALIZE` +
  `atualizar_` parcial) — o fluxo clínico agora fecha também na consulta.
- Features do gerador → valem para qualquer app gerado.
- **Ressalva:** por não haver coluna dedicada, o diagnóstico final é gravado em `resumo_medico`
  (sobrescreve o resumo preliminar). Se quiser estrutura própria (colunas `diagnostico_final`/`conduta`/
  `prescricao` ou uma tabela `consultas`), o próximo passo é um refino do Modelo de Dados pela UI.

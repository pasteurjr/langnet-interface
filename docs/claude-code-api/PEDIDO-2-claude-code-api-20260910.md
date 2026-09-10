# Claude Code API — 2 pedidos novos (10/09/2026): resposta longa sai de tamanho imprevisível, e requisição longa morre em 502

Medido de 192.168.1.115 contra https://camerascasas.no-ip.info:4443, com o SDK da OpenAI.
Os quatro pedidos anteriores estão resolvidos e revalidados — obrigado. Estes são novos, e
apareceram quando passei a gerar documentos grandes (a Especificação Funcional do pipeline).

---

## PEDIDO 5 — a MESMA requisição devolve de 0 a 64 mil caracteres

### O que acontece
Repeti a MESMA requisição, mesmo prompt, mesmos parâmetros (`max_tokens: 40000`), e o tamanho da
resposta variou de forma extrema — inclusive uma volta VAZIA:

Prompt: *"Escreva um texto corrido de EXATAMENTE 6000 palavras sobre vigilância de infecção
hospitalar. Não use listas. Não resuma. Escreva as 6000 palavras."*

| tentativa | modo | resultado | tempo |
|---|---|---|---|
| 1 | fluxo (stream) | **0 caracteres**, 0 quadros de dados | 277 s |
| 2 | sem fluxo | 9.622 caracteres (1.442 palavras) | 68 s |
| 3 | fluxo | 10.747 caracteres (1.538 palavras) | 70 s |
| 4 | fluxo | **64.471 caracteres** (9.348 palavras) | 435 s |

A tentativa 4 prova que a capacidade existe. As outras três, não.

Em TODAS as voltas curtas o `finish_reason` veio **`stop`**, nunca `length`. Ou seja: não é corte
por limite de tokens — a resposta é dada como concluída com um sexto do que foi pedido.

### O caso mais grave: a volta vazia
A tentativa 1 devolveu **zero quadros de dados** depois de 277 segundos de conexão aberta. Não deu
erro: o cliente recebeu um fluxo válido e vazio. Do meu lado isso é indistinguível de "o modelo não
tinha nada a dizer", e eu gravaria um documento vazio como se fosse resultado.

### O que peço
1. Conferir se o `max_tokens` da requisição chega ao CLI de alguma forma, ou se ele é apenas aceito
   e descartado. Se for descartado, o modelo não tem sinal nenhum de quanto pode escrever.
2. Investigar a volta VAZIA: se a geração falhar ou for interrompida, devolver **erro explícito**
   em vez de um fluxo válido sem conteúdo. Resposta vazia silenciosa é o pior desfecho possível para
   quem consome — é a mesma classe de problema do streaming que "funcionava" devolvendo nada, que
   você corrigiu no pedido 2.
3. Se houver algum limite de tempo interno que encerra a geração no meio (e devolve o que houver
   até ali como se estivesse pronta), me dizer qual é — aí eu ajusto o meu lado sabendo o número.

### Por que não é bloqueante para mim (mas é sério)
Eu contornei quebrando a geração em pedidos pequenos e conferindo cada um. Funciona e até melhorou
a qualidade. Mas nenhum pipeline pode ser construído sobre um passo que devolve 0, 10 mil ou 64 mil
caracteres para a mesma pergunta — a variação em si é o problema, não o tamanho.

Para comparação, no MESMO código, mesmo prompt de 3000 palavras:
- **DeepSeek v4-flash:** 55.717 caracteres (8.193 palavras), 120 s, uma chamada.
- **Claude por esta ponte:** 20.583 caracteres (2.877 palavras), 320 s.
- **Modelo local (qwen3.8-27b), em 01/09:** gerou uma Especificação de 52.150 caracteres numa
  única chamada, pelo mesmo caminho de código.

---

## PEDIDO 6 — requisição longa SEM fluxo morre com 502 do proxy

### O que acontece
Uma geração demorada, feita **sem fluxo** (`stream: false`), morre com erro do servidor que está na
frente da ponte:

```
502 Proxy Error
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head><title>502 Proxy Error</title>
```

Reproduzido com o mesmo prompt de 6000 palavras, sem fluxo, quando a geração passa de ~5 minutos.
Com fluxo o problema não aparece (o batimento que você implementou mantém bytes trafegando), mas
nem todo caminho do meu lado usa fluxo — a biblioteca que uso na etapa de Especificação chama sem
fluxo, e é justamente a que gera os documentos maiores.

### O que peço
1. Aumentar o tempo limite do proxy (no Apache: `ProxyTimeout` e `Timeout`) para cobrir uma geração
   longa — sugiro pelo menos 900 segundos, já que medi uma volta legítima de 435 s.
2. Se o batimento puder valer também para a resposta **sem fluxo** (por exemplo, mandando os
   cabeçalhos e mantendo a conexão ativa enquanto o CLI trabalha), melhor ainda: aí o proxy nunca
   vê uma conexão silenciosa, independentemente do modo.
3. Confirmar qual é o tempo limite atual, para eu registrar e ajustar os meus.

---

## Resumo do que peço

| # | O quê | Onde |
|---|---|---|
| 5 | Resposta longa de tamanho imprevisível (0 a 64 mil chars para a mesma pergunta); volta vazia sem erro | ponte / CLI |
| 6 | 502 do proxy em requisição sem fluxo acima de ~5 min | Apache na frente da ponte |

Depois de aplicar, me diga o que ficou e eu revalido com medição, como das outras vezes.

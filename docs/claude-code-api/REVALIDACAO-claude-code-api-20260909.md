# Claude Code API — revalidação do commit 7b8efdc (09/09/2026)

Medido de `192.168.1.115` contra `https://camerascasas.no-ip.info:4443`.
Cliente: SDK OpenAI e CrewAI 1.15.17 (provedor nativo, sem litellm).

## DEFEITO 1 (vazamento de contexto) — CORRIGIDO ✅

Reprodução original (ABACAXI-7731, 6 repetições da requisição independente):
**0 de 6 vazaram** (antes 1 de 6). `GET /v1/context` = 0. Seis leituras do `context_items`
após o `DELETE`: `0 0 0 0 0 0` — o apagar agora vale em todas as leituras.

**Não pude testar:** o isolamento ENTRE chaves diferentes (só tenho uma chave). Se for possível,
vale a prova cruzada: gravar com a chave A e tentar ler com a chave B.

## DEFEITO 2 (streaming) — CORRIGIDO no formato, mas falta o batimento ⚠️

O que ficou certo: o SDK da OpenAI consome sem erro, os quadros vêm como
`object: chat.completion.chunk` e termina em `[DONE]`. A falha silenciosa (resposta vazia) acabou.

O que ainda falta: **não chega byte nenhum durante a geração**. Medido numa geração longa
(texto de 1500 palavras):

```
 64.34s  data: {"id":"chatcmpl-7be0de83b748","object":"chat.completion.chunk"...
 64.34s  data: ...
 64.35s  data: ...      <- todos os quadros de uma vez, aos 64 s
```

64 segundos de silêncio absoluto e depois tudo junto. Entendo que o `claude -p` não entrega
incremental — não é isso que peço. O problema é outro: **uma conexão sem tráfego por minutos é
derrubada** por proxy, NAT ou temporizador de leitura no meio do caminho, e do lado do cliente é
indistinguível de travamento. É por isso que continuo com o streaming desligado para este provedor
e com a detecção de estol desativada (o que me tira uma proteção que uso com os outros modelos).

**Pedido:** enviar um **batimento** enquanto o CLI gera — uma linha de comentário SSE
(`: ping\n\n`) a cada 10-15 segundos. É inócuo (o SDK ignora comentários), custa nada, e aí a
promessa de "manter a conexão viva" passa a valer de fato. Com isso eu religo o streaming e volto
a detectar conexão morta.

## `include_context: true` — a opção existe mas está inerte ℹ️

Sequência medida: `DELETE /v1/context` → uma requisição gravando algo → `GET /v1/context`
devolve **`total_interactions: 0`**. Ou seja, **nada está sendo gravado**, então o `include_context:
true` não tem o que injetar (testado: responde "não sei" mesmo com a opção ligada).

Para o meu uso está ótimo — quero isolamento total. Só registro a divergência: o comportamento não
é "opt-in", é "desligado". Se a gravação era para continuar acontecendo, tem um defeito aí.

## `usage` — melhorou ✅
Aquele caso de `prompt_tokens: 4` agora dá `56`, e a resposta com ferramenta contou `56/16`.
Continua estimativa, como você disse — está documentado.

## Regressão: chamada de ferramenta ✅
Continua funcionando depois das correções: `finish_reason: tool_calls`, ida e volta em `role: tool`,
e a função Python executando de verdade sob CrewAI (registro interno + resposta final igual ao
retorno da função).

---

## Um achado NOVO, que não estava no relatório anterior 🔒

Nas respostas dos testes de vazamento, o modelo descreveu o que consultou:

> "Verifiquei minha **memória persistente deste projeto** (`~/.claude/projects/-mnt-kin...`)"
> "Meu **diretório de memória persistente** para este projeto está vazio (só existe um arquivo de lock)"

Ou seja: o CLI atrás da ponte roda dentro de um diretório de projeto e **lê a memória persistente
desse projeto**. Hoje está vazia, então não atrapalha. Mas **se alguém usar aquela máquina e essa
pasta ganhar conteúdo, esse conteúdo entra em TODAS as minhas chamadas de geração** — é a mesma
contaminação do defeito 1, entrando por outra porta, e essa eu não tenho como ver nem limpar daqui.

**Pedido:** rodar o CLI da ponte com a memória de projeto desabilitada, ou num diretório dedicado e
vazio que ninguém use para trabalhar.

## Uma observação de infraestrutura (não é defeito seu)
O certificado é do Let's Encrypt, válido para o **nome** `camerascasas.no-ip.info` e **não** para o
IP `192.168.1.100`. O provedor nativo do CrewAI não aceita desligar a conferência do certificado,
então pelo IP a conexão simplesmente cai. Passei a usar o nome. Consequência: o tráfego sai e volta
pela internet mesmo estando as duas máquinas na mesma rede. Se der para emitir um certificado que
cubra também o IP (ou publicar o nome no DNS interno), fica tudo dentro da rede.

**Aviso:** esse certificado **vence em 18/09/2026** — nove dias. Vale conferir a renovação
automática, porque quando ele vencer o pipeline inteiro para de conectar.

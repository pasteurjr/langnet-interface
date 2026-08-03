# Guia Completo — Como Obter as Credenciais das Integrações

**Para:** app gerado pelo LangNet (Quântica Comercial) · **Onde vão:** arquivo `.env` do `ws-server`, seção **INTEGRAÇÕES EXTERNAS**
**Objetivo:** obter cada valor que precisa ser colado no `.env` para habilitar as tools. Enquanto vazio, a tool **falha explícito** (não finge) — é seguro deixar em branco até você ter a credencial.

> ⚠️ **Aviso honesto:** os nomes de menu/telas dos painéis (Meta, Google, LinkedIn) mudam com frequência.
> Os **passos e conceitos** abaixo são estáveis; se um botão tiver outro nome, procure o equivalente.
> Onde envolve **aprovação (App Review)** ou **custo**, está sinalizado.

---

## Resumo rápido — o que preencher e onde conseguir

| Integração | Variáveis no `.env` | Onde obter | Precisa pagar? | Precisa aprovação? |
|---|---|---|---|---|
| **LinkedIn** | `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN` | LinkedIn Developers (app OAuth) | Não (grátis) | Sim, p/ postar como empresa |
| **Instagram** | `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_USER_ID` | Meta for Developers (app) | Não (grátis) | Sim (App Review) p/ produção |
| **Google Calendar** | `GOOGLE_CALENDAR_ACCESS_TOKEN`, `GOOGLE_CALENDAR_ID` | Google Cloud Console (OAuth) | Não (dentro da cota) | Não (interno) / Sim (público) |
| **CMS** | `CMS_API_URL`, `CMS_API_KEY` | Painel do CMS do cliente | Depende do CMS | Não |
| **E-mail (SMTP)** | `SMTP_HOST/PORT/USER/PASSWORD/FROM` | Gmail (App Password) ou provedor | Grátis/limites ou pago | Não |
| **Embeddings** | `EMBEDDINGS_API_BASE`, `EMBEDDINGS_MODEL` | LM Studio local (grátis) ou OpenAI | Grátis (local) / pago (OpenAI) | Não |
| **Busca vetorial** | `VECTOR_TABLE`, `VECTOR_TEXT_COL`, `VECTOR_ID_COL` | Sua própria tabela no banco | Não | Não |

---

## 1. LinkedIn — publicar posts

**O que a tool faz:** publica um post de texto (via LinkedIn *UGC Posts API*).
**Conta necessária:** um perfil LinkedIn. Para postar **como empresa**, uma **LinkedIn Page** (página da empresa) onde você seja administrador.
**Custo:** a API é **gratuita**. (Postar como empresa exige aprovação da Community Management API.)

### Passo a passo
1. Acesse **https://www.linkedin.com/developers/** e faça login.
2. **Create app** → informe nome, associe a **Company Page** da empresa, logo e aceite os termos.
3. Na aba **Auth** do app você verá o **Client ID** e **Client Secret** (guarde).
4. Na aba **Products**, adicione:
   - **Share on LinkedIn** (para postar como o **membro/pessoa** logado) — liberação geralmente automática.
   - **Community Management API** (para postar como a **empresa/organização**) — **requer solicitação/aprovação** da LinkedIn.
5. **Obter o access token (OAuth 2.0):**
   - Configure uma **Redirect URL** (ex.: `http://localhost:8000/callback`) na aba Auth.
   - Autorize com o **scope** adequado:
     - `w_member_social` → postar como pessoa (o mais simples).
     - `w_organization_social` → postar como empresa (precisa da aprovação do passo 4).
   - Troque o *authorization code* por um **access token**. Ferramenta oficial fácil: o **OAuth Token Generator** dentro do próprio app (aba **Auth → OAuth 2.0 tools**), que gera um token de teste com os scopes marcados.
   - → Esse token é o **`LINKEDIN_ACCESS_TOKEN`**. ⏳ Expira (tokens de membro ~60 dias); renove quando expirar.
6. **Obter o URN do autor (`LINKEDIN_AUTHOR_URN`):**
   - **Pessoa:** chame `GET https://api.linkedin.com/v2/userinfo` (com o token) → use `urn:li:person:{sub}` onde `{sub}` é o id retornado.
   - **Empresa:** o URN é `urn:li:organization:{ID_DA_PAGE}` — o ID aparece na URL de admin da Company Page.

```
LINKEDIN_ACCESS_TOKEN=AQV...(token gerado)
LINKEDIN_AUTHOR_URN=urn:li:person:AbC123   (ou urn:li:organization:12345678)
```

---

## 2. Instagram — publicar imagem (Graph API)

**O que a tool faz:** publica uma imagem com legenda (cria o container e publica).
**Contas necessárias (obrigatório):**
- Conta do Instagram do tipo **Business** ou **Creator** (não pode ser pessoal comum).
- Uma **Página do Facebook** vinculada a essa conta do Instagram.
- Uma conta no **Meta for Developers**.

**Custo:** **gratuito**. Para uso em **produção** (fora do modo de teste), a Meta exige **App Review** das permissões.

### Passo a passo
1. **Prepare as contas:** no app do Instagram → Configurações → converta para **conta profissional (Business)**. No **Facebook**, crie/una uma **Página** e vincule o Instagram (Configurações da Página → Contas do Instagram).
2. Acesse **https://developers.facebook.com/** → **My Apps** → **Create App** → tipo **Business**.
3. No app, adicione o produto **Instagram Graph API** (e **Facebook Login**).
4. **Permissões necessárias:** `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management`.
5. **Gerar o token:** use o **Graph API Explorer** (developers.facebook.com/tools/explorer):
   - Selecione seu app, clique **Generate Access Token**, marque as permissões acima.
   - Isso gera um **User Access Token** de curta duração. Troque por um **long-lived token** (dura ~60 dias) com a chamada `oauth/access_token?grant_type=fb_exchange_token`.
   - → esse é o **`INSTAGRAM_ACCESS_TOKEN`**. ⏳ Renove a cada ~60 dias (ou configure um token de sistema).
6. **Descobrir o `INSTAGRAM_USER_ID`** (id da conta business do Instagram):
   - `GET /me/accounts` → pega o **id da Página**.
   - `GET /{page-id}?fields=instagram_business_account` → retorna o **id da conta IG** → esse é o `INSTAGRAM_USER_ID`.
7. **App Review (para produção):** enquanto o app está em *Desenvolvimento*, só funciona com contas de teste/administradores. Para publicar de verdade em contas do cliente, submeta as permissões à **App Review** da Meta.

```
INSTAGRAM_ACCESS_TOKEN=EAAG...(long-lived)
INSTAGRAM_USER_ID=17841400000000000
```
> Obs.: a imagem enviada precisa estar em uma **URL pública** (o Instagram baixa a imagem da URL).

---

## 3. Google Calendar — criar eventos

**O que a tool faz:** cria um evento (data/hora início e fim) num calendário.
**Conta necessária:** uma conta Google + um **projeto no Google Cloud**.
**Custo:** **gratuito** dentro da cota generosa da API.

### Passo a passo
1. Acesse **https://console.cloud.google.com/** → crie um **projeto** (ou use um existente).
2. **APIs e serviços → Biblioteca** → procure **Google Calendar API** → **Ativar**.
3. **Tela de consentimento OAuth:** configure (tipo *Externo* ou *Interno* se for Google Workspace da empresa). Adicione o **escopo** `https://www.googleapis.com/auth/calendar.events`.
4. **Credenciais → Criar credenciais → ID do cliente OAuth** (tipo *App para computador* ou *Web*). Guarde **Client ID** e **Client Secret**.
5. **Obter o access token:** rode o fluxo OAuth (ex.: no **OAuth 2.0 Playground** — https://developers.google.com/oauthplayground):
   - No Playground, engrenagem → marque *Use your own OAuth credentials* e cole Client ID/Secret.
   - Selecione o escopo **Calendar API v3 → .../auth/calendar.events** → **Authorize** → login → **Exchange authorization code for tokens**.
   - Copie o **Access token** → esse é o **`GOOGLE_CALENDAR_ACCESS_TOKEN`**.
   - ⏳ **Importante:** o access token do Google **expira em ~1 hora**. Para uso contínuo, guarde o **refresh token** (o Playground também mostra) e gere um novo access token quando expirar — ou use uma **Service Account** (recomendado para servidor, sem interação humana).
6. **`GOOGLE_CALENDAR_ID`:** use `primary` (a agenda principal da conta) ou o ID de um calendário específico (Google Calendar → Configurações do calendário → **ID do calendário**, algo como `abc123@group.calendar.google.com`).

```
GOOGLE_CALENDAR_ACCESS_TOKEN=ya29....(expira em 1h — renovar via refresh token)
GOOGLE_CALENDAR_ID=primary
```
> Recomendação p/ produção: em vez de token manual, criar uma **conta de serviço** e compartilhar o calendário com o e-mail dela — assim o servidor autentica sozinho.

---

## 4. CMS — publicar conteúdo

**O que a tool faz:** manda um `POST` com `{title, content, status}` para o endpoint REST do CMS, com um **token Bearer**.
**Depende de qual CMS o cliente usa.** A tool é genérica (endpoint + chave). Exemplos:

- **Ghost / Strapi / Contentful / headless CMS** (usam Bearer token nativamente):
  - `CMS_API_URL` = o endpoint de criação de post (ex.: `https://cms.cliente.com/api/posts`).
  - `CMS_API_KEY` = o **API token** gerado no painel do CMS (em *Settings → API Keys / Tokens*).
- **WordPress** (padrão usa **Application Password** com Basic Auth, não Bearer):
  - Endpoint: `https://site.com/wp-json/wp/v2/posts`.
  - Gere uma **Application Password** (Usuário → Perfil → *Application Passwords*).
  - ⚠️ WordPress usa **Basic Auth** (usuário:senha), enquanto a tool envia **Bearer**. Para WordPress, use um **plugin de JWT** (ex.: *JWT Authentication for WP REST API*) que aceita Bearer, OU me peça que eu adapto a `cms_api_tool` para Basic Auth do WordPress.
- **Custo:** depende do CMS (WordPress/Ghost self-hosted = grátis; Contentful/serviços gerenciados têm planos pagos).

```
CMS_API_URL=https://cms.cliente.com/api/posts
CMS_API_KEY=(token gerado no painel do CMS)
```

---

## 5. E-mail (SMTP) — `email_sender_tool`

**O que a tool faz:** envia e-mail via SMTP.
**Opção A — Gmail (rápido para testar):**
1. Ative a **verificação em 2 etapas** na conta Google (obrigatório).
2. Vá em **https://myaccount.google.com/apppasswords** → gere uma **Senha de app** (16 caracteres).
3. Preencha:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seuemail@gmail.com
SMTP_PASSWORD=(a senha de app de 16 caracteres — NÃO a senha normal)
SMTP_FROM=seuemail@gmail.com
```
- **Custo:** grátis, mas o Gmail tem **limite diário** de envios (~500). Para volume, use um provedor transacional.

**Opção B — Provedor transacional (recomendado p/ produção):** SendGrid, Mailgun, Amazon SES, Brevo.
- Crie conta (têm **plano gratuito** com limite mensal; acima disso é pago), verifique seu domínio, pegue as credenciais SMTP do painel e preencha `SMTP_HOST/PORT/USER/PASSWORD/FROM` com os dados que eles fornecem.

---

## 6. Embeddings — `embedding_tool`

**O que a tool faz:** transforma texto em vetor (para busca semântica).
- **Opção A — LM Studio local (grátis, sem chave):** já é o padrão. Carregue um modelo de embeddings no LM Studio e aponte:
```
EMBEDDINGS_API_BASE=http://192.168.1.115:1234/v1
EMBEDDINGS_MODEL=text-embedding-nomic-embed-text-v1.5
```
- **Opção B — OpenAI (pago, por uso):** crie conta em https://platform.openai.com/, gere uma **API key**, e use:
```
EMBEDDINGS_API_BASE=https://api.openai.com/v1
EMBEDDINGS_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-...(a chave)
```
- **Custo:** LM Studio local = **grátis**. OpenAI = **pago por token** (embeddings são baratos).

---

## 7. Busca vetorial — `vector_search_tool`

**O que a tool faz:** embeda a consulta e ranqueia por similaridade os textos de uma **tabela do seu banco**.
**Não precisa de credencial externa** — só apontar para a tabela:
```
VECTOR_TABLE=nome_da_tabela        (ex.: base_conhecimento)
VECTOR_TEXT_COL=texto              (coluna com o texto a indexar)
VECTOR_ID_COL=id                   (coluna identificadora)
```
- **Custo:** nenhum (usa seu próprio banco + o `embedding_tool` acima).

---

## 🧪 Testar ANTES de ter as credenciais — modo Simulação

Você **não precisa** de credencial para testar o fluxo. Ligue o modo de simulação:

```
SIMULATE_EXTERNAL=true
```

Com isso, as tools externas (LinkedIn, Instagram, Google Calendar, CMS) e o e-mail **não chamam a
API real** — retornam um resultado **claramente rotulado como simulado**, mostrando o que *seria*
enviado. Exemplo do retorno:

```json
{
  "status": "simulado",
  "tool": "linkedin_api_tool",
  "message": "[SIMULAÇÃO] publicaria este post no LinkedIn — nenhuma ação externa REAL foi executada...",
  "preview": "Novo case da Quântica no ar!"
}
```

- É **opt-in e transparente** (status `simulado`) — **não** é um mock silencioso: você sempre sabe que
  foi simulado.
- Quando tiver as credenciais, é só **apagar/definir `SIMULATE_EXTERNAL=false`** e preencher as
  variáveis reais → as tools passam a agir de verdade.
- Sem simulação e sem credencial, a tool **falha explícito** dizendo qual variável preencher.

**Resumo dos 3 estados de cada tool:**
| `SIMULATE_EXTERNAL` | Credencial no `.env` | Comportamento |
|---|---|---|
| `true` | tanto faz | retorna **"simulado"** (com preview) |
| vazio/`false` | ausente | **falha explícito** ("preencha X") |
| vazio/`false` | preenchida | **ação real** (chama a API) |

---

## Como aplicar (depois de obter as credenciais)

1. Edite o arquivo **`ws-server/.env`** do app gerado.
2. Preencha as variáveis das integrações que você quer ativar (deixe em branco as que não usar).
3. **Reinicie o ws-server.** Pronto — as tools correspondentes passam a funcionar de verdade.
4. Enquanto uma variável estiver **vazia**, a tool falha com uma mensagem clara dizendo **exatamente qual variável preencher** (nunca inventa resultado).

## O que EU (LangNet) preciso de você
Só os **valores** acima — não preciso das suas senhas de painel, só dos **tokens/URLs finais** que os passos geram. Me passe (ou cole no `.env`) e as integrações ficam ativas. Se algum serviço tiver um fluxo diferente (ex.: WordPress em Basic Auth, ou Google via conta de serviço), me avise que eu **adapto a tool** correspondente.

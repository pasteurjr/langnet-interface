# -*- coding: utf-8 -*-
"""V15 — a V14 inteira (incluindo o título da lâmina 4 editado pelo autor) mais:
1. figuras da apresentação-base nas lâminas dos algoritmos de Machine Learning;
2. na lâmina de redes convolucionais, a figura da arquitetura (camadas convolucionais, pooling,
   flatten, camada densa) junto com a do caminho da imagem."""
import copy

B6_ = "Engenharia de contexto"

HIST = "Histórico da IA-70 anos em 1 minuto"

FIG = {
    "K Vizinhos Mais Próximos": "diagrams_v15/knn.png",
    "Regressão Linear": "diagrams_v15/reg_linear.png",
    "Regressão Logística": "diagrams_v15/reg_logistica.png",
    "Árvore de Decisão": "diagrams_v15/arvore.png",
    "Random Forest — Floresta Aleatória": "diagrams_v15/floresta.png",
    "Máquina de Vetores de Suporte": "diagrams_v15/svm.png",
    "K-Means — K Médias": "diagrams_v15/kmeans.png",
}


def _acha(S, titulo):
    for i, s in enumerate(S):
        if s.get("titulo") == titulo:
            return i
    raise KeyError(titulo)


def aplicar(v14):
    S = copy.deepcopy(v14)
    S[_acha(S, "Histórico da IA")]["titulo"] = HIST          # edição do autor na V14
    for t, img in FIG.items():
        s = S[_acha(S, t)]
        s["tipo"] = "algoritmo_fig"
        s["imagem"] = img
    c = S[_acha(S, "Redes convolucionais: o caminho da imagem")]
    c["tipo"] = "figuras2"
    c["imagens"] = [("O caminho da imagem", c["imagem"], 2.15), ("A arquitetura", "diagrams_v15/cnn_arquitetura.png", 2.6)]
    # 3. panoramas com a comparação de desempenho por tarefa (pesquisa de 29/09/2026)
    pr = S[_acha(S, "Panorama: modelos proprietários")]
    pr["tipo"] = "tabela2"
    pr["larguras"] = [2.0, 2.1, 6.6, 1.43]
    pr["comparacao"] = {
        "titulo": "Quem é melhor em quê",
        "colunas": ["Tarefa (medida)", "Melhor", "2º lugar", "Placar"],
        "larguras": [3.2, 2.05, 2.05, 4.83],
        "linhas": [
            ["*Geração de código (Terminal-Bench 4.0)", "Claude Opus 5.5", "GPT-6 Astra", "Opus 5.5 66,4 · GPT-6 Astra 57,9 · Fable 5.1 55,8 · Grok 4.7 38,0"],
            ["*Trabalho de escritório (GDPval, Elo)", "Claude Opus 5.5", "Claude Fable 5.1", "Opus 5.5 1846 · Fable 5.1 1735 · Grok 4.7 1695 · GPT-6 Astra 1542"],
            ["*Planilhas (ranking para Excel)", "Claude Opus 5.5", "Claude Fable 5.1", "à frente de Fable 5.1 e GPT-6 Astra"],
            ["*Produção de texto (EQ-Bench, escrita)", "Claude", "GPT-5.6 Sol", "Opus 5 lidera (2121) · GPT-5.6 Sol 1963"],
            ["*Interpretação e conhecimento (HLE)", "Claude Opus 5.5", "Claude Fable 5.1", "Opus 5.5 67,7 · Fable 5.1 65,6 · GPT-6 Astra 57,2"],
            ["*Raciocínio científico (GPQA Diamond)", "GPT-6 Astra", "Gemini 3.8 Flash", "Astra 96,0 · Gemini 3.8 Flash 95,3"],
            ["*Matemática (FrontierMath nível 4)", "GPT-6 Astra", "Claude Fable 5.1", "Astra 97,6 · Fable 5.1 87,8"],
        ],
        "nota": "Placares divulgados pelos fabricantes e por Artificial Analysis, EQ-Bench e BenchLM — em 29/09/2026. Mudam todo mês.",
    }
    ab = S[_acha(S, "Panorama: modelos abertos")]
    ab["tipo"] = "tabela2"
    ab["comparacao"] = {
        "titulo": "Quem é melhor em quê",
        "colunas": ["Tarefa (medida)", "Melhor", "2º lugar", "Placar"],
        "larguras": [3.2, 2.05, 2.05, 4.83],
        "linhas": [
            ["*Geração de código (SWE-bench)", "DeepSeek V4-Pro", "DeepSeek V4.1-Flash", "V4-Pro 80,6 (Verified) · V4.1-Flash 74,2 (DeepSWE) · Qwen3.8-Max 67,7 (Pro)"],
            ["*Raciocínio científico (GPQA Diamond)", "Kimi K3", "Qwen3.8-Max", "Kimi K3 93,5 · Qwen3.8-Max 92,7 · V4.1-Flash 90,9 · V4-Pro 90,1"],
            ["*Planilhas (SpreadsheetBench)", "Kimi K3", "MiniMax M3", "Kimi K3 34,8 no v2 (o mais difícil) · MiniMax M3 lidera o v1 (0,893)"],
            ["*Produção de texto (EQ-Bench, escrita)", "Kimi K3", "—", "2º lugar geral (2071), atrás só do Claude Opus 5"],
            ["*Custo e velocidade", "DeepSeek V4.1-Flash", "—", "só 8 a 16B ativos; supera o V4-Pro, bem maior"],
            ["*Rodar dentro de casa", "Qwen3.8-27B", "—", "Apache-2.0, cabe numa placa de 24 GB"],
        ],
        "nota": "Placares divulgados pelos fabricantes e por Artificial Analysis, EQ-Bench e SpreadsheetBench — em 29/09/2026.",
    }
    # 4. vídeos gravados (curso_engenharia_ia_sdd, pastas 01 a 11): conteúdo tirado dos roteiros
    def vid(titulo, **kw):
        v = S[_acha(S, titulo)]
        v.update(kw)
        return v

    def novo(bloco, chapeu, titulo, minutos, resumo, percurso, pasta):
        return {"tipo": "video", "bloco": bloco, "chapeu": chapeu, "titulo": titulo, "minutos": minutos,
                "resumo": resumo, "percurso": percurso, "pasta": pasta, "fala": ""}

    vid("O pipeline de Machine Learning, do início ao fim", minutos=16, pasta="01_pipeline_machine_learning",
        resumo="o notebook executando as seis etapas sobre exames de câncer de mama",
        percurso=["A base real: exames de câncer de mama, benigno ou maligno",
                  "Preparar e visualizar: estatísticas, histogramas e matriz de espalhamento",
                  "Separar treino e teste",
                  "Escolher o modelo com validação cruzada",
                  "Treinar e avaliar: precisão, recall, F-score e matriz de confusão",
                  "Prever um caso novo e comparar os modelos"])
    vid("Treinamento e Transfer Learning", minutos=10, pasta="03_deep_learning_covid_ct",
        resumo="COVID-19 em tomografias, com uma rede pré-treinada",
        percurso=["O problema: tomografia de pulmão, COVID-19 ou normal",
                  "Treino, validação e teste, carregados com tf.data",
                  "Aumento de dados e normalização",
                  "Transfer learning: a VGG16 congelada e uma cabeça nova",
                  "Treinar, e depois fazer o ajuste fino",
                  "Avaliar (recall, precisão, especificidade) e prever novas tomografias"])
    vid("Classificação e apoio à decisão em saúde", minutos=7, pasta="02_ia_na_medicina",
        resumo="diagnóstico, avaliação, prognóstico e tratamento, com dados reais",
        percurso=["Diagnóstico por imagem: raio-X de tórax com uma DenseNet121 treinada",
                  "Onde o modelo olhou: o Grad-CAM",
                  "Avaliar o teste: curva ROC, prevalência, incerteza e calibração",
                  "Prognóstico no ensaio ACTG 175 (HIV): Kaplan-Meier e modelo de Cox",
                  "Tratamento: o T-learner estima o benefício para cada paciente"])
    vid("Criação da estrutura de um Transformer", minutos=11, pasta="04_transformer_llm_do_zero",
        resumo="construindo um LLM do tipo GPT, do zero",
        percurso=["Tokenização: o tokenizador do GPT-2 e a janela deslizante",
                  "Atenção: query, key e value, máscara causal e várias cabeças",
                  "A arquitetura GPT: normalização, GELU, feed-forward, atalhos e o bloco transformer",
                  "Pré-treino: gerar texto, medir o erro e carregar os pesos oficiais do GPT-2",
                  "Ajuste fino para classificar mensagens",
                  "Ajuste fino para seguir instruções, avaliado pelo Llama 3"])
    vid("O pipeline completo do LangNet, do documento à aplicação", pasta="09_langnet_sdd")

    i = _acha(S, "Criação da estrutura de um Transformer")
    S.insert(i + 1, novo(4, "Modelos de linguagem", "Fine-tuning com LoRA: um modelo de 7B sobre infecção", 4,
        "o Llama-2-7b ajustado numa única GPU", 
        ["LoRA: os pesos congelados e duas matrizes finas treinadas",
         "QLoRA: o modelo em 4 bits, para caber numa única GPU",
         "Os principais parâmetros e o dataset de controle de infecção",
         "Antes e depois do ajuste, com uma medida objetiva"], "08_fine_tuning_lora"))
    i = _acha(S, "RAG na prática")
    S.insert(i + 1, novo(6, B6_, "RAG: um assistente de controle de infecção hospitalar", 6,
        "busca nos documentos e responde com as fontes",
        ["A base de conhecimento: epidemiologia hospitalar e infectologia",
         "Dividir em trechos e gerar os embeddings",
         "O índice FAISS e a busca",
         "Gerar a resposta com as fontes, usando o DeepSeek",
         "Sem RAG e com RAG, lado a lado",
         "Um cálculo, e uma pergunta fora da base"], "07_rag"))
    i = _acha(S, "Outros: OpenAI Agents SDK e Claude Agent SDK")
    S[i + 1:i + 1] = [
        novo(7, "Frameworks", "Agentes com CrewAI: qualificação de leads e e-mail de vendas", 10,
             "cinco agentes em duas equipes, ligadas por um Flow",
             ["O lead: os agentes pesquisam a pessoa e a empresa, e dão uma nota",
              "Agentes e tarefas declarados em YAML",
              "Saída estruturada com Pydantic, e a busca no Google como ferramenta",
              "O Flow: o roteiro que liga as duas equipes",
              "A execução: cada agente trabalhando, a nota, o e-mail final, os tokens e o custo",
              "Indo além: router, and_ e or_ no Flow"], "05_agentes_crewai"),
        novo(7, "Frameworks", "AutoGen: residente e infectologista revisam pareceres da CCIH", 4,
             "dois agentes conversando até o parecer ser aprovado",
             ["Dois agentes com o DeepSeek: o residente dá o parecer, o infectologista confere",
              "O protocolo da CCIH, e uma ferramenta para as contas exatas",
              "A regra de parada: APROVADO encerra a conversa",
              "Três casos: infecção por cateter, multirresistência e aumento do indicador"], "06_agentes_autogen")]
    i = _acha(S, "O pipeline completo do LangNet, do documento à aplicação")
    S[i + 1:i + 1] = [
        novo(11, "Validação", "App de validação rápida", 3,
             "o sistema executa os casos de uso sozinho, e o validador decide",
             ["Criar o teste: projeto, sprint e casos de uso",
              "O executor abre o sistema e preenche tudo sozinho",
              "O painel de cada passo: antes e depois, e a conferência automática",
              "O validador observa, aprova ou reprova",
              "O relatório final, em Markdown, Word ou PDF"], "10_app_validacao_rapida"),
        novo(11, "Validação", "App de validação: documentos e trilha de correções", 7,
             "toda a documentação do projeto e a validação num só lugar",
             ["Requisitos, casos de uso e planejamento, com todas as versões",
              "Os vídeos de cada caso de uso, gerados executando o sistema",
              "O Tutorial Guiado: o validador executa, dita por voz e redige com IA",
              "A trilha de correções: cada observação volta como correção",
              "Justificativas, notificações e monitor ao vivo",
              "Falar com o Claude, e validar em paralelo"], "11_app_validacao_documentos")]
    # 5. fine-tuning em detalhe, logo depois da escada da adaptação
    i = _acha(S, "A escada da adaptação")
    S.insert(i + 1, {
        "tipo": "figura", "bloco": 4, "chapeu": "Modelos de linguagem", "titulo": "Fine-tuning de modelos",
        "destaque": "Continuar o treino de um modelo pronto com exemplos do seu domínio.",
        "imagem": "diagrams_v15/lora.png", "lado": "esquerda", "larg": 6.9,
        "cartoes": [("Como se faz", "centenas a milhares de pares pergunta → resposta; poucas épocas; confere-se antes e depois."),
                    ("LoRA", "congela os pesos e treina duas matrizes finas: menos de 1% dos parâmetros."),
                    ("QLoRA", "o modelo em 4 bits: um 7B cabe numa única GPU.", "good")],
        "fala": ""})
    # 6. sai a lâmina de vídeo sem gravação correspondente (pedido do autor, 29/09)
    del S[_acha(S, "Um sistema multiagente com resultado verificável")]
    # 7. ordem pedida pelo autor (30/09): vídeo de RAG no fim do bloco, depois de "Saída estruturada e proteções";
    #    app de validação (documentos) antes do app de validação rápida
    r = S.pop(_acha(S, "RAG: um assistente de controle de infecção hospitalar"))
    S.insert(_acha(S, "Saída estruturada e proteções") + 1, r)
    d = S.pop(_acha(S, "App de validação: documentos e trilha de correções"))
    S.insert(_acha(S, "App de validação rápida"), d)
    return S

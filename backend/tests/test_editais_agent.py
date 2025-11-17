"""
Teste Unitário Completo - Sistema de Análise de Editais
Testa o pipeline LangNet com documentos reais de editais usando DeepSeek
"""
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.langnetagents import execute_document_analysis_workflow
from agents.langnetstate import LangNetFullState, init_full_state
from services.memory_service import AgentMemoryService
from utils.pdf_processor import process_pdf_for_agent


# ============================================================================
# CONFIGURAÇÃO DO TESTE
# ============================================================================

EDITAIS_DIR = "/home/pasteurjr/progreact/langnet-interface/instancias/editais"
TEST_PROJECT_ID = "test-editais-001"
TEST_PROJECT_NAME = "Sistema de Seleção e Análise de Editais"

# Instruções detalhadas sobre o sistema
SYSTEM_INSTRUCTIONS = """
PROPOSTA DE ARQUITETURA DO SISTEMA DE IA PARA LICITAÇÕES:

1. Cadastro Inteligente do Portfólio:
   - Criação de uma máscara de entrada totalmente parametrizável
   - A empresa informa as características técnicas dos produtos por classe, seguindo os critérios normalmente avaliados nos certames
   - A IA também realiza a leitura dos manuais técnicos e sugere novos campos ou requisitos faltantes para enriquecer o cadastro

2. Agente de IA para Captura e Leitura dos Certames:
   - Um agente autônomo monitora diariamente as fontes públicas (federal, estaduais e municipais) e captura novos editais
   - O sistema lê o edital, interpreta cláusulas técnicas e administrativas e calcula automaticamente o grau de aderência de cada item aos produtos cadastrados

3. Sugestão de Participação:
   - Com base na análise do edital, a IA identifica quais produtos da empresa são aderentes e recomenda a participação
   - O agente também lista os requisitos técnicos, administrativos e documentais que precisam compor a proposta e os anexos obrigatórios

4. Geração Automática da Proposta:
   - A IA monta automaticamente a proposta completa:
     * texto técnico aderente ao edital
     * documentos oficiais e complementares
     * fichas técnicas e anexos
     * arquivo final organizado para envio eletrônico ou impressão (para licitações presenciais)
   - Um painel de revisão permite ajustes antes do envio

CONTEXTO DO SISTEMA:

Você está analisando documentos para criar um Sistema Inteligente de Seleção e Análise de Editais de Licitação.

OBJETIVOS DO SISTEMA:
1. **Captação Automática de Editais**: Monitorar portais públicos (ComprasNet, Licitações-e, portais estaduais/municipais)
   para identificar novos editais relevantes para a empresa.

2. **Análise Inteligente**: Extrair informações críticas dos editais:
   - Tipo de licitação (Pregão Eletrônico, Concorrência, Tomada de Preços, etc.)
   - Objeto da licitação (descrição do que está sendo contratado)
   - Valor estimado e limites orçamentários
   - Prazo de entrega/execução
   - Documentação de habilitação exigida
   - Critérios de julgamento (menor preço, melhor técnica, técnica e preço)
   - Exigências técnicas específicas
   - Garantias e seguros necessários
   - Prazos críticos (entrega de propostas, sessão pública)

3. **Classificação de Viabilidade**: Avaliar automaticamente se a empresa tem condições de participar:
   - Capacidade técnica (histórico, atestados)
   - Capacidade financeira (balanços, capital social)
   - Conformidade documental (certidões, registros)
   - Adequação ao objeto (produtos/serviços oferecidos)
   - Prazo realista de preparação da proposta

4. **Gestão de Requisitos**: Extrair e estruturar requisitos:
   - Requisitos funcionais (o que o sistema deve fazer)
   - Requisitos não-funcionais (performance, segurança, disponibilidade)
   - Regras de negócio (Lei 14.133/2021, decretos, instruções normativas)
   - Conformidade legal (LGPD, acessibilidade, transparência)

5. **Alertas e Notificações**: Sistema de alerta para:
   - Editais que atendem ao perfil da empresa
   - Prazos se aproximando
   - Mudanças em editais monitorados
   - Resultados de licitações participadas

6. **Análise de Concorrência**: Identificar:
   - Empresas que costumam participar
   - Padrões de preços vencedores
   - Taxa de sucesso por tipo de licitação

INFORMAÇÕES IMPORTANTES A EXTRAIR DOS DOCUMENTOS:

1. **Processos de Licitação**:
   - Etapas do processo licitatório (da publicação ao contrato)
   - Documentos obrigatórios em cada fase
   - Prazos legais e procedimentais
   - Recursos e impugnações

2. **Critérios de Habilitação**:
   - Habilitação jurídica (CNPJ, contrato social, inscrições)
   - Regularidade fiscal (federal, estadual, municipal, trabalhista)
   - Qualificação técnica (atestados, certidões, registros profissionais)
   - Qualificação econômico-financeira (balanços, índices)
   - Garantias de proposta e execução

3. **Nova Lei de Licitações (Lei 14.133/2021)**:
   - Mudanças em relação à Lei 8.666/93
   - Novos procedimentos e modalidades
   - Uso obrigatório de meios eletrônicos
   - Portal Nacional de Contratações Públicas (PNCP)

4. **Boas Práticas**:
   - Análise estratégica de editais
   - Montagem de propostas vencedoras
   - Gestão de prazos e documentação
   - Evitar erros comuns (inabilitação, desclassificação)

5. **Planilhas de Custos**:
   - Estrutura de composição de preços
   - Custos diretos e indiretos
   - BDI (Bonificação e Despesas Indiretas)
   - Encargos sociais e trabalhistas

REQUISITOS TÉCNICOS ESPERADOS:

- **Backend**: API REST, processamento assíncrono, web scraping, NLP
- **Banco de Dados**: Armazenamento de editais, empresas, propostas, histórico
- **Machine Learning**: Classificação de editais, extração de entidades, pontuação de viabilidade
- **Integrações**: Portais de licitação, Receita Federal (CNPJs), Serasa (certidões)
- **Frontend**: Dashboard, alertas, visualização de editais, geração de relatórios
- **Segurança**: Autenticação, criptografia, auditoria, LGPD

COMPLEMENTAÇÃO COM WEB RESEARCH:

Por favor, busque na web informações sobre:
1. Melhores práticas em análise de editais de licitação (2024)
2. Principais portais de licitação no Brasil
3. Ferramentas de automação para licitações
4. API do Portal Nacional de Contratações Públicas (PNCP)
5. Requisitos da Lei 14.133/2021 (Nova Lei de Licitações)
6. Tecnologias de NLP para extração de informações de editais
7. Conformidade com LGPD em sistemas de licitações
8. Integrações com sistemas governamentais (Serpro, Receita Federal)
"""


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_pdf_files():
    """Lista todos os PDFs na pasta de editais"""
    pdf_files = list(Path(EDITAIS_DIR).glob("*.pdf"))
    return sorted(pdf_files)


def parse_nested_json(data, key_path="team_result"):
    """
    Parse JSON that may be wrapped in team_result and/or markdown code fences.
    Handles formats like:
    1. '{"team_result": "..."}'
    2. '{"team_result": "```json\n{...}\n```"}'
    3. Direct JSON objects
    """
    if not data:
        return {}

    # If already a dict, return as-is
    if isinstance(data, dict):
        # Check if it has team_result key
        if "team_result" in data:
            data = data["team_result"]
        else:
            return data

    # If string, try to parse
    if isinstance(data, str):
        try:
            # First parse: get outer JSON
            parsed = json.loads(data)

            # Extract team_result if present
            if isinstance(parsed, dict) and "team_result" in parsed:
                inner_str = parsed["team_result"]

                # Remove markdown code fence if present
                if isinstance(inner_str, str):
                    inner_str = inner_str.strip()
                    if inner_str.startswith("```json"):
                        inner_str = inner_str[7:]  # Remove ```json
                    if inner_str.startswith("```"):
                        inner_str = inner_str[3:]  # Remove ```
                    if inner_str.endswith("```"):
                        inner_str = inner_str[:-3]  # Remove trailing ```
                    inner_str = inner_str.strip()

                    # Second parse: get actual data
                    try:
                        return json.loads(inner_str)
                    except:
                        return {}
                return inner_str if isinstance(inner_str, dict) else {}
            return parsed
        except Exception as e:
            print(f"   ⚠️  JSON parse error: {str(e)[:100]}")
            return {}

    return {}


def format_duration(seconds):
    """Formata duração em minutos e segundos"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}m {secs}s"


def save_result(result_data, output_file):
    """Salva resultado em arquivo JSON"""
    output_path = Path(__file__).parent / "results" / output_file
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    return output_path


def save_requirements_document(markdown_content, output_file):
    """Salva documento de requisitos em MD"""
    output_path = Path(__file__).parent / "results" / output_file
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return output_path


# ============================================================================
# TESTES UNITÁRIOS
# ============================================================================

def test_single_document(pdf_path: Path, use_deepseek: bool = True):
    """
    Testa análise de um único documento

    Args:
        pdf_path: Caminho para o PDF
        use_deepseek: Se True, usa DeepSeek; se False, usa OpenAI

    Returns:
        dict com resultados do teste
    """
    print(f"\n{'='*80}")
    print(f"TESTE: {pdf_path.name}")
    print(f"LLM: {'DeepSeek' if use_deepseek else 'OpenAI GPT-4'}")
    print(f"{'='*80}\n")

    test_result = {
        "document_name": pdf_path.name,
        "document_path": str(pdf_path),
        "document_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
        "llm_provider": "deepseek" if use_deepseek else "openai",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "duration_seconds": 0,
        "status": "running",
        "errors": [],
        "warnings": [],
        "metrics": {},
        "state": None
    }

    start_time = time.time()

    try:
        # Criar document_id único
        document_id = f"doc-{pdf_path.stem.replace(' ', '-')[:30]}-{int(time.time())}"

        print(f"📄 Documento: {pdf_path.name} ({test_result['document_size_mb']} MB)")
        print(f"🆔 Document ID: {document_id}")
        print(f"⏱️  Início: {test_result['start_time']}")

        # ==================== NOVO: Processar PDF com chunking ====================
        print(f"\n🔧 Processando PDF (extração + chunking)...\n")
        pdf_processed = process_pdf_for_agent(
            str(pdf_path),
            max_pages=50,
            chunk_size=1000,
            chunk_overlap=200,
            max_chunks=60
        )

        # Juntar todos os chunks formatados em um único texto
        document_content_chunked = "\n\n".join(pdf_processed['formatted_chunks'])

        print(f"✅ PDF processado:")
        print(f"   📝 Texto extraído: {pdf_processed['stats']['raw_text_length']:,} chars ({pdf_processed['stats']['raw_text_words']:,} palavras)")
        print(f"   ✂️  Chunks gerados: {pdf_processed['stats']['num_formatted_chunks']}")
        print(f"   📦 Tamanho médio do chunk: {pdf_processed['stats']['avg_chunk_size']:.0f} chars")
        print(f"\n🔄 Iniciando workflow de análise...\n")
        # ==========================================================================

        # Executar workflow de análise COM TEXTO CHUNKADO
        result_state = execute_document_analysis_workflow(
            project_id=TEST_PROJECT_ID,
            document_id=document_id,
            document_path=str(pdf_path),
            document_content=document_content_chunked,  # NOVO: passar texto chunkado
            project_name=TEST_PROJECT_NAME,
            project_description="Sistema inteligente para captação, análise e gestão de editais de licitação pública",
            project_domain="Licitações e Contratações Públicas",
            additional_instructions=SYSTEM_INSTRUCTIONS,
            document_type="pdf",
            use_deepseek=use_deepseek
        )

        end_time = time.time()
        duration = end_time - start_time

        test_result["end_time"] = datetime.now().isoformat()
        test_result["duration_seconds"] = round(duration, 2)
        test_result["status"] = "completed"
        test_result["state"] = result_state

        # Extrair métricas
        # Parse requirements and research data with proper nested parsing
        requirements_data = parse_nested_json(result_state.get("requirements_json", "{}"))
        research_data = parse_nested_json(result_state.get("research_findings", "{}"))

        test_result["metrics"] = {
            "completed_tasks": result_state.get("completed_tasks", 0),
            "total_tasks": result_state.get("total_tasks", 0),
            "progress_percentage": result_state.get("progress_percentage", 0),
            "requirements_count": len(requirements_data.get("functional_requirements", [])),
            "nfr_count": len(requirements_data.get("non_functional_requirements", [])),
            "business_rules_count": len(requirements_data.get("business_rules", [])),
            "entities_count": len(requirements_data.get("entities", [])),
            "actors_count": len(requirements_data.get("actors", [])),
            "web_research_queries": len(research_data.get("queries", [])),
            "web_research_results": len(research_data.get("results", [])),
            "document_word_count": len(result_state.get("document_content", "").split()),
            "requirements_doc_length": len(result_state.get("requirements_document_md", ""))
        }

        # Verificar e reportar erros
        if result_state.get("errors"):
            print(f"\n⚠️  ERROS DETECTADOS DURANTE EXECUÇÃO: {len(result_state['errors'])}")
            for err in result_state["errors"]:
                print(f"   ❌ Task: {err.get('task', 'unknown')}")
                print(f"      Erro: {err.get('error_message', 'no message')[:200]}")
            test_result["warnings"].extend(result_state["errors"])

        # Verificar se requisitos foram extraídos
        if test_result["metrics"]["requirements_count"] == 0:
            print(f"\n⚠️  ATENÇÃO: Nenhum requisito funcional extraído!")
            if not result_state.get("errors"):
                print(f"   Possível causa: LLM não retornou JSON no formato esperado")
                print(f"   Verificar output do task 'extract_requirements'")

        # Original warnings check
        if result_state.get("errors"):
            pass  # Already handled above

        # Salvar documento de requisitos
        if result_state.get("requirements_document_md"):
            doc_filename = f"{pdf_path.stem}_requirements.md"
            doc_path = save_requirements_document(
                result_state["requirements_document_md"],
                doc_filename
            )
            test_result["requirements_document_path"] = str(doc_path)
            print(f"\n✅ Documento de requisitos salvo: {doc_path}")

        print(f"\n{'='*80}")
        print(f"✅ TESTE CONCLUÍDO COM SUCESSO")
        print(f"⏱️  Duração: {format_duration(duration)}")
        print(f"📊 Requisitos Funcionais: {test_result['metrics']['requirements_count']}")
        print(f"📊 Requisitos Não-Funcionais: {test_result['metrics']['nfr_count']}")
        print(f"📊 Regras de Negócio: {test_result['metrics']['business_rules_count']}")
        print(f"📊 Entidades: {test_result['metrics']['entities_count']}")
        print(f"📊 Atores: {test_result['metrics']['actors_count']}")
        print(f"🌐 Queries Web Research: {test_result['metrics']['web_research_queries']}")
        print(f"🌐 Resultados Web Research: {test_result['metrics']['web_research_results']}")
        print(f"{'='*80}\n")

    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time

        test_result["end_time"] = datetime.now().isoformat()
        test_result["duration_seconds"] = round(duration, 2)
        test_result["status"] = "failed"
        test_result["errors"].append({
            "type": type(e).__name__,
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        })

        print(f"\n{'='*80}")
        print(f"❌ TESTE FALHOU")
        print(f"⏱️  Duração até falha: {format_duration(duration)}")
        print(f"❌ Erro: {type(e).__name__}: {str(e)}")
        print(f"{'='*80}\n")

    return test_result


def test_multiple_documents(pdf_paths: list, use_deepseek: bool = True, limit: int = None):
    """
    Testa análise de múltiplos documentos

    Args:
        pdf_paths: Lista de caminhos para PDFs
        use_deepseek: Se True, usa DeepSeek
        limit: Limite de documentos a testar (None = todos)

    Returns:
        dict com resultados agregados
    """
    if limit:
        pdf_paths = pdf_paths[:limit]

    print(f"\n{'='*80}")
    print(f"TESTE EM LOTE: {len(pdf_paths)} documentos")
    print(f"LLM: {'DeepSeek' if use_deepseek else 'OpenAI GPT-4'}")
    print(f"{'='*80}\n")

    batch_result = {
        "test_suite": "editais_batch_test",
        "total_documents": len(pdf_paths),
        "llm_provider": "deepseek" if use_deepseek else "openai",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "total_duration_seconds": 0,
        "tests": [],
        "summary": {
            "completed": 0,
            "failed": 0,
            "total_requirements": 0,
            "total_nfr": 0,
            "total_business_rules": 0,
            "total_entities": 0,
            "total_web_queries": 0,
            "avg_duration_seconds": 0
        }
    }

    batch_start = time.time()

    for i, pdf_path in enumerate(pdf_paths, 1):
        print(f"\n📄 Testando {i}/{len(pdf_paths)}: {pdf_path.name}")

        test_result = test_single_document(pdf_path, use_deepseek)
        batch_result["tests"].append(test_result)

        # Atualizar summary
        if test_result["status"] == "completed":
            batch_result["summary"]["completed"] += 1
            batch_result["summary"]["total_requirements"] += test_result["metrics"].get("requirements_count", 0)
            batch_result["summary"]["total_nfr"] += test_result["metrics"].get("nfr_count", 0)
            batch_result["summary"]["total_business_rules"] += test_result["metrics"].get("business_rules_count", 0)
            batch_result["summary"]["total_entities"] += test_result["metrics"].get("entities_count", 0)
            batch_result["summary"]["total_web_queries"] += test_result["metrics"].get("web_research_queries", 0)
        else:
            batch_result["summary"]["failed"] += 1

        # Pausa entre testes (rate limiting)
        if i < len(pdf_paths):
            print(f"\n⏳ Aguardando 5 segundos antes do próximo teste...\n")
            time.sleep(5)

    batch_end = time.time()
    batch_duration = batch_end - batch_start

    batch_result["end_time"] = datetime.now().isoformat()
    batch_result["total_duration_seconds"] = round(batch_duration, 2)

    if batch_result["summary"]["completed"] > 0:
        total_duration_completed = sum(
            t["duration_seconds"] for t in batch_result["tests"]
            if t["status"] == "completed"
        )
        batch_result["summary"]["avg_duration_seconds"] = round(
            total_duration_completed / batch_result["summary"]["completed"], 2
        )

    return batch_result


def test_multiple_documents_consolidated(pdf_paths: list, use_deepseek: bool = False):
    """
    Testa análise de múltiplos documentos CONSOLIDADOS (1 execução do agent)

    Esta função processa todos os PDFs de uma vez, gerando um único documento
    de requisitos consolidado. É MUITO mais rápido que processar individualmente.

    Args:
        pdf_paths: Lista de caminhos para PDFs
        use_deepseek: Se True, usa DeepSeek; se False, usa OpenAI GPT-4

    Returns:
        LangNetFullState com documento consolidado
    """
    print(f"\n{'='*80}")
    print(f"TESTE CONSOLIDADO: {len(pdf_paths)} documentos em 1 execução")
    print(f"LLM: {'DeepSeek' if use_deepseek else 'OpenAI GPT-4'}")
    print(f"{'='*80}\n")

    # Listar documentos
    print(f"📋 Documentos a processar:")
    for i, pdf_path in enumerate(pdf_paths, 1):
        size_mb = round(pdf_path.stat().st_size / (1024 * 1024), 2)
        print(f"   {i}. {pdf_path.name} ({size_mb} MB)")

    print(f"\n⏳ Processando PDFs e consolidando conteúdo...")

    # Processar todos os PDFs e juntar conteúdo
    all_content_parts = []
    total_size_mb = 0

    for pdf_path in pdf_paths:
        size_mb = pdf_path.stat().st_size / (1024 * 1024)
        total_size_mb += size_mb

        print(f"   📄 Processando: {pdf_path.name}...")
        content = process_pdf_for_agent(str(pdf_path))

        # Adicionar separador claro entre documentos
        all_content_parts.append(f"""
{'='*80}
DOCUMENTO: {pdf_path.name}
TAMANHO: {size_mb:.2f} MB
{'='*80}

{content}
""")

    # Juntar todo o conteúdo
    consolidated_content = "\n\n".join(all_content_parts)

    print(f"\n✅ {len(pdf_paths)} documentos processados ({total_size_mb:.2f} MB total)")
    print(f"📊 Tamanho consolidado: {len(consolidated_content)} caracteres")
    print(f"\n🤖 Executando análise consolidada com agent...")
    print(f"⚠️  ATENÇÃO: Processamento pode levar 5-15 minutos\n")

    start_time = time.time()

    try:
        # Executar UMA VEZ com todo o conteúdo consolidado
        result_state = execute_document_analysis_workflow(
            project_id=TEST_PROJECT_ID,
            document_id=f"consolidated_{len(pdf_paths)}_docs_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            document_path=str(pdf_paths[0]),  # Path do primeiro como referência
            project_name=TEST_PROJECT_NAME,
            project_description=f"Análise consolidada de {len(pdf_paths)} documentos sobre editais de licitação",
            additional_instructions=SYSTEM_INSTRUCTIONS,
            use_deepseek=use_deepseek,
            document_content=consolidated_content,  # TODOS OS DOCUMENTOS JUNTOS
            enable_web_research=True  # HABILITADO: Pesquisa web para enriquecer requisitos
        )

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n{'='*80}")
        print(f"✅ ANÁLISE CONSOLIDADA CONCLUÍDA")
        print(f"⏱️  Duração: {format_duration(duration)}")
        print(f"{'='*80}\n")

        # Extrair métricas
        requirements_json = result_state.get("requirements_json", "{}")
        requirements_data = parse_nested_json(requirements_json)

        functional_reqs = requirements_data.get("functional_requirements", [])
        nonfunctional_reqs = requirements_data.get("non_functional_requirements", [])
        business_rules = requirements_data.get("business_rules", [])
        entities = requirements_data.get("entities", [])
        actors = requirements_data.get("actors", [])

        print(f"📊 MÉTRICAS CONSOLIDADAS:")
        print(f"   Requisitos Funcionais: {len(functional_reqs)}")
        print(f"   Requisitos Não-Funcionais: {len(nonfunctional_reqs)}")
        print(f"   Regras de Negócio: {len(business_rules)}")
        print(f"   Entidades: {len(entities)}")
        print(f"   Atores: {len(actors)}")
        print(f"\n")

        # Salvar documento consolidado
        md_path = Path(__file__).parent / "results" / "documento_requisitos_extraido.md"
        md_path.parent.mkdir(exist_ok=True)

        requirements_md = result_state.get("requirements_document_md", "")

        if requirements_md:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(requirements_md)
            print(f"📝 Documento consolidado salvo: {md_path}")
            print(f"   Tamanho: {len(requirements_md)} caracteres\n")
        else:
            print(f"⚠️  AVISO: Documento de requisitos vazio!\n")

        # Salvar JSON completo para debug
        json_path = Path(__file__).parent / "results" / f"consolidated_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_result(result_state, json_path.name)
        print(f"💾 Estado completo salvo: {json_path}\n")

        return result_state

    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time

        print(f"\n{'='*80}")
        print(f"❌ ERRO NA ANÁLISE CONSOLIDADA")
        print(f"⏱️  Duração até falha: {format_duration(duration)}")
        print(f"❌ Erro: {type(e).__name__}: {str(e)}")
        print(f"{'='*80}\n")

        raise


def generate_report(batch_result: dict):
    """Gera relatório formatado dos testes"""

    report = f"""
{'='*80}
RELATÓRIO DE TESTES - SISTEMA DE ANÁLISE DE EDITAIS
{'='*80}

📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🤖 LLM Provider: {batch_result['llm_provider'].upper()}
📄 Documentos Testados: {batch_result['total_documents']}
⏱️  Duração Total: {format_duration(batch_result['total_duration_seconds'])}

{'='*80}
RESUMO GERAL
{'='*80}

✅ Testes Concluídos: {batch_result['summary']['completed']} ({batch_result['summary']['completed']/batch_result['total_documents']*100:.1f}%)
❌ Testes Falhados: {batch_result['summary']['failed']} ({batch_result['summary']['failed']/batch_result['total_documents']*100:.1f}%)
⏱️  Duração Média: {format_duration(batch_result['summary']['avg_duration_seconds'])}

{'='*80}
MÉTRICAS AGREGADAS
{'='*80}

📊 Total de Requisitos Funcionais: {batch_result['summary']['total_requirements']}
📊 Total de Requisitos Não-Funcionais: {batch_result['summary']['total_nfr']}
📊 Total de Regras de Negócio: {batch_result['summary']['total_business_rules']}
📊 Total de Entidades Identificadas: {batch_result['summary']['total_entities']}
🌐 Total de Queries Web Research: {batch_result['summary']['total_web_queries']}

{'='*80}
RESULTADOS POR DOCUMENTO
{'='*80}

"""

    for i, test in enumerate(batch_result['tests'], 1):
        status_icon = "✅" if test['status'] == 'completed' else "❌"

        report += f"""
{i}. {status_icon} {test['document_name']}
   Tamanho: {test['document_size_mb']} MB
   Status: {test['status'].upper()}
   Duração: {format_duration(test['duration_seconds'])}
"""

        if test['status'] == 'completed':
            metrics = test['metrics']
            report += f"""   Requisitos Funcionais: {metrics.get('requirements_count', 0)}
   Requisitos Não-Funcionais: {metrics.get('nfr_count', 0)}
   Regras de Negócio: {metrics.get('business_rules_count', 0)}
   Entidades: {metrics.get('entities_count', 0)}
   Atores: {metrics.get('actors_count', 0)}
   Web Research Queries: {metrics.get('web_research_queries', 0)}
   Web Research Results: {metrics.get('web_research_results', 0)}
   Palavras no Documento: {metrics.get('document_word_count', 0):,}
   Tamanho Doc. Requisitos: {metrics.get('requirements_doc_length', 0):,} chars
"""
            if test.get('requirements_document_path'):
                report += f"   📄 Documento Requisitos: {test['requirements_document_path']}\n"
        else:
            if test.get('errors'):
                for error in test['errors']:
                    report += f"   ❌ Erro: {error['type']}: {error['message']}\n"

        report += "\n"

    report += f"""
{'='*80}
ANÁLISE DE DESEMPENHO
{'='*80}

Tempo médio por documento: {format_duration(batch_result['summary']['avg_duration_seconds'])}
Requisitos funcionais por documento: {batch_result['summary']['total_requirements']/max(batch_result['summary']['completed'], 1):.1f}
Requisitos não-funcionais por documento: {batch_result['summary']['total_nfr']/max(batch_result['summary']['completed'], 1):.1f}
Regras de negócio por documento: {batch_result['summary']['total_business_rules']/max(batch_result['summary']['completed'], 1):.1f}
Entidades por documento: {batch_result['summary']['total_entities']/max(batch_result['summary']['completed'], 1):.1f}
Queries web research por documento: {batch_result['summary']['total_web_queries']/max(batch_result['summary']['completed'], 1):.1f}

{'='*80}
CONCLUSÃO
{'='*80}

Taxa de Sucesso: {batch_result['summary']['completed']/batch_result['total_documents']*100:.1f}%
Qualidade: {"EXCELENTE ✅" if batch_result['summary']['completed']/batch_result['total_documents'] > 0.9 else "BOA ✅" if batch_result['summary']['completed']/batch_result['total_documents'] > 0.7 else "REGULAR ⚠️" if batch_result['summary']['completed']/batch_result['total_documents'] > 0.5 else "BAIXA ❌"}
Performance: {"EXCELENTE ✅" if batch_result['summary']['avg_duration_seconds'] < 180 else "BOA ✅" if batch_result['summary']['avg_duration_seconds'] < 300 else "REGULAR ⚠️" if batch_result['summary']['avg_duration_seconds'] < 420 else "BAIXA ❌"}

{'='*80}
FIM DO RELATÓRIO
{'='*80}
"""

    return report


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Executa suíte de testes"""

    print(f"\n{'='*80}")
    print("SUÍTE DE TESTES - SISTEMA DE ANÁLISE DE EDITAIS")
    print(f"{'='*80}\n")

    # Listar PDFs disponíveis
    pdf_files = get_pdf_files()

    print(f"📂 Pasta de editais: {EDITAIS_DIR}")
    print(f"📄 PDFs encontrados: {len(pdf_files)}")
    print(f"\n📋 Lista de documentos:")
    for i, pdf in enumerate(pdf_files, 1):
        size_mb = round(pdf.stat().st_size / (1024 * 1024), 2)
        print(f"   {i}. {pdf.name} ({size_mb} MB)")

    # Selecionar 2 documentos para teste consolidado (mais relevantes para o contexto de sistema de IA para licitações)
    selected_names = [
        "Análise estratégica de edital passo a passo - eLicitação.pdf",  # Análise e leitura de editais
        "Manual de Licitacoes para Micro e Pequenas Empresas.pdf"  # Manual completo sobre licitações
    ]
    test_pdfs = [pdf for pdf in pdf_files if pdf.name in selected_names]

    if len(test_pdfs) < 2:
        print(f"\n⚠️  AVISO: Apenas {len(test_pdfs)} dos 2 documentos selecionados foram encontrados")
        if len(test_pdfs) == 0:
            print(f"❌ ERRO: Nenhum documento encontrado!")
            return

    print(f"\n🧪 Testando {len(test_pdfs)} documento(s) CONSOLIDADO(S) com GPT-4o-mini...")
    print(f"\n⚠️  NOTA: Análise consolidada pode levar 5-15 minutos (mais rápido que individual!)\n")

    # Confirmar antes de continuar
    import sys
    if "--yes" in sys.argv or "-y" in sys.argv:
        print("\n▶️  Executando testes automaticamente...")
    else:
        try:
            response = input("Deseja continuar? (s/n): ")
            if response.lower() != 's':
                print("\n❌ Teste cancelado pelo usuário")
                return
        except EOFError:
            print("\n▶️  Input não disponível, executando automaticamente...")
            pass

    # Executar teste CONSOLIDADO (1 execução para todos os documentos)
    result_state = test_multiple_documents_consolidated(test_pdfs, use_deepseek=False)

    print(f"\n{'='*80}")
    print(f"✅ TESTE CONSOLIDADO FINALIZADO")
    print(f"📝 Documento de requisitos salvo em:")
    print(f"   tests/results/documento_requisitos_extraido.md")
    print(f"{'='*80}\n")

    return result_state


if __name__ == "__main__":
    main()

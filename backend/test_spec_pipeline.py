"""
Test script for the specification generation pipeline
Tests the 6-step CrewAI workflow following Generative Computing principles
"""
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_connection
from agents.langnetagents import execute_specification_workflow

def main():
    print("\n" + "="*80)
    print("🧪 TESTE DO PIPELINE DE ESPECIFICAÇÃO (7 Steps CrewAI)")
    print("="*80 + "\n")

    # 1. Load the latest requirements document
    print("📄 Carregando último documento de requisitos...")

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # Get the latest requirements version (simple query without JOIN)
        cursor.execute("""
            SELECT session_id, version, requirements_document, created_at, change_type
            FROM session_requirements_version
            ORDER BY created_at DESC
            LIMIT 1
        """)

        req_data = cursor.fetchone()

        if not req_data:
            print("❌ Nenhum documento de requisitos encontrado!")
            return

        cursor.close()

    requirements_document = req_data['requirements_document']
    requirements_version = req_data['version']
    requirements_created_at = req_data['created_at'].strftime('%Y-%m-%d') if req_data['created_at'] else datetime.now().strftime('%Y-%m-%d')
    project_id = "test-project"
    project_name = "Sistema de Teste"

    print(f"✅ Requisitos carregados:")
    print(f"   - Session: {req_data['session_id']}")
    print(f"   - Versão: {requirements_version}")
    print(f"   - Tamanho: {len(requirements_document)} caracteres")
    print(f"   - Projeto: {project_name}")
    print(f"   - Criado em: {requirements_created_at}")
    print()

    # 2. Execute the specification workflow
    print("🚀 Iniciando pipeline de especificação (7 steps)...")
    print("   Pipeline: Router → EntityExtractor → WebResearcher → Composer → Verifier → Compliance → Formatter")
    print()

    def verbose_callback(message: str):
        """Callback for progress updates"""
        print(f"   {message}")

    try:
        final_state = execute_specification_workflow(
            project_id=project_id,
            requirements_document=requirements_document,
            requirements_version=requirements_version,
            requirements_created_at=requirements_created_at,
            project_name=project_name,
            detail_level="detailed",
            target_audience="mixed",
            use_deepseek=False,
            verbose_callback=verbose_callback
        )

        # 3. Analyze results
        print("\n" + "="*80)
        print("📊 RESULTADOS DO TESTE")
        print("="*80 + "\n")

        spec_document = final_state.get('spec_document_md', '')

        if not spec_document:
            spec_document = final_state.get('spec_draft_document_md', '')
            if spec_document:
                print("⚠️  Usando documento draft (formatação final pode ter falhado)")

        print(f"Status: {final_state.get('spec_status', 'unknown')}")
        print(f"Documento gerado: {len(spec_document)} caracteres")
        print(f"Grounding score: {final_state.get('spec_grounding_score_final', 'N/A')}")
        print(f"Compliance score: {final_state.get('spec_compliance_score_final', 'N/A')}")
        print(f"Total seções: {final_state.get('spec_total_sections', 'N/A')}")
        print(f"Seções completas: {final_state.get('spec_complete_sections', 'N/A')}")

        gaps = final_state.get('spec_final_gaps', [])
        warnings = final_state.get('spec_warnings', [])
        errors = final_state.get('errors', [])

        if gaps:
            print(f"\n⚠️  Gaps encontrados: {len(gaps)}")
            for gap in gaps[:5]:
                print(f"   - {gap}")

        if warnings:
            print(f"\n⚠️  Warnings: {len(warnings)}")
            for warn in warnings[:5]:
                print(f"   - {warn}")

        if errors:
            print(f"\n❌ Erros: {len(errors)}")
            for err in errors[:5]:
                print(f"   - {err}")

        # 4. Save document to file for review
        if spec_document:
            output_file = f"/tmp/spec_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(spec_document)
            print(f"\n📁 Documento salvo em: {output_file}")

            # Count sections
            section_count = spec_document.count('## ')
            print(f"📋 Seções encontradas no documento: {section_count}")

            # Show first 500 chars
            print(f"\n📝 Preview (primeiros 500 chars):")
            print("-"*40)
            print(spec_document[:500])
            print("-"*40)
        else:
            print("\n❌ Nenhum documento foi gerado!")

        print("\n✅ Teste concluído!")

    except Exception as e:
        import traceback
        print(f"\n❌ ERRO DURANTE O TESTE: {e}")
        print("\nTraceback completo:")
        traceback.print_exc()

if __name__ == "__main__":
    main()

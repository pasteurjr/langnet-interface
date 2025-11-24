"""
LangNet Agents Implementation
Based on tropicalagentssalesv6.py Context State List pattern

This module implements the complete multi-agent system for LangNet:
- Document analysis and requirements extraction
- Agent and task design
- Workflow modeling with Petri Nets
- YAML and code generation

Pattern: Context State List + Task Registry + Input/Output Functions
"""
import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# Add framework to path
framework_path = Path(__file__).parent.parent.parent / "framework"
sys.path.insert(0, str(framework_path))

# Import framework components
from frameworkagentsadapterv4 import FrameworkAdapterFactory
from langchain_openai import ChatOpenAI

# Import LangNet components
from .langnetstate import (
    LangNetFullState,
    init_full_state,
    log_task_start,
    log_task_complete,
    log_task_error
)
from .langnettools import create_langnet_tools


# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


# Load agent and task configurations
CONFIG_DIR = Path(__file__).parent.parent / "config"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
AGENTS_CONFIG = load_yaml_config(CONFIG_DIR / "langnet_agents.yaml")
TASKS_CONFIG = load_yaml_config(CONFIG_DIR / "langnet_tasks.yaml")


def load_template(template_name: str) -> str:
    """Load a Markdown template from templates directory"""
    template_path = TEMPLATES_DIR / template_name
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


# ============================================================================
# FRAMEWORK SETUP
# ============================================================================

# Get framework adapters (using v4 with LangGraph support)
adapters = FrameworkAdapterFactory.get_framework_adapters(version="crewai")
AgentClass = adapters["agent"]
TaskClass = adapters["task"]
TeamClass = adapters["team"]
ToolClass = adapters["tool"]
ProcessClass = adapters["process"]
ProcessType = adapters["processtype"]

# LLM instances (lazy initialization)
_llm_cache = {}

def get_llm(use_deepseek: bool = False):
    """
    Get LLM instance based on configuration (with caching)

    Args:
        use_deepseek: If True, returns DeepSeek LLM; if False, returns OpenAI

    Returns:
        LLM instance
    """
    cache_key = "deepseek" if use_deepseek else "openai"

    if cache_key not in _llm_cache:
        if use_deepseek:
            # DeepSeek configuration
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

            _llm_cache[cache_key] = ChatOpenAI(
                model="deepseek/deepseek-chat",
                openai_api_key=deepseek_api_key,
                openai_api_base="https://api.deepseek.com",
                temperature=0.3,
                max_tokens=16384
            )
        else:
            # Default OpenAI
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")

            _llm_cache[cache_key] = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                openai_api_key=openai_api_key,
                temperature=0.3,
                max_tokens=16384
            )

    return _llm_cache[cache_key]

# Default LLM instance (for backward compatibility)
llm = None  # Will be initialized on first use

# Create custom tools
LANGNET_TOOLS = create_langnet_tools()


# ============================================================================
# AGENT CREATION FUNCTIONS (WITH MEMORY SUPPORT)
# ============================================================================

def create_document_analyst_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Document Analyst agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "document_analyst_agent",
        "config": AGENTS_CONFIG['document_analyst_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_requirements_engineer_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Requirements Engineer agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "requirements_engineer_agent",
        "config": AGENTS_CONFIG['requirements_engineer_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_requirements_validator_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Requirements Validator agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "requirements_validator_agent",
        "config": AGENTS_CONFIG['requirements_validator_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_generator_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Generator agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "specification_generator_agent",
        "config": AGENTS_CONFIG['specification_generator_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_agent_specifier_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Agent Specifier agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "agent_specifier_agent",
        "config": AGENTS_CONFIG['agent_specifier_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_task_decomposer_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Task Decomposer agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "task_decomposer_agent",
        "config": AGENTS_CONFIG['task_decomposer_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_petri_net_designer_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Petri Net Designer agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "petri_net_designer_agent",
        "config": AGENTS_CONFIG['petri_net_designer_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_yaml_generator_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create YAML Generator agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "yaml_generator_agent",
        "config": AGENTS_CONFIG['yaml_generator_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_code_generator_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Code Generator agent with optional memory and custom LLM"""
    agent_kwargs = {
        "name": "code_generator_agent",
        "config": AGENTS_CONFIG['code_generator_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_web_researcher_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Web Researcher agent with optional memory and custom LLM"""
    # Note: Tools will be added separately in TASK_REGISTRY
    agent_kwargs = {
        "name": "web_researcher_agent",
        "config": AGENTS_CONFIG['web_researcher_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


# Agents cache (lazy initialization)
_agents_cache = {}

def get_agent(agent_name: str, use_deepseek: bool = False):
    """
    Get agent instance with lazy initialization

    Args:
        agent_name: Name of the agent
        use_deepseek: If True, uses DeepSeek LLM

    Returns:
        Agent instance
    """
    cache_key = f"{agent_name}_{'deepseek' if use_deepseek else 'openai'}"

    if cache_key not in _agents_cache:
        llm_instance = get_llm(use_deepseek) if use_deepseek else None

        agent_creators = {
            "document_analyst": create_document_analyst_agent,
            "requirements_engineer": create_requirements_engineer_agent,
            "requirements_validator": create_requirements_validator_agent,
            "specification_generator": create_specification_generator_agent,
            "agent_specifier": create_agent_specifier_agent,
            "task_decomposer": create_task_decomposer_agent,
            "petri_net_designer": create_petri_net_designer_agent,
            "yaml_generator": create_yaml_generator_agent,
            "code_generator": create_code_generator_agent,
            "web_researcher": create_web_researcher_agent
        }

        if agent_name not in agent_creators:
            raise ValueError(f"Unknown agent: {agent_name}")

        _agents_cache[cache_key] = agent_creators[agent_name](llm_instance=llm_instance)

    return _agents_cache[cache_key]

# Initialize all agents (for backward compatibility - lazy loaded)
AGENTS = {
    "document_analyst": None,  # Loaded on first use
    "requirements_engineer": None,
    "requirements_validator": None,
    "specification_generator": None,
    "agent_specifier": None,
    "task_decomposer": None,
    "petri_net_designer": None,
    "yaml_generator": None,
    "code_generator": None,
    "web_researcher": None
}


# ============================================================================
# INPUT FUNCTIONS (Extract data from context state for each task)
# ============================================================================

def analyze_document_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for analyze_document task"""
    print(f"\n{'='*80}")
    print(f"[PHASE 3] analyze_document_input_func() called")
    print(f"[PHASE 3] state['document_content'] length: {len(state.get('document_content', ''))} chars")
    print(f"[PHASE 3] state['additional_instructions'] length: {len(state.get('additional_instructions', ''))} chars")
    print(f"{'='*80}\n")

    task_input = {
        "document_path": state.get("document_path", ""),
        "document_type": state.get("document_type", ""),
        "document_content": state.get("document_content", ""),  # Pre-extracted chunked content
        "additional_instructions": state.get("additional_instructions", ""),
        "project_name": state.get("project_name", ""),
        "project_description": state.get("project_description", "")
    }

    print(f"\n{'='*80}")
    print(f"[PHASE 3] analyze_document_input_func() RETURNED")
    print(f"[PHASE 3] task_input['document_content'] length: {len(task_input.get('document_content', ''))} chars")
    print(f"[PHASE 3] task_input['document_content'] preview (first 300 chars):")
    print(f"{task_input.get('document_content', '(EMPTY!)')[:300]}")
    print(f"{'='*80}\n")

    return task_input


def extract_requirements_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for extract_requirements task"""
    print(f"\n{'='*80}")
    print(f"[PHASE 3] extract_requirements_input_func() called")
    print(f"[PHASE 3] state['document_content'] length: {len(state.get('document_content', ''))} chars")
    print(f"[PHASE 3] state['additional_instructions'] length: {len(state.get('additional_instructions', ''))} chars")
    print(f"{'='*80}\n")

    task_input = {
        "document_content": state.get("document_content", ""),
        "additional_instructions": state.get("additional_instructions", ""),
        "project_name": state.get("project_name", ""),
        "project_description": state.get("project_description", ""),
        "analysis_json": state.get("document_analysis_json", "{}")  # BUG FIX: Add analysis from task 1
    }

    print(f"\n{'='*80}")
    print(f"[PHASE 3] extract_requirements_input_func() RETURNED")
    print(f"[PHASE 3] task_input['document_content'] length: {len(task_input.get('document_content', ''))} chars")
    print(f"[PHASE 3] task_input['document_content'] preview (first 300 chars):")
    print(f"{task_input.get('document_content', '(EMPTY!)')[:300]}")
    print(f"{'='*80}\n")

    return task_input


def research_additional_info_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for research_additional_info task"""
    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "document_content": state.get("document_content", ""),  # BUG FIX: Add document content for context
        "additional_instructions": state.get("additional_instructions", ""),
        "project_name": state.get("project_name", "")
    }


def validate_requirements_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for validate_requirements task - includes template"""
    from datetime import datetime

    # Load the Requirements Document template
    template = load_template("requirements_document_template.md")

    # Provide ALL template variables with defaults to avoid interpolation errors
    # The LLM will fill in the actual values based on the requirements and research
    default_placeholder = "To be filled by analysis"
    template_vars = {
        # Project info
        "project_name": state.get("project_name", ""),
        "project_description": state.get("project_description", ""),
        "project_objectives": state.get("additional_instructions", "")[:200] if state.get("additional_instructions") else default_placeholder,
        "project_context": "See additional instructions for context",
        "project_domain": state.get("project_domain", ""),
        "scope_includes": default_placeholder,
        "scope_excludes": default_placeholder,

        # Document metadata
        "document_id": state.get("document_id", ""),
        "document_path": state.get("document_path", ""),
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "document_status": "Draft",
        "documents_table": default_placeholder,
        "total_documents": "1",
        "total_pages": "N/A",
        "total_words": str(len(state.get("document_content", "").split())),
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "processing_time": "N/A",
        "total_processing_time": "N/A",

        # Requirements sections
        "functional_requirements_by_category": default_placeholder,
        "functional_requirements_list": default_placeholder,
        "non_functional_requirements_list": default_placeholder,
        "business_rules_by_domain": default_placeholder,
        "business_rules_list": default_placeholder,
        "actors_list": default_placeholder,
        "entities_description": default_placeholder,
        "workflows_overview": default_placeholder,
        "workflows_detailed": default_placeholder,
        "glossary_table": default_placeholder,
        "glossary_entries": default_placeholder,

        # NFR categories
        "nfr_performance": default_placeholder,
        "nfr_security": default_placeholder,
        "nfr_usability": default_placeholder,
        "nfr_reliability": default_placeholder,
        "nfr_scalability": default_placeholder,
        "nfr_maintainability": default_placeholder,

        # Quality analysis
        "consistency_analysis": default_placeholder,
        "conflicts_table": default_placeholder,
        "conflicts_entries": default_placeholder,
        "ambiguities_analysis": default_placeholder,
        "ambiguities_list": default_placeholder,
        "ambiguous_text": default_placeholder,
        "clarification_questions": default_placeholder,
        "high_priority_questions": default_placeholder,
        "medium_priority_questions": default_placeholder,
        "low_priority_questions": default_placeholder,

        # Completeness scores
        "completeness_score": "N/A",
        "fr_completeness": "N/A",
        "nfr_completeness": "N/A",
        "br_completeness": "N/A",
        "actors_completeness": "N/A",
        "entities_completeness": "N/A",
        "workflows_completeness": "N/A",

        # Quality scores
        "clarity_score": "N/A",
        "clarity_status": "N/A",
        "clarity_notes": "N/A",
        "consistency_score": "N/A",
        "consistency_status": "N/A",
        "consistency_notes": "N/A",
        "testability_score": "N/A",
        "testability_status": "N/A",
        "testability_notes": "N/A",
        "traceability_score": "N/A",
        "traceability_status": "N/A",
        "traceability_notes": "N/A",
        "completeness_status": "N/A",
        "completeness_notes": "N/A",

        # Gaps and issues
        "critical_gaps": default_placeholder,
        "information_requests": default_placeholder,
        "information_requests_list": default_placeholder,
        "essential_coverage_analysis": default_placeholder,
        "essential_coverage_table": default_placeholder,
        "application_type": "Web Application",
        "issues_summary": default_placeholder,
        "issues_detailed_list": default_placeholder,
        "critical_issues_count": "0",
        "high_issues_count": "0",
        "medium_issues_count": "0",
        "low_issues_count": "0",
        "severity": "N/A",

        # Diagrams and visualizations
        "entity_relationship_diagram": default_placeholder,
        "entity_attributes_table": default_placeholder,
        "workflow_sequence_diagram": default_placeholder,
        "prioritization_chart_data": default_placeholder,
        "dependencies_graph": default_placeholder,
        "critical_path_analysis": default_placeholder,
        "critical_requirements_list": default_placeholder,
        "coverage_mindmap": default_placeholder,
        "traceability_matrix": default_placeholder,

        # Web research
        "industry_best_practices": default_placeholder,
        "recommended_standards": default_placeholder,
        "suggested_technologies": default_placeholder,
        "compliance_checklist": default_placeholder,
        "compliance_entries": default_placeholder,
        "missing_requirements_discovered": default_placeholder,

        # Improvements
        "general_recommendations": default_placeholder,
        "fr_improvements": default_placeholder,
        "nfr_improvements": default_placeholder,
        "br_improvements": default_placeholder,
        "documentation_improvements": default_placeholder,

        # Next steps
        "immediate_actions": default_placeholder,
        "validations_needed": default_placeholder,
        "spec_preparation": default_placeholder,

        # System metadata
        "framework_version": "LangNet v1.0",
        "llm_provider": "OpenAI",
        "llm_model": "GPT-4",
        "web_research_enabled": "Yes",
        "has_additional_instructions": "Yes" if state.get("additional_instructions") else "No",
        "version_history": "N/A",

        # Other
        "abbreviations_table": default_placeholder
    }

    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "research_findings_json": state.get("research_findings_json", "{}"),
        "document_content": state.get("document_content", ""),  # BUG FIX: Add document content for LLM context
        "additional_instructions": state.get("additional_instructions", ""),  # BUG FIX: Add instructions for LLM context
        "template": template,
        **template_vars  # Spread all template variables
    }


def generate_specification_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for generate_specification task"""
    validation_data = state.get("validation_data", {})
    return {
        "validated_requirements": json.dumps(validation_data.get("valid_requirements", []))
    }


def suggest_agents_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for suggest_agents task"""
    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "specification_data": json.dumps(state.get("specification_data", {}))
    }


def decompose_tasks_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for decompose_tasks task"""
    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "agents_json": json.dumps(state.get("agents_data", []))
    }


def design_petri_net_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for design_petri_net task"""
    return {
        "tasks_json": json.dumps(state.get("tasks_data", [])),
        "dependencies": json.dumps(state.get("dependencies", {})),
        "agents_json": json.dumps(state.get("agents_data", []))
    }


def generate_yaml_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for generate_yaml_files task"""
    return {
        "agents_json": json.dumps(state.get("agents_data", [])),
        "tasks_json": json.dumps(state.get("tasks_data", []))
    }


def generate_code_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for generate_python_code task"""
    return {
        "framework_choice": state.get("framework_choice", "crewai")
    }


# ============================================================================
# OUTPUT FUNCTIONS (Update context state with task results)
# ============================================================================

def analyze_document_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with analyze_document results"""
    # Parse result
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {"error": "Failed to parse JSON", "raw": output_json}

    # Update state
    # IMPORTANTE: NÃO sobrescrever document_content (precisa ser preservado para próximas tasks)
    updated_state = {
        **state,
        "document_analysis_json": output_json,
        # "document_content": parsed.get("content", ""),  # REMOVIDO: mantém original intacto
        "document_structure": parsed.get("structure", {}),
        "document_metadata": parsed.get("metadata", {})
    }

    return log_task_complete(updated_state, "analyze_document", output_json[:200])


def extract_requirements_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with extract_requirements results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "requirements_json": output_json,
        "requirements_data": parsed
    }

    return log_task_complete(updated_state, "extract_requirements", output_json[:200])


def research_additional_info_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with research_additional_info results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "research_findings_json": output_json,
        "research_findings_data": parsed
    }

    return log_task_complete(updated_state, "research_additional_info", output_json[:200])


def validate_requirements_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with validate_requirements results and extract requirements document"""
    print(f"\n{'='*80}")
    print(f"[DEBUG] validate_requirements_output_func - Processing result")
    print(f"[DEBUG] Result type: {type(result)}")

    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    print(f"[DEBUG] output_json length: {len(output_json)}")
    print(f"[DEBUG] output_json preview: {output_json[:500]}")

    try:
        parsed = json.loads(output_json)
        print(f"[DEBUG] JSON parsing SUCCESS")
        print(f"[DEBUG] Parsed keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'NOT A DICT'}")
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parsing FAILED: {e}")
        parsed = {}

    # Extract the requirements document MD from the validation output
    requirements_doc_md = ""

    # CRUCIAL FIX: CrewAI wraps the response in "team_result" with markdown code blocks
    if isinstance(parsed, dict) and "team_result" in parsed:
        print(f"[DEBUG] Found 'team_result' key, extracting nested JSON...")
        team_result_str = parsed["team_result"]

        # Remove markdown code blocks (```json and ```)
        if isinstance(team_result_str, str):
            # Remove ```json at start and ``` at end
            team_result_str = team_result_str.strip()
            if team_result_str.startswith("```json"):
                team_result_str = team_result_str[7:]  # Remove ```json
            elif team_result_str.startswith("```"):
                team_result_str = team_result_str[3:]  # Remove ```
            if team_result_str.endswith("```"):
                team_result_str = team_result_str[:-3]  # Remove trailing ```
            team_result_str = team_result_str.strip()

            print(f"[DEBUG] After removing markdown, length: {len(team_result_str)}")

            # Parse the NESTED JSON
            try:
                nested_parsed = json.loads(team_result_str)
                print(f"[DEBUG] Nested JSON parsing SUCCESS")
                print(f"[DEBUG] Nested keys: {list(nested_parsed.keys()) if isinstance(nested_parsed, dict) else 'NOT A DICT'}")

                # NOW extract requirements_document_md from the nested JSON
                requirements_doc_md = nested_parsed.get("requirements_document_md", "")
                print(f"[DEBUG] requirements_doc_md from NESTED JSON: length={len(requirements_doc_md)}")

                # Update parsed to use the nested data
                parsed = nested_parsed
            except json.JSONDecodeError as e2:
                print(f"[DEBUG] Nested JSON parsing FAILED: {e2}")

    # Fallback: try direct extraction
    if not requirements_doc_md:
        requirements_doc_md = parsed.get("requirements_document_md", "")
        print(f"[DEBUG] requirements_doc_md from parsed (direct): length={len(requirements_doc_md)}")

    # If not in JSON, try to extract from raw output (agent might return MD directly)
    if not requirements_doc_md and isinstance(result, dict):
        requirements_doc_md = result.get("requirements_document_md", "")
        print(f"[DEBUG] requirements_doc_md from result dict: length={len(requirements_doc_md)}")

    print(f"[DEBUG] FINAL requirements_doc_md length: {len(requirements_doc_md)}")
    if requirements_doc_md:
        print(f"[DEBUG] FINAL requirements_doc_md preview:\n{requirements_doc_md[:300]}")
    else:
        print(f"[DEBUG] ⚠️  WARNING: requirements_document_md is EMPTY!")
    print(f"{'='*80}\n")

    updated_state = {
        **state,
        "validation_json": output_json,
        "validation_data": parsed,
        "requirements_document_md": requirements_doc_md  # Add the generated document
    }

    return log_task_complete(updated_state, "validate_requirements")


def generate_specification_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with generate_specification results"""
    if isinstance(result, dict):
        output_md = result.get("raw_output", str(result))
    else:
        output_md = str(result)

    updated_state = {
        **state,
        "specification_md": output_md,
        "specification_data": {"markdown": output_md}
    }

    return log_task_complete(updated_state, "generate_specification")


def suggest_agents_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with suggest_agents results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {"agents": []}

    updated_state = {
        **state,
        "agents_suggestions_json": output_json,
        "agents_data": parsed.get("agents", [])
    }

    return log_task_complete(updated_state, "suggest_agents")


def decompose_tasks_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with decompose_tasks results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {"tasks": [], "dependencies": {}}

    updated_state = {
        **state,
        "tasks_decomposition_json": output_json,
        "tasks_data": parsed.get("tasks", []),
        "dependencies": parsed.get("dependencies", {}),
        "execution_order": parsed.get("execution_order", []),
        "parallel_groups": parsed.get("parallel_groups", [])
    }

    return log_task_complete(updated_state, "decompose_tasks")


def design_petri_net_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with design_petri_net results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "petri_net_json": output_json,
        "petri_net_data": parsed
    }

    return log_task_complete(updated_state, "design_petri_net")


def generate_yaml_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with generate_yaml_files results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "yaml_files_json": output_json,
        "agents_yaml": parsed.get("agents_yaml", ""),
        "tasks_yaml": parsed.get("tasks_yaml", "")
    }

    return log_task_complete(updated_state, "generate_yaml_files")


def generate_code_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with generate_python_code results"""
    if isinstance(result, dict):
        output_json = result.get("raw_output", json.dumps(result))
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "code_generation_json": output_json,
        "generated_code": parsed.get("main_file", ""),
        "generated_files": parsed.get("additional_files", {}),
        "requirements_txt": parsed.get("requirements_txt", ""),
        "readme_md": parsed.get("readme_md", "")
    }

    return log_task_complete(updated_state, "generate_python_code")


# ============================================================================
# TASK REGISTRY (Maps task names to configurations)
# ============================================================================

TASK_REGISTRY = {
    "analyze_document": {
        "input_func": analyze_document_input_func,
        "output_func": analyze_document_output_func,
        "requires": [],
        "produces": ["document_content", "document_structure", "document_metadata"],
        "agent": AGENTS["document_analyst"],
        "tools": [LANGNET_TOOLS["document_reader"]],
        "phase": "document_analysis"
    },
    "extract_requirements": {
        "input_func": extract_requirements_input_func,
        "output_func": extract_requirements_output_func,
        "requires": ["document_content"],
        "produces": ["requirements_json", "requirements_data"],
        "agent": AGENTS["requirements_engineer"],
        "tools": [],
        "phase": "requirements_extraction"
    },
    "research_additional_info": {
        "input_func": research_additional_info_input_func,
        "output_func": research_additional_info_output_func,
        "requires": ["requirements_json"],
        "produces": ["research_findings_json", "research_findings_data"],
        "agent": AGENTS["web_researcher"],
        "tools": [LANGNET_TOOLS["serper_search"], LANGNET_TOOLS["serpapi_search"]],
        "phase": "requirements_extraction"
    },
    "validate_requirements": {
        "input_func": validate_requirements_input_func,
        "output_func": validate_requirements_output_func,
        "requires": ["requirements_json"],
        "produces": ["validation_json", "validation_data"],
        "agent": AGENTS["requirements_validator"],
        "tools": [],
        "phase": "requirements_extraction"
    },
    "generate_specification": {
        "input_func": generate_specification_input_func,
        "output_func": generate_specification_output_func,
        "requires": ["validation_data"],
        "produces": ["specification_md", "specification_data"],
        "agent": AGENTS["specification_generator"],
        "tools": [LANGNET_TOOLS["markdown_writer"]],
        "phase": "requirements_extraction"
    },
    "suggest_agents": {
        "input_func": suggest_agents_input_func,
        "output_func": suggest_agents_output_func,
        "requires": ["requirements_json", "specification_data"],
        "produces": ["agents_suggestions_json", "agents_data"],
        "agent": AGENTS["agent_specifier"],
        "tools": [],
        "phase": "agent_design"
    },
    "decompose_tasks": {
        "input_func": decompose_tasks_input_func,
        "output_func": decompose_tasks_output_func,
        "requires": ["requirements_json", "agents_data"],
        "produces": ["tasks_decomposition_json", "tasks_data", "dependencies"],
        "agent": AGENTS["task_decomposer"],
        "tools": [],
        "phase": "agent_design"
    },
    "design_petri_net": {
        "input_func": design_petri_net_input_func,
        "output_func": design_petri_net_output_func,
        "requires": ["tasks_data", "dependencies", "agents_data"],
        "produces": ["petri_net_json", "petri_net_data"],
        "agent": AGENTS["petri_net_designer"],
        "tools": [],
        "phase": "workflow_design"
    },
    "generate_yaml_files": {
        "input_func": generate_yaml_input_func,
        "output_func": generate_yaml_output_func,
        "requires": ["agents_data", "tasks_data"],
        "produces": ["agents_yaml", "tasks_yaml"],
        "agent": AGENTS["yaml_generator"],
        "tools": [LANGNET_TOOLS["yaml_writer"], LANGNET_TOOLS["yaml_validator"]],
        "phase": "code_generation"
    },
    "generate_python_code": {
        "input_func": generate_code_input_func,
        "output_func": generate_code_output_func,
        "requires": ["agents_yaml", "tasks_yaml", "petri_net_data"],
        "produces": ["generated_code", "generated_files"],
        "agent": AGENTS["code_generator"],
        "tools": [LANGNET_TOOLS["python_code_writer"]],
        "phase": "code_generation"
    }
}


# ============================================================================
# EXECUTOR FUNCTIONS
# ============================================================================

def execute_task_with_context(
    task_name: str,
    context_state: LangNetFullState,
    verbose_callback: Optional[Callable[[str], None]] = None
) -> LangNetFullState:
    """
    Execute a single task with context state

    Args:
        task_name: Name of task from TASK_REGISTRY
        context_state: Current state
        verbose_callback: Optional callback for progress messages

    Returns:
        Updated context state
    """
    if task_name not in TASK_REGISTRY:
        raise ValueError(f"Task '{task_name}' not found in TASK_REGISTRY")

    task_config = TASK_REGISTRY[task_name]

    # Log task start
    context_state = log_task_start(context_state, task_name)
    context_state["current_phase"] = task_config["phase"]

    if verbose_callback:
        verbose_callback(f"Starting task: {task_name}")

    try:
        # 1. Extract input from context state
        task_input = task_config["input_func"](context_state)

        # VALIDAÇÃO: Verificar se inputs críticos não estão vazios
        if task_name in ["analyze_document", "extract_requirements", "validate_requirements"]:
            doc_content = context_state.get("document_content", "")
            if not doc_content or len(doc_content) < 100:
                error_msg = f"ERROR: Task '{task_name}' requires document_content but it's empty or too short ({len(doc_content)} chars)"
                print(f"\n{'='*80}")
                print(f"[VALIDATION ERROR] {error_msg}")
                print(f"{'='*80}\n")
                return {
                    **context_state,
                    "errors": context_state.get("errors", []) + [error_msg],
                    "status": "failed",
                    "last_error": error_msg
                }

        if verbose_callback:
            verbose_callback(f"Task input: {json.dumps(task_input, indent=2)[:200]}")

        # 2. Get agent (lazy load with DeepSeek support)
        use_deepseek = context_state.get("use_deepseek", False)
        agent_ref = task_config["agent"]

        # If agent is None or we need DeepSeek, load dynamically
        if agent_ref is None or use_deepseek:
            # Determine agent name from task name
            agent_name_map = {
                "analyze_document": "document_analyst",
                "extract_requirements": "requirements_engineer",
                "research_additional_info": "web_researcher",
                "validate_requirements": "requirements_validator",
                "generate_specification": "specification_generator",
                "suggest_agents": "agent_specifier",
                "decompose_tasks": "task_decomposer",
                "design_petri_net": "petri_net_designer",
                "generate_yaml_files": "yaml_generator",
                "generate_python_code": "code_generator"
            }

            agent_name = agent_name_map.get(task_name)
            if not agent_name:
                raise ValueError(f"Cannot determine agent for task: {task_name}")

            agent = get_agent(agent_name, use_deepseek)
        else:
            agent = agent_ref

        # 3. Create task
        print(f"\n{'='*80}")
        print(f"[PHASE 3] BEFORE formatting task description for '{task_name}'")
        print(f"[PHASE 3] task_input keys: {list(task_input.keys())}")
        print(f"[PHASE 3] task_input['document_content'] length: {len(task_input.get('document_content', ''))} chars")
        print(f"[PHASE 3] task_input['additional_instructions'] length: {len(task_input.get('additional_instructions', ''))} chars")
        print(f"[PHASE 3] Raw task description template (first 500 chars):")
        print(f"{TASKS_CONFIG[task_name]['description'][:500]}")
        print(f"{'='*80}\n")

        task_description = TASKS_CONFIG[task_name]['description'].format(**task_input)

        print(f"\n{'='*80}")
        print(f"[PHASE 3] AFTER formatting task description for '{task_name}'")
        print(f"[PHASE 3] Formatted description length: {len(task_description)} chars")
        print(f"[PHASE 3] Formatted description preview (first 800 chars):")
        print(f"{task_description[:800]}")
        print(f"[PHASE 3] Formatted description preview (search for 'document_content' keyword):")
        if 'document_content:' in task_description:
            idx = task_description.index('document_content:')
            print(f"{task_description[idx:idx+400]}")
        else:
            print("⚠️  'document_content:' NOT FOUND in formatted description!")
        print(f"{'='*80}\n")

        task_expected_output = TASKS_CONFIG[task_name]['expected_output']

        # Convert tools to framework format: [(crewai_tool, phidata_tool), ...]
        # Since we only use CrewAI tools, we create tuples with (tool, None)
        tools_list = task_config.get("tools", [])
        framework_tools = [(tool, None) for tool in tools_list] if tools_list else []

        task_obj = TaskClass(
            description=task_description,
            expected_output=task_expected_output,
            agent=agent,
            tools=framework_tools
        )

        # 4. Execute task
        crew = TeamClass(
            agents=[agent],  # Use the agent (potentially recreated with DeepSeek)
            tasks=[task_obj],
            verbose=False,
            process=ProcessClass(ProcessType.SEQUENTIAL)
        )

        # Execute the crew - check which method is available
        # LangGraphTeamAdapter uses executar(), CrewAI Crew uses kickoff()
        if hasattr(crew, 'kickoff'):
            result = crew.kickoff(inputs=task_input)
        elif hasattr(crew, 'executar'):
            result = crew.executar(inputs=task_input)
        else:
            raise AttributeError(f"Team object has neither 'kickoff' nor 'executar' method: {type(crew).__name__}")

        if verbose_callback:
            verbose_callback(f"Task result: {str(result)[:200]}")

        # 4. Update context state
        updated_context = task_config["output_func"](context_state, result)

        if verbose_callback:
            verbose_callback(f"Task completed: {task_name}")

        return updated_context

    except Exception as e:
        import traceback
        full_traceback = traceback.format_exc()

        if verbose_callback:
            verbose_callback(f"Task failed: {task_name} - {str(e)}")
            verbose_callback(f"Full traceback:\n{full_traceback}")

        # Always print to console for debugging
        print(f"\n{'='*80}")
        print(f"ERROR in task: {task_name}")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception message: {str(e)}")
        print(f"\nFull Traceback:")
        print(full_traceback)
        print(f"{'='*80}\n")

        return log_task_error(context_state, task_name, e)


def execute_full_pipeline(
    project_id: str,
    document_id: str,
    document_path: str,
    framework_choice: str = "crewai",
    additional_instructions: str = "",
    verbose_callback: Optional[Callable[[str], None]] = None
) -> LangNetFullState:
    """
    Execute the complete LangNet pipeline

    Flow:
    1. Document Analysis → Extract Requirements → Web Research → Validate → Specify
    2. Suggest Agents → Decompose Tasks
    3. Design Petri Net
    4. Generate YAML → Generate Python Code

    Args:
        project_id: Project UUID
        document_id: Document UUID
        document_path: Path to uploaded document
        framework_choice: Target framework (crewai, autogen, langgraph)
        additional_instructions: Custom instructions from user
        verbose_callback: Optional callback for progress updates

    Returns:
        Final context state with all results
    """
    # Initialize state
    state = init_full_state(
        project_id=project_id,
        document_id=document_id,
        document_path=document_path,
        framework_choice=framework_choice,
        additional_instructions=additional_instructions
    )

    # Define execution order (NOW WITH 10 TASKS!)
    pipeline_tasks = [
        "analyze_document",
        "extract_requirements",
        "research_additional_info",  # NEW TASK - Web research
        "validate_requirements",
        "generate_specification",
        "suggest_agents",
        "decompose_tasks",
        "design_petri_net",
        "generate_yaml_files",
        "generate_python_code"
    ]

    # Execute each task sequentially
    for task_name in pipeline_tasks:
        if verbose_callback:
            verbose_callback(f"\n{'='*60}\nExecuting: {task_name}\n{'='*60}")

        state = execute_task_with_context(task_name, state, verbose_callback)

        # Check for errors
        if state.get("errors") and len(state["errors"]) > 0:
            if verbose_callback:
                verbose_callback(f"Pipeline stopped due to error in {task_name}")
            break

    # Mark completion
    state["completed_at"] = datetime.now().isoformat()

    return state


# Note: init_full_state is imported from langnetstate.py
# Do not redefine it here


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def execute_document_analysis_workflow(
    project_id: str,
    document_id: str,
    document_path: str,
    project_name: str = "",
    project_description: str = "",
    project_domain: str = "",
    additional_instructions: str = "",
    document_type: str = "pdf",
    use_deepseek: bool = False,
    document_content: str = "",
    enable_web_research: bool = True
) -> LangNetFullState:
    """
    Execute only document analysis workflow

    Args:
        project_id: Project UUID
        document_id: Document UUID
        document_path: Path to document file
        project_name: Name of the project
        project_description: Project description
        project_domain: Project domain/industry
        additional_instructions: Additional instructions for agents
        document_type: Type of document (pdf, docx, txt, etc.)
        use_deepseek: If True, uses DeepSeek LLM; if False, uses OpenAI GPT-4
        document_content: Pre-extracted and chunked document content (optional)
        enable_web_research: If True, enables web research for additional context (default: True)

    Returns:
        Final state with requirements document
    """
    print(f"\n{'='*80}")
    print(f"[PHASE 2] execute_document_analysis_workflow() called")
    print(f"[PHASE 2] Parameters received:")
    print(f"[PHASE 2]   - document_content length: {len(document_content)} chars")
    print(f"[PHASE 2]   - document_content preview (first 300 chars):")
    print(f"{document_content[:300] if document_content else '(EMPTY!)'}")
    print(f"{'='*80}\n")

    # Initialize state with all parameters
    state = init_full_state(
        project_id=project_id,
        document_id=document_id,
        document_path=document_path,
        project_name=project_name,
        project_description=project_description,
        project_domain=project_domain,
        additional_instructions=additional_instructions,
        document_type=document_type,
        document_content=document_content
    )

    print(f"\n{'='*80}")
    print(f"[PHASE 2] State returned from init_full_state")
    print(f"[PHASE 2] state['document_content'] length: {len(state.get('document_content', ''))} chars")
    print(f"[PHASE 2] state['additional_instructions'] length: {len(state.get('additional_instructions', ''))} chars")
    print(f"{'='*80}\n")

    # Add DeepSeek flag to state
    state["use_deepseek"] = use_deepseek

    print(f"\n{'='*80}")
    print(f"[PHASE 2] About to execute analyze_document task")
    print(f"[PHASE 2] State passed to task has document_content: {len(state.get('document_content', ''))} chars")
    print(f"{'='*80}\n")

    # Execute workflow tasks
    state = execute_task_with_context("analyze_document", state)
    state = execute_task_with_context("extract_requirements", state)

    # Web research task (can be enabled/disabled via parameter)
    if enable_web_research:
        print(f"\n🌐 Web research HABILITADA - Buscando best practices e padrões da indústria...")
        state = execute_task_with_context("research_additional_info", state)
    else:
        print(f"\n⏭️  Web research DESABILITADA - Pulando pesquisa complementar...")

    state = execute_task_with_context("validate_requirements", state)

    return state


def execute_agent_design_workflow(requirements_data: Dict, specification_data: Dict) -> LangNetFullState:
    """Execute only agent design workflow"""
    state = init_full_state(
        project_id="temp",
        document_id="temp",
        document_path="temp"
    )
    state["requirements_data"] = requirements_data
    state["specification_data"] = specification_data
    state["requirements_json"] = json.dumps(requirements_data)
    state = execute_task_with_context("suggest_agents", state)
    state = execute_task_with_context("decompose_tasks", state)
    return state


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("LangNet Agents System")
    print(f"Loaded {len(AGENTS)} agents")
    print(f"Loaded {len(TASK_REGISTRY)} tasks")
    print("\nAgents:", list(AGENTS.keys()))
    print("\nTasks:", list(TASK_REGISTRY.keys()))

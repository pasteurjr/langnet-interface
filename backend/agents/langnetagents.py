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
from json import JSONDecoder
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
        use_deepseek: If True, returns DeepSeek LLM; if False, checks LLM_PROVIDER env var

    Returns:
        LLM instance
    """
    # Check LLM_PROVIDER environment variable
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

    # Override with use_deepseek parameter
    if use_deepseek:
        llm_provider = "deepseek"

    cache_key = llm_provider

    if cache_key not in _llm_cache:
        if llm_provider == "claude_code":
            # Claude Code via local API using CrewAI's LLM class
            from crewai import LLM

            claude_api_base = os.getenv("CLAUDE_CODE_API_BASE", "http://localhost:8807")
            print(f"[LangNet] Using Claude Code API at {claude_api_base}/v1")

            _llm_cache[cache_key] = LLM(
                model="openai/claude-code",  # Use openai/ prefix for LiteLLM compatibility
                base_url=f"{claude_api_base}/v1",
                api_key="dummy",  # Required by CrewAI but not validated
                temperature=0.3,
                max_tokens=16384
            )

        elif llm_provider == "deepseek":
            # DeepSeek configuration
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

            # Read model from environment (same pattern as app/llm.py)
            deepseek_model = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek/deepseek-chat")

            # Handle deepseek/ prefix (avoid deepseek/deepseek/...)
            if deepseek_model.startswith("deepseek/"):
                deepseek_model_clean = deepseek_model
            else:
                deepseek_model_clean = f"deepseek/{deepseek_model}"

            # Adjust max_tokens based on model
            if "reasoner" in deepseek_model.lower():
                max_tokens_value = 65536  # 64K for deepseek-reasoner
            else:
                max_tokens_value = 8192   # 8K for deepseek-chat

            _llm_cache[cache_key] = ChatOpenAI(
                model=deepseek_model_clean,
                openai_api_key=deepseek_api_key,
                openai_api_base="https://api.deepseek.com",
                temperature=0.3,
                max_tokens=max_tokens_value
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


# =============================================================================
# SPECIFICATION GENERATION AGENTS (Multi-Step Pipeline)
# Based on Generative Computing principles - IBM Research
# =============================================================================

def create_specification_router_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Router agent for intent classification"""
    agent_kwargs = {
        "name": "specification_router_agent",
        "config": AGENTS_CONFIG['specification_router_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_entity_extractor_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Entity Extractor agent"""
    agent_kwargs = {
        "name": "specification_entity_extractor_agent",
        "config": AGENTS_CONFIG['specification_entity_extractor_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_composer_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Composer agent"""
    agent_kwargs = {
        "name": "specification_composer_agent",
        "config": AGENTS_CONFIG['specification_composer_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_verifier_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Verifier agent for grounding validation"""
    agent_kwargs = {
        "name": "specification_verifier_agent",
        "config": AGENTS_CONFIG['specification_verifier_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_compliance_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Compliance agent"""
    agent_kwargs = {
        "name": "specification_compliance_agent",
        "config": AGENTS_CONFIG['specification_compliance_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_formatter_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Formatter agent with fallback support"""
    agent_kwargs = {
        "name": "specification_formatter_agent",
        "config": AGENTS_CONFIG['specification_formatter_agent'],
        "llm": llm_instance if llm_instance else get_llm(),
        "verbose": True,
        "allow_delegation": False
    }
    if memory_system:
        agent_kwargs["memory"] = memory_system
    return AgentClass(**agent_kwargs)


def create_specification_web_researcher_agent(memory_system: Optional[Any] = None, llm_instance: Optional[Any] = None) -> Any:
    """Create Specification Web Researcher agent for external knowledge enrichment"""
    agent_kwargs = {
        "name": "specification_web_researcher_agent",
        "config": AGENTS_CONFIG['specification_web_researcher_agent'],
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
            "web_researcher": create_web_researcher_agent,
            # Specification multi-step pipeline agents
            "specification_router": create_specification_router_agent,
            "specification_entity_extractor": create_specification_entity_extractor_agent,
            "specification_web_researcher": create_specification_web_researcher_agent,
            "specification_composer": create_specification_composer_agent,
            "specification_verifier": create_specification_verifier_agent,
            "specification_compliance": create_specification_compliance_agent,
            "specification_formatter": create_specification_formatter_agent
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
    "web_researcher": None,
    # Specification multi-step pipeline agents
    "specification_router": None,
    "specification_entity_extractor": None,
    "specification_web_researcher": None,
    "specification_composer": None,
    "specification_verifier": None,
    "specification_compliance": None,
    "specification_formatter": None
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

    # ========== FIX: Format template with actual values BEFORE sending to LLM ==========
    # This ensures dates are correct and not invented by the LLM
    try:
        formatted_template = template.format(**template_vars)
        print(f"[TEMPLATE] ✅ Template formatado com {len(template_vars)} variáveis")
        print(f"[TEMPLATE] 📅 Data de geração: {template_vars['generation_date']}")
        print(f"[TEMPLATE] 📅 Data da análise: {template_vars['analysis_date']}")
    except KeyError as e:
        print(f"[TEMPLATE] ⚠️ Erro ao formatar template: {e}")
        formatted_template = template  # Fallback to unformatted

    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "research_findings_json": state.get("research_findings_json", "{}"),
        "document_content": state.get("document_content", ""),  # BUG FIX: Add document content for LLM context
        "additional_instructions": state.get("additional_instructions", ""),  # BUG FIX: Add instructions for LLM context
        "template": formatted_template,  # ← Template já formatado com datas corretas
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
        "framework_choice": state.get("framework_choice", "crewai"),
        "agents_yaml": state.get("agents_yaml", ""),
        "tasks_yaml": state.get("tasks_yaml", "")
    }


# =============================================================================
# SPECIFICATION PIPELINE INPUT FUNCTIONS
# =============================================================================

def classify_specification_intent_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for classify_specification_intent task (Router)"""
    return {
        "requirements_document": state.get("requirements_document", ""),
        "requirements_version": state.get("requirements_version", 1),
        "project_name": state.get("project_name", "Sistema"),
        "detail_level": state.get("spec_detail_level", "detailed"),
        "target_audience": state.get("spec_target_audience", "mixed")
    }


def extract_specification_entities_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for extract_specification_entities task (EntityExtractor)"""
    return {
        "requirements_document": state.get("requirements_document", ""),
        "classification_json": state.get("spec_classification_json", "{}"),
        "project_name": state.get("project_name", "Sistema")
    }


def compose_spec_use_cases_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for compose_spec_use_cases task - generates only section 5 (Use Cases)"""
    return {
        "entities_json": state.get("spec_entities_json", "{}"),
        "requirements_document": state.get("requirements_document", ""),
        "project_name": state.get("project_name", "Sistema"),
    }


def compose_spec_document_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for compose_spec_document task - generates sections 1-4 and 6-14"""
    return {
        "entities_json": state.get("spec_entities_json", "{}"),
        "research_context_json": state.get("spec_research_context_json", "{}"),
        "use_cases_json": state.get("spec_use_cases_json", "{}"),
        "project_name": state.get("project_name", "Sistema"),
        "requirements_version": state.get("requirements_version", 1),
        "requirements_created_at": state.get("requirements_created_at", datetime.now().strftime("%Y-%m-%d")),
        "detail_level": state.get("spec_detail_level", "detailed"),
        "target_audience": state.get("spec_target_audience", "mixed")
    }


def verify_specification_grounding_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for verify_specification_grounding task (Verifier)"""
    return {
        "draft_sections_json": state.get("spec_draft_sections_json", "{}"),
        "entities_json": state.get("spec_entities_json", "{}"),
        "requirements_document": state.get("requirements_document", "")
    }


def validate_specification_compliance_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for validate_specification_compliance task (Compliance)"""
    return {
        "draft_sections_json": state.get("spec_draft_sections_json", "{}"),
        "verification_results_json": state.get("spec_verification_json", "{}"),
        "target_audience": state.get("spec_target_audience", "mixed")
    }


def apply_spec_corrections_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for apply_spec_corrections task - applies verification and compliance corrections"""
    return {
        "draft_sections_json": state.get("spec_draft_sections_json", "{}"),
        "verification_results_json": state.get("spec_verification_json", "{}"),
        "compliance_results_json": state.get("spec_compliance_json", "{}")
    }


def render_final_specification_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for render_final_specification task - renders final Markdown document"""
    return {
        "corrected_sections_json": state.get("spec_corrected_sections_json", "{}"),
        "project_name": state.get("project_name", "Sistema"),
        "requirements_version": state.get("requirements_version", 1),
        "requirements_created_at": state.get("requirements_created_at", datetime.now().strftime("%Y-%m-%d"))
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

    # CrewAI returns CrewOutput object (pydantic model), not a dict
    # Must extract content properly using .raw, .json_dict, or .model_dump()
    if hasattr(result, 'raw'):
        # CrewOutput object - get raw string output
        output_json = result.raw
        print(f"[DEBUG] Extracted from CrewOutput.raw")
    elif hasattr(result, 'json_dict') and result.json_dict:
        # CrewOutput with pre-parsed JSON dictionary
        output_json = json.dumps(result.json_dict)
        print(f"[DEBUG] Extracted from CrewOutput.json_dict")
    elif hasattr(result, 'model_dump'):
        # Pydantic model - convert to dict then JSON
        output_json = json.dumps(result.model_dump())
        print(f"[DEBUG] Extracted from CrewOutput.model_dump()")
    elif isinstance(result, dict):
        # Already a dict (shouldn't happen with CrewAI but keep as fallback)
        output_json = json.dumps(result)
        print(f"[DEBUG] Result is already a dict")
    else:
        # Last resort - string conversion (likely won't work correctly)
        output_json = str(result)
        print(f"[DEBUG] WARNING: Using str() fallback - may not work correctly")

    print(f"[DEBUG] output_json type: {type(output_json)}")
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

            # Detect if using Claude Code (check provider from config or state)
            is_claude_code = False
            try:
                # Try to detect from environment or config
                import os
                from app.config import settings
                is_claude_code = settings.llm_provider.lower() == "claude_code"
                print(f"[DEBUG] Detected LLM provider: {settings.llm_provider}")
            except:
                # Fallback: assume Claude if team_result exists
                is_claude_code = True
                print(f"[DEBUG] Could not detect provider, assuming Claude-like behavior")

            # Parse the NESTED JSON - use different strategy for Claude vs GPT
            try:
                if is_claude_code:
                    # CLAUDE CODE: Use raw_decode to handle extra text after JSON
                    print(f"[DEBUG] Using raw_decode for Claude Code (handles extra text)")
                    decoder = JSONDecoder()
                    nested_parsed, json_end_index = decoder.raw_decode(team_result_str)

                    print(f"[DEBUG] Nested JSON parsing SUCCESS via raw_decode")
                    print(f"[DEBUG] JSON ends at index {json_end_index} of {len(team_result_str)}")
                    print(f"[DEBUG] Nested keys: {list(nested_parsed.keys()) if isinstance(nested_parsed, dict) else 'NOT A DICT'}")

                    # Extra text after JSON is ignored automatically by raw_decode
                    if json_end_index < len(team_result_str):
                        extra_text_preview = team_result_str[json_end_index:json_end_index+100].strip()
                        print(f"[DEBUG] Extra text found after JSON (ignored): {extra_text_preview[:50]}...")
                else:
                    # GPT-4o-mini and others: Use standard json.loads (expects pure JSON)
                    print(f"[DEBUG] Using json.loads for standard LLM (expects pure JSON)")
                    nested_parsed = json.loads(team_result_str)
                    print(f"[DEBUG] Nested JSON parsing SUCCESS via json.loads")
                    print(f"[DEBUG] Nested keys: {list(nested_parsed.keys()) if isinstance(nested_parsed, dict) else 'NOT A DICT'}")

                # NOW extract requirements_document_md from the nested JSON
                requirements_doc_md = nested_parsed.get("requirements_document_md", "")
                print(f"[DEBUG] requirements_doc_md from NESTED JSON: length={len(requirements_doc_md)}")

                # Update parsed to use the nested data
                parsed = nested_parsed

            except json.JSONDecodeError as e2:
                print(f"[DEBUG] Nested JSON parsing FAILED: {e2}")

                # FALLBACK: Extract requirements_document_md directly from string using regex
                # This handles cases where the JSON is malformed but the field exists
                print(f"[DEBUG] Attempting regex extraction of requirements_document_md...")
                import re
                match = re.search(r'"requirements_document_md"\s*:\s*"((?:[^"\\]|\\.)*)"', team_result_str, re.DOTALL)
                if match:
                    # Unescape the JSON string
                    requirements_doc_md = match.group(1).encode().decode('unicode_escape')
                    print(f"[DEBUG] REGEX EXTRACTION SUCCESS: length={len(requirements_doc_md)}")
                else:
                    print(f"[DEBUG] REGEX EXTRACTION FAILED: field not found")

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


def enrich_requirements_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for enrich_requirements task"""
    return {
        "requirements_json": state.get("requirements_json", "{}"),
        "research_findings_json": state.get("research_findings_json", "{}"),
        "business_context": state.get("business_context", "{}"),
        "project_name": state.get("project_name", "")
    }


def enrich_requirements_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with enrich_requirements results"""
    # Extract output (same pattern as other output funcs)
    if hasattr(result, 'raw'):
        output_json = result.raw
    elif hasattr(result, 'json_dict') and result.json_dict:
        output_json = json.dumps(result.json_dict)
    elif hasattr(result, 'model_dump'):
        output_json = json.dumps(result.model_dump())
    elif isinstance(result, dict):
        output_json = json.dumps(result)
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
        # Handle nested team_result if present (Claude Code pattern)
        if isinstance(parsed, dict) and "team_result" in parsed:
            team_result_str = parsed["team_result"]
            if isinstance(team_result_str, str):
                # Remove markdown code blocks
                team_result_str = team_result_str.strip()
                if team_result_str.startswith("```json"):
                    team_result_str = team_result_str[7:]
                elif team_result_str.startswith("```"):
                    team_result_str = team_result_str[3:]
                if team_result_str.endswith("```"):
                    team_result_str = team_result_str[:-3]
                parsed = json.loads(team_result_str.strip())
    except json.JSONDecodeError as e:
        print(f"[ERROR] enrich_requirements JSON parsing failed: {e}")
        parsed = {}

    updated_state = {
        **state,
        "enriched_requirements": parsed.get("enriched_requirements", {}),
        "validation_status": parsed.get("validation_status", "UNKNOWN"),
        "validation_message": parsed.get("validation_message", ""),
        "completeness_flags": parsed.get("completeness_flags", {})
    }

    return log_task_complete(updated_state, "enrich_requirements")


def validate_quality_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for validate_quality task"""
    return {
        "enriched_requirements": json.dumps(state.get("enriched_requirements", {})),
        "business_context": state.get("business_context", "{}"),
        "project_name": state.get("project_name", "")
    }


def validate_quality_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with validate_quality results"""
    # Extract output (same pattern as other output funcs)
    if hasattr(result, 'raw'):
        output_json = result.raw
    elif hasattr(result, 'json_dict') and result.json_dict:
        output_json = json.dumps(result.json_dict)
    elif hasattr(result, 'model_dump'):
        output_json = json.dumps(result.model_dump())
    elif isinstance(result, dict):
        output_json = json.dumps(result)
    else:
        output_json = str(result)

    try:
        parsed = json.loads(output_json)
        # Handle nested team_result if present (Claude Code pattern)
        if isinstance(parsed, dict) and "team_result" in parsed:
            team_result_str = parsed["team_result"]
            if isinstance(team_result_str, str):
                # Remove markdown code blocks
                team_result_str = team_result_str.strip()
                if team_result_str.startswith("```json"):
                    team_result_str = team_result_str[7:]
                elif team_result_str.startswith("```"):
                    team_result_str = team_result_str[3:]
                if team_result_str.endswith("```"):
                    team_result_str = team_result_str[:-3]
                parsed = json.loads(team_result_str.strip())
    except json.JSONDecodeError as e:
        print(f"[ERROR] validate_quality JSON parsing failed: {e}")
        parsed = {}

    updated_state = {
        **state,
        "quality_validation": parsed,
        "quality_scores": parsed.get("quality_scores", {}),
        "issues_found": parsed.get("issues_found", []),
        "critical_gaps": parsed.get("critical_gaps", [])
    }

    return log_task_complete(updated_state, "validate_quality")


def generate_document_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for generate_document task - includes template"""
    from datetime import datetime

    # Load the Requirements Document template
    template = load_template("requirements_document_template.md")

    # Provide ALL template variables with defaults
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
        "llm_provider": "DeepSeek",
        "llm_model": "DeepSeek Reasoner",
        "web_research_enabled": "Yes",
        "has_additional_instructions": "Yes" if state.get("additional_instructions") else "No",
        "version_history": "N/A",

        # Other
        "abbreviations_table": default_placeholder
    }

    # Format template with actual values BEFORE sending to LLM
    try:
        formatted_template = template.format(**template_vars)
        print(f"[TEMPLATE] ✅ Template formatado com {len(template_vars)} variáveis")
        print(f"[TEMPLATE] 📅 Data de geração: {template_vars['generation_date']}")
    except KeyError as e:
        print(f"[TEMPLATE] ⚠️ Erro ao formatar template: {e}")
        formatted_template = template

    return {
        "enriched_requirements": json.dumps(state.get("enriched_requirements", {})),
        "quality_validation": json.dumps(state.get("quality_validation", {})),
        "research_findings_json": state.get("research_findings_json", "{}"),
        "template": formatted_template,
        "project_name": state.get("project_name", ""),
        **template_vars
    }


def generate_document_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with generate_document results and extract requirements document"""
    print(f"\n{'='*80}")
    print(f"[DEBUG] generate_document_output_func - Processing result")
    print(f"[DEBUG] Result type: {type(result)}")

    # Extract output (same pattern as validate_requirements_output_func)
    if hasattr(result, 'raw'):
        output_json = result.raw
    elif hasattr(result, 'json_dict') and result.json_dict:
        output_json = json.dumps(result.json_dict)
    elif hasattr(result, 'model_dump'):
        output_json = json.dumps(result.model_dump())
    elif isinstance(result, dict):
        output_json = json.dumps(result)
    else:
        output_json = str(result)

    print(f"[DEBUG] output_json length: {len(output_json)}")
    print(f"[DEBUG] output_json preview (first 500 chars): {output_json[:500]}")

    try:
        parsed = json.loads(output_json)
        print(f"[DEBUG] Parsed type: {type(parsed)}")
        if isinstance(parsed, dict):
            print(f"[DEBUG] Parsed keys: {list(parsed.keys())}")
            print(f"[DEBUG] Has 'requirements_document_md' key: {'requirements_document_md' in parsed}")
            if 'requirements_document_md' in parsed:
                print(f"[DEBUG] requirements_document_md type: {type(parsed['requirements_document_md'])}")
                print(f"[DEBUG] requirements_document_md length: {len(str(parsed['requirements_document_md']))}")

        # Handle nested team_result if present
        if isinstance(parsed, dict) and "team_result" in parsed:
            team_result_str = parsed["team_result"]
            if isinstance(team_result_str, str):
                # Remove markdown code blocks
                team_result_str = team_result_str.strip()
                if team_result_str.startswith("```json"):
                    team_result_str = team_result_str[7:]
                elif team_result_str.startswith("```"):
                    team_result_str = team_result_str[3:]
                if team_result_str.endswith("```"):
                    team_result_str = team_result_str[:-3]
                
                # Parse the nested JSON
                try:
                    parsed = json.loads(team_result_str.strip())
                except json.JSONDecodeError:
                    # Fallback to original if nested parsing fails
                    pass
    except json.JSONDecodeError as e:
        print(f"[DEBUG] JSON parsing FAILED: {e}")
        parsed = {}

    # Extract the requirements document MD
    requirements_doc_md = ""
    if isinstance(parsed, dict):
        requirements_doc_md = parsed.get("requirements_document_md", "")

    print(f"[DEBUG] FINAL requirements_doc_md length: {len(requirements_doc_md)}")
    if requirements_doc_md:
        print(f"[DEBUG] FINAL requirements_doc_md preview:\n{requirements_doc_md[:300]}")
    else:
        print(f"[DEBUG] ⚠️  WARNING: requirements_document_md is EMPTY!")
    print(f"{'='*80}\n")

    # ─── BUILD REFERENCES SECTION (100% Python, zero LLM cost) ─────────────────
    if requirements_doc_md:
        from datetime import datetime

        ref_lines = [
            "\n\n---\n",
            "## 📚 Referências\n"
        ]

        # 16.1 — Source documents
        doc_path = state.get("document_path", "")
        doc_names = []
        if doc_path.startswith("Multiple documents: "):
            raw = doc_path.replace("Multiple documents: ", "")
            doc_names = [d.strip() for d in raw.split(",") if d.strip()]
        elif doc_path:
            doc_names = [doc_path.strip()]

        if doc_names:
            ref_lines.append("\n### 16.1 Documentos Analisados\n")
            ref_lines.append("| # | Documento |")
            ref_lines.append("|---|-----------|")
            for i, name in enumerate(doc_names, 1):
                ref_lines.append(f"| {i} | {name} |")
            ref_lines.append(f"\n*Analisados em: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")

        # 16.2 — Web sources
        research_json = state.get("research_findings_json", "{}")
        try:
            research = json.loads(research_json) if isinstance(research_json, str) else research_json
        except (json.JSONDecodeError, TypeError):
            research = {}

        web_sources = []
        seen_urls = set()

        def add_source(name, url):
            if url and url not in seen_urls and url.startswith("http"):
                seen_urls.add(url)
                web_sources.append((name, url))

        for sys_item in research.get("analogous_systems", []):
            add_source(sys_item.get("name", "Sistema"), sys_item.get("source_url", ""))

        for bp in research.get("best_practices", []):
            add_source(bp.get("title", bp.get("source", "Referência")), bp.get("url", bp.get("source_url", "")))

        for comp in research.get("compliance_requirements", []):
            add_source(comp.get("standard", comp.get("name", "Norma")), comp.get("source_url", comp.get("url", "")))

        for tech in research.get("recommended_technologies", []):
            add_source(tech.get("name", "Tecnologia"), tech.get("source_url", tech.get("url", "")))

        if web_sources:
            ref_lines.append("\n### 16.2 Fontes Web Consultadas\n")
            ref_lines.append("| # | Fonte | URL |")
            ref_lines.append("|---|-------|-----|")
            for i, (name, url) in enumerate(web_sources, 1):
                ref_lines.append(f"| {i} | {name} | [{url}]({url}) |")
        elif research:
            ref_lines.append("\n### 16.2 Pesquisa Web\n")
            ref_lines.append("*Pesquisa web realizada sem URLs externas rastreáveis nos resultados.*")

        requirements_doc_md += "\n".join(ref_lines)
        print(f"[REFS] ✅ Seção de referências adicionada: {len(doc_names)} documentos, {len(web_sources)} fontes web")
    # ────────────────────────────────────────────────────────────────────────────

    updated_state = {
        **state,
        "validation_json": output_json,
        "validation_data": parsed,
        "requirements_document_md": requirements_doc_md,
        "document_metadata": parsed.get("document_metadata", {}),
        "quality_summary": parsed.get("quality_summary", {}),
        "source_distribution": parsed.get("source_distribution", {})
    }

    return log_task_complete(updated_state, "generate_document")


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


# =============================================================================
# SPECIFICATION PIPELINE OUTPUT FUNCTIONS
# =============================================================================

def _extract_crewai_result(result: Any) -> str:
    """Helper to extract raw output from CrewAI result"""
    raw_output = ""

    if hasattr(result, 'raw'):
        raw_output = result.raw
    elif hasattr(result, 'json_dict') and result.json_dict:
        return json.dumps(result.json_dict)
    elif hasattr(result, 'model_dump'):
        return json.dumps(result.model_dump())
    elif isinstance(result, dict):
        # Check if it's the new CrewAI format with 'team_result'
        if 'team_result' in result:
            raw_output = result['team_result']
        else:
            return json.dumps(result)
    else:
        raw_output = str(result)

    # Remove markdown code fences if present
    if isinstance(raw_output, str):
        # Remove ```json ... ``` wrappers
        import re
        raw_output = re.sub(r'^```json\s*\n', '', raw_output)
        raw_output = re.sub(r'\n```\s*$', '', raw_output)
        raw_output = re.sub(r'^```\s*\n', '', raw_output)  # Also handle plain ``` without json

    return raw_output


def classify_specification_intent_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with classify_specification_intent results (Router)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {"intent": "create", "scope": "functional_spec"}

    updated_state = {
        **state,
        "spec_classification_json": output_json,
        "spec_intent": parsed.get("intent", "create"),
        "spec_scope": parsed.get("scope", "functional_spec"),
        "spec_target_sections": parsed.get("target_sections", list(range(1, 15))),
        "spec_estimated_complexity": parsed.get("estimated_complexity", "medium")
    }

    return log_task_complete(updated_state, "classify_specification_intent", output_json[:200])


def extract_specification_entities_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with extract_specification_entities results (EntityExtractor)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_entities_json": output_json,
        "spec_actors": parsed.get("actors", []),
        "spec_functional_requirements": parsed.get("functional_requirements", []),
        "spec_non_functional_requirements": parsed.get("non_functional_requirements", []),
        "spec_use_cases": parsed.get("use_cases", []),
        "spec_business_rules": parsed.get("business_rules", []),
        "spec_data_entities": parsed.get("data_entities", []),
        "spec_apis": parsed.get("apis", []),
        "spec_workflows": parsed.get("workflows", []),
        "spec_gaps": parsed.get("gaps", []),
        "spec_extraction_summary": parsed.get("extraction_summary", {})
    }

    return log_task_complete(updated_state, "extract_specification_entities", output_json[:200])


def research_specification_context_input_func(state: LangNetFullState) -> Dict[str, Any]:
    """Extract input for research_specification_context task (WebResearcher)"""
    return {
        "entities_json": state.get("spec_entities_json", "{}"),
        "project_name": state.get("project_name", "Sistema")
    }


def research_specification_context_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with research_specification_context results (WebResearcher)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_research_context_json": output_json,
        "spec_technical_standards": parsed.get("technical_standards", []),
        "spec_compliance_requirements": parsed.get("compliance_requirements", []),
        "spec_best_practices": parsed.get("best_practices", []),
        "spec_reference_architectures": parsed.get("reference_architectures", []),
        "spec_research_summary": parsed.get("research_summary", {})
    }

    return log_task_complete(updated_state, "research_specification_context", output_json[:200])


def compose_spec_use_cases_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with compose_spec_use_cases results - use cases for section 5"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_use_cases_json": output_json,
        "spec_use_cases": parsed.get("use_cases", []),
        "spec_use_cases_count": parsed.get("use_cases_count", 0),
        "spec_use_cases_with_min_steps": parsed.get("use_cases_with_min_steps", 0),
        "spec_actors_identified": parsed.get("actors_identified", []),
        "spec_uc_gaps": parsed.get("gaps", [])
    }

    return log_task_complete(updated_state, "compose_spec_use_cases", output_json[:200])


def compose_spec_document_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with compose_spec_document results - sections 1-4 and 6-14"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    document_md = parsed.get("document_md", "")

    updated_state = {
        **state,
        "spec_draft_sections_json": output_json,
        "spec_draft_document_md": document_md,
        "spec_sections": parsed.get("sections", []),
        "spec_business_rules_count": parsed.get("business_rules_count", 0),
        "spec_generation_gaps": parsed.get("gaps", []),
        "spec_generation_summary": parsed.get("generation_summary", {})
    }

    return log_task_complete(updated_state, "compose_spec_document", output_json[:200])


def verify_specification_grounding_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with verify_specification_grounding results (Verifier)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    verification_summary = parsed.get("verification_summary", {})

    updated_state = {
        **state,
        "spec_verification_json": output_json,
        "spec_verified_items": parsed.get("verified_items", []),
        "spec_verification_issues": parsed.get("issues", {}),
        "spec_actions_recommended": parsed.get("actions_recommended", []),
        "spec_grounding_score": verification_summary.get("grounding_score", 0),
        "spec_verification_summary": verification_summary
    }

    return log_task_complete(updated_state, "verify_specification_grounding", output_json[:200])


def validate_specification_compliance_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with validate_specification_compliance results (Compliance)"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_compliance_json": output_json,
        "spec_compliance_ok": parsed.get("compliance_ok", False),
        "spec_compliance_violations": parsed.get("violations", []),
        "spec_checks_passed": parsed.get("checks_passed", {}),
        "spec_compliance_score": parsed.get("compliance_score", 0),
        "spec_corrections_needed": parsed.get("corrections_needed", []),
        "spec_minimum_requirements_check": parsed.get("minimum_requirements_check", {})
    }

    return log_task_complete(updated_state, "validate_specification_compliance", output_json[:200])


def apply_spec_corrections_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with apply_spec_corrections results - corrected sections"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    updated_state = {
        **state,
        "spec_corrected_sections_json": output_json,
        "spec_corrected_sections": parsed.get("corrected_sections", []),
        "spec_corrections_applied": parsed.get("corrections_applied", []),
        "spec_grounding_score": parsed.get("grounding_score", 0),
        "spec_compliance_score": parsed.get("compliance_score", 0),
        "spec_remaining_gaps": parsed.get("remaining_gaps", [])
    }

    return log_task_complete(updated_state, "apply_spec_corrections", output_json[:200])


def render_final_specification_output_func(state: LangNetFullState, result: Any) -> LangNetFullState:
    """Update state with render_final_specification results - final document"""
    output_json = _extract_crewai_result(result)

    try:
        parsed = json.loads(output_json)
    except json.JSONDecodeError:
        parsed = {}

    document_md = parsed.get("document_md", "")
    metadata = parsed.get("metadata", {})

    updated_state = {
        **state,
        "spec_final_json": output_json,
        "spec_status": parsed.get("status", "failed"),
        "spec_document_md": document_md,
        "spec_final_gaps": parsed.get("gaps", []),
        "spec_warnings": parsed.get("warnings", []),
        "spec_metadata": metadata,
        "spec_grounding_score_final": metadata.get("grounding_score", 0),
        "spec_compliance_score_final": metadata.get("compliance_score", 0),
        "spec_total_sections": metadata.get("total_sections", 0),
        "spec_complete_sections": metadata.get("complete_sections", 0)
    }

    return log_task_complete(updated_state, "render_final_specification", output_json[:200])


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
        "tools": [
            LANGNET_TOOLS["serpapi_search"],  # DuckDuckGo for general searches
            LANGNET_TOOLS["tavily_search"],   # Tavily for deep research
            LANGNET_TOOLS["serper_search"]    # Google for specific/regulatory info
        ],
        "phase": "requirements_extraction"
    },
    "enrich_requirements": {
        "input_func": enrich_requirements_input_func,
        "output_func": enrich_requirements_output_func,
        "requires": ["requirements_json", "research_findings_json"],
        "produces": ["enriched_requirements", "validation_status"],
        "agent": AGENTS["requirements_validator"],
        "tools": [],
        "phase": "requirements_extraction"
    },
    "validate_quality": {
        "input_func": validate_quality_input_func,
        "output_func": validate_quality_output_func,
        "requires": ["enriched_requirements"],
        "produces": ["quality_validation", "quality_scores"],
        "agent": AGENTS["requirements_validator"],
        "tools": [],
        "phase": "requirements_extraction"
    },
    "generate_document": {
        "input_func": generate_document_input_func,
        "output_func": generate_document_output_func,
        "requires": ["enriched_requirements", "quality_validation"],
        "produces": ["requirements_document_md", "validation_data"],
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
    },

    # =========================================================================
    # SPECIFICATION GENERATION PIPELINE (Multi-Step following Generative Computing)
    # =========================================================================

    "classify_specification_intent": {
        "input_func": classify_specification_intent_input_func,
        "output_func": classify_specification_intent_output_func,
        "requires": ["requirements_document"],
        "produces": ["spec_classification_json", "spec_intent", "spec_scope", "spec_target_sections"],
        "agent": AGENTS["specification_router"],
        "tools": [],
        "phase": "specification_generation"
    },
    "extract_specification_entities": {
        "input_func": extract_specification_entities_input_func,
        "output_func": extract_specification_entities_output_func,
        "requires": ["requirements_document", "spec_classification_json"],
        "produces": ["spec_entities_json", "spec_actors", "spec_functional_requirements", "spec_use_cases"],
        "agent": AGENTS["specification_entity_extractor"],
        "tools": [],
        "phase": "specification_generation"
    },
    "research_specification_context": {
        "input_func": research_specification_context_input_func,
        "output_func": research_specification_context_output_func,
        "requires": ["spec_entities_json"],
        "produces": ["spec_research_context_json", "spec_technical_standards", "spec_compliance_requirements", "spec_best_practices"],
        "agent": AGENTS["specification_web_researcher"],
        "tools": [
            LANGNET_TOOLS["tavily_search"],
            LANGNET_TOOLS["serpapi_search"],
            LANGNET_TOOLS["serper_search"]
        ],
        "phase": "specification_generation"
    },
    "compose_spec_use_cases": {
        "input_func": compose_spec_use_cases_input_func,
        "output_func": compose_spec_use_cases_output_func,
        "requires": ["spec_entities_json", "requirements_document"],
        "produces": ["spec_use_cases_json", "spec_use_cases", "spec_use_cases_count"],
        "agent": AGENTS["specification_composer"],
        "tools": [],
        "phase": "specification_generation"
    },
    "compose_spec_document": {
        "input_func": compose_spec_document_input_func,
        "output_func": compose_spec_document_output_func,
        "requires": ["spec_entities_json", "spec_research_context_json", "spec_use_cases_json"],
        "produces": ["spec_draft_sections_json", "spec_draft_document_md", "spec_sections"],
        "agent": AGENTS["specification_composer"],
        "tools": [],
        "phase": "specification_generation"
    },
    "verify_specification_grounding": {
        "input_func": verify_specification_grounding_input_func,
        "output_func": verify_specification_grounding_output_func,
        "requires": ["spec_draft_sections_json", "spec_entities_json", "requirements_document"],
        "produces": ["spec_verification_json", "spec_verified_items", "spec_grounding_score"],
        "agent": AGENTS["specification_verifier"],
        "tools": [],
        "phase": "specification_generation"
    },
    "validate_specification_compliance": {
        "input_func": validate_specification_compliance_input_func,
        "output_func": validate_specification_compliance_output_func,
        "requires": ["spec_draft_sections_json", "spec_verification_json"],
        "produces": ["spec_compliance_json", "spec_compliance_ok", "spec_compliance_score"],
        "agent": AGENTS["specification_compliance"],
        "tools": [],
        "phase": "specification_generation"
    },
    "apply_spec_corrections": {
        "input_func": apply_spec_corrections_input_func,
        "output_func": apply_spec_corrections_output_func,
        "requires": ["spec_draft_sections_json", "spec_verification_json", "spec_compliance_json"],
        "produces": ["spec_corrected_sections_json", "spec_corrections_applied", "spec_grounding_score"],
        "agent": AGENTS["specification_formatter"],
        "tools": [],
        "phase": "specification_generation"
    },
    "render_final_specification": {
        "input_func": render_final_specification_input_func,
        "output_func": render_final_specification_output_func,
        "requires": ["spec_corrected_sections_json"],
        "produces": ["spec_final_json", "spec_status", "spec_document_md", "spec_metadata"],
        "agent": AGENTS["specification_formatter"],
        "tools": [],
        "phase": "specification_generation"
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
        if task_name in ["analyze_document", "extract_requirements"]:
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
                "enrich_requirements": "requirements_validator",
                "validate_quality": "requirements_validator",
                "generate_document": "requirements_validator",
                "generate_specification": "specification_generator",
                "suggest_agents": "agent_specifier",
                "decompose_tasks": "task_decomposer",
                "design_petri_net": "petri_net_designer",
                "generate_yaml_files": "yaml_generator",
                "generate_python_code": "code_generator",
                # Specification multi-step pipeline agents
                "classify_specification_intent": "specification_router",
                "extract_specification_entities": "specification_entity_extractor",
                "research_specification_context": "specification_web_researcher",
                "compose_spec_use_cases": "specification_composer",
                "compose_spec_document": "specification_composer",
                "verify_specification_grounding": "specification_verifier",
                "validate_specification_compliance": "specification_compliance",
                "apply_spec_corrections": "specification_formatter",
                "render_final_specification": "specification_formatter"
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

        # Note: After .format(), all template variables have been replaced with actual values.
        # Any remaining braces {} in the content (from JSON in LLM outputs) should not be
        # interpreted as template variables by CrewAI - we'll pass empty inputs to prevent this.

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
        # No escaping needed - expected_output now uses textual descriptions instead of JSON with braces

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
        # Pass empty inputs since we've already formatted the description with all values
        # This prevents CrewAI from trying to interpolate any braces in the content

        if hasattr(crew, 'kickoff'):
            result = crew.kickoff(inputs={})
        elif hasattr(crew, 'executar'):
            result = crew.executar(inputs={})
        else:
            raise AttributeError(f"Team object has neither 'kickoff' nor 'executar' method: {type(crew).__name__}")

        # Debug CrewOutput structure to understand what we're receiving
        print(f"\n{'='*80}")
        print(f"[CREW RESULT DEBUG] Task: {task_name}")
        print(f"[CREW RESULT DEBUG] Result type: {type(result)}")
        print(f"[CREW RESULT DEBUG] Has 'raw' attribute: {hasattr(result, 'raw')}")
        print(f"[CREW RESULT DEBUG] Has 'json_dict' attribute: {hasattr(result, 'json_dict')}")
        print(f"[CREW RESULT DEBUG] Has 'model_dump' method: {hasattr(result, 'model_dump')}")
        if hasattr(result, 'raw'):
            raw_preview = str(result.raw)[:500] if result.raw else '(None)'
            print(f"[CREW RESULT DEBUG] result.raw preview (first 500 chars):\n{raw_preview}")
        if hasattr(result, 'json_dict'):
            json_dict_keys = list(result.json_dict.keys()) if result.json_dict else '(None)'
            print(f"[CREW RESULT DEBUG] result.json_dict keys: {json_dict_keys}")
        print(f"{'='*80}\n")

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

    # Define execution order (NOW WITH 12 TASKS!)
    pipeline_tasks = [
        "analyze_document",
        "extract_requirements",
        "research_additional_info",  # Web research
        "enrich_requirements",      # NEW: Validate completeness + AI suggestions (replaces validate_requirements)
        "validate_quality",          # NEW: Quality validation + gap analysis
        "generate_document",         # NEW: Generate final markdown document
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

    # Dividido em 3 tasks para reduzir tamanho do prompt e evitar timeouts
    state = execute_task_with_context("enrich_requirements", state)
    state = execute_task_with_context("validate_quality", state)
    state = execute_task_with_context("generate_document", state)

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


def execute_specification_workflow(
    project_id: str,
    requirements_document: str,
    requirements_version: int = 1,
    requirements_created_at: str = "",
    project_name: str = "Sistema",
    detail_level: str = "detailed",
    target_audience: str = "mixed",
    use_deepseek: bool = False,
    verbose_callback: Optional[Callable[[str], None]] = None
) -> LangNetFullState:
    """
    Execute the multi-step specification generation workflow following Generative Computing principles.

    Pipeline:
    1. classify_specification_intent (RouterAgent) - Classify intent and scope
    2. extract_specification_entities (EntityExtractorAgent) - Extract all entities with context_ids
    3. research_specification_context (WebResearcherAgent) - Research standards and best practices
    4. compose_spec_use_cases (ComposerAgent) - Generate detailed Use Cases (section 5 only)
    5. compose_spec_document (ComposerAgent) - Generate sections 1-4 and 6-14
    6. verify_specification_grounding (VerifierAgent) - Validate all items have context support
    7. validate_specification_compliance (ComplianceAgent) - Check language, structure, policies
    8. apply_spec_corrections (FormatterAgent) - Apply verification and compliance corrections
    9. render_final_specification (FormatterAgent) - Render final Markdown document

    Args:
        project_id: Project UUID
        requirements_document: The requirements document (Markdown) to generate specification from
        requirements_version: Version number of the requirements document
        requirements_created_at: Creation date of the requirements document
        project_name: Name of the project/system
        detail_level: Level of detail ("detailed", "summary", "executive")
        target_audience: Target audience ("technical", "business", "mixed")
        use_deepseek: If True, uses DeepSeek LLM; if False, uses configured LLM
        verbose_callback: Optional callback for progress updates

    Returns:
        Final state with specification document in spec_document_md
    """
    print(f"\n{'='*80}")
    print(f"[SPECIFICATION] Starting multi-step specification generation workflow")
    print(f"[SPECIFICATION] Pipeline: Router → EntityExtractor → WebResearcher → UseCases → Document → Verifier → Compliance → Corrections → Renderer")
    print(f"[SPECIFICATION] Requirements document length: {len(requirements_document)} chars")
    print(f"[SPECIFICATION] Project: {project_name}, Version: {requirements_version}")
    print(f"{'='*80}\n")

    # Initialize state with specification-specific parameters
    state = init_full_state(
        project_id=project_id,
        document_id="spec_gen",
        document_path=""
    )

    # Add specification-specific state
    state["requirements_document"] = requirements_document
    state["requirements_version"] = requirements_version
    state["requirements_created_at"] = requirements_created_at or datetime.now().strftime("%Y-%m-%d")
    state["project_name"] = project_name
    state["spec_detail_level"] = detail_level
    state["spec_target_audience"] = target_audience
    state["use_deepseek"] = use_deepseek

    # Define specification pipeline tasks (9 steps following Generative Computing)
    spec_pipeline_tasks = [
        "classify_specification_intent",      # Step 1: Router - classify intent
        "extract_specification_entities",     # Step 2: EntityExtractor - extract entities with context_ids
        "research_specification_context",     # Step 3: WebResearcher - research standards and best practices
        "compose_spec_use_cases",             # Step 4: Composer - generate Use Cases (section 5)
        "compose_spec_document",              # Step 5: Composer - generate sections 1-4 and 6-14
        "verify_specification_grounding",     # Step 6: Verifier - validate grounding
        "validate_specification_compliance",  # Step 7: Compliance - check language/structure
        "apply_spec_corrections",             # Step 8: Formatter - apply corrections
        "render_final_specification"          # Step 9: Formatter - render final document
    ]

    # Execute each task sequentially
    for i, task_name in enumerate(spec_pipeline_tasks, 1):
        if verbose_callback:
            verbose_callback(f"\n[Step {i}/9] Executing: {task_name}")

        print(f"\n{'='*80}")
        print(f"[SPECIFICATION] Step {i}/9: {task_name}")
        print(f"{'='*80}\n")

        state = execute_task_with_context(task_name, state, verbose_callback)

        # Check for errors
        if state.get("errors") and len(state["errors"]) > 0:
            print(f"\n⚠️  [SPECIFICATION] Pipeline stopped due to error in {task_name}")
            if verbose_callback:
                verbose_callback(f"Pipeline stopped due to error in {task_name}")
            break

        # Log intermediate progress
        if verbose_callback:
            if task_name == "classify_specification_intent":
                verbose_callback(f"   Intent: {state.get('spec_intent', 'N/A')}, Scope: {state.get('spec_scope', 'N/A')}")
            elif task_name == "extract_specification_entities":
                verbose_callback(f"   Extracted: {len(state.get('spec_actors', []))} actors, {len(state.get('spec_use_cases', []))} use cases")
            elif task_name == "research_specification_context":
                summary = state.get('spec_research_summary', {})
                verbose_callback(f"   Researched: {summary.get('total_standards', 0)} standards, {summary.get('total_compliance', 0)} compliance, {summary.get('total_practices', 0)} practices")
            elif task_name == "compose_spec_use_cases":
                verbose_callback(f"   Use cases generated: {state.get('spec_use_cases_count', 0)}")
            elif task_name == "compose_spec_document":
                verbose_callback(f"   Generated: {len(state.get('spec_sections', []))} sections")
            elif task_name == "verify_specification_grounding":
                verbose_callback(f"   Grounding score: {state.get('spec_grounding_score', 'N/A')}%")
            elif task_name == "validate_specification_compliance":
                verbose_callback(f"   Compliance: {'OK' if state.get('spec_compliance_ok') else 'Issues found'}")
            elif task_name == "apply_spec_corrections":
                verbose_callback(f"   Corrections applied: {len(state.get('spec_corrections_applied', []))}")
            elif task_name == "render_final_specification":
                verbose_callback(f"   Final status: {state.get('spec_status', 'N/A')}")

    # Mark completion
    state["completed_at"] = datetime.now().isoformat()

    # Log final results
    print(f"\n{'='*80}")
    print(f"[SPECIFICATION] Workflow completed")
    print(f"[SPECIFICATION] Status: {state.get('spec_status', 'unknown')}")
    print(f"[SPECIFICATION] Document length: {len(state.get('spec_document_md', ''))} chars")
    print(f"[SPECIFICATION] Grounding score: {state.get('spec_grounding_score_final', 'N/A')}")
    print(f"[SPECIFICATION] Compliance score: {state.get('spec_compliance_score_final', 'N/A')}")
    print(f"[SPECIFICATION] Total sections: {state.get('spec_total_sections', 'N/A')}")
    print(f"[SPECIFICATION] Complete sections: {state.get('spec_complete_sections', 'N/A')}")
    print(f"[SPECIFICATION] Gaps: {len(state.get('spec_final_gaps', []))}")
    print(f"[SPECIFICATION] Warnings: {len(state.get('spec_warnings', []))}")
    print(f"{'='*80}\n")

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

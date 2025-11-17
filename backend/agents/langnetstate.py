"""
LangNet Context States
Based on tropicalagentssalesv6.py Context State List pattern

These TypedDicts define the accumulated state that flows through the workflow.
Each task can read from and write to this state using input/output functions.
"""
from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime


class DocumentAnalysisState(TypedDict, total=False):
    """
    State for document analysis workflow

    Flow: Upload → Parse → Extract Structure
    """
    # Inputs
    document_id: str
    document_path: str
    document_type: str  # pdf, docx, txt, md

    # Task outputs (raw JSON strings from LLM)
    document_analysis_json: str

    # Parsed data (structured)
    document_content: str
    document_structure: Dict[str, Any]  # {sections: [...], headings: [...]}
    document_metadata: Dict[str, Any]   # {word_count, page_count, author, etc}

    # Workflow metadata
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str
    errors: List[Dict[str, Any]]


class RequirementsExtractionState(TypedDict, total=False):
    """
    State for requirements extraction workflow

    Flow: Document → Extract → Validate → Specify
    """
    # Inputs (from previous state or database)
    document_id: str
    document_content: str
    document_structure: Dict[str, Any]

    # Task outputs (raw JSON strings)
    requirements_json: str
    validation_json: str
    specification_md: str

    # Parsed data (structured)
    requirements_data: Dict[str, Any]  # {functional_requirements: [...], non_functional_requirements: [...], business_rules: [...], actors: [...], use_cases: [...]}
    validation_data: Dict[str, Any]    # {valid_requirements: [...], issues_found: [...], scores: {...}}
    specification_data: Dict[str, Any]  # {title, sections: [...], metadata: {...}}

    # Workflow metadata
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str
    errors: List[Dict[str, Any]]


class AgentDesignState(TypedDict, total=False):
    """
    State for agent design workflow

    Flow: Requirements → Suggest Agents → Decompose Tasks
    """
    # Inputs
    project_id: str
    requirements_data: Dict[str, Any]
    specification_data: Dict[str, Any]

    # Task outputs (raw JSON strings)
    agents_suggestions_json: str
    tasks_decomposition_json: str

    # Parsed data (structured)
    agents_data: List[Dict[str, Any]]  # [{agent_id, name, role, goal, backstory, tools, ...}, ...]
    tasks_data: List[Dict[str, Any]]   # [{task_id, name, description, agent_id, tools, ...}, ...]
    dependencies: Dict[str, List[str]]  # {task_id: [required_task_ids]}
    execution_order: List[str]          # [task_id1, task_id2, ...]
    parallel_groups: List[List[str]]    # [[task_id1, task_id2], [task_id3]]

    # Workflow metadata
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str
    errors: List[Dict[str, Any]]


class WorkflowDesignState(TypedDict, total=False):
    """
    State for workflow design using Petri Nets

    Flow: Tasks + Dependencies → Petri Net Model
    """
    # Inputs
    project_id: str
    tasks_data: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    agents_data: List[Dict[str, Any]]

    # Task outputs (raw JSON strings)
    petri_net_json: str

    # Parsed data (structured)
    petri_net_data: Dict[str, Any]  # {places: [...], transitions: [...], arcs: [...], agents: [...], properties: {...}}

    # Workflow metadata
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str
    errors: List[Dict[str, Any]]


class CodeGenerationState(TypedDict, total=False):
    """
    State for code generation

    Flow: Agents + Tasks + Petri Net → YAML → Python Code
    """
    # Inputs
    project_id: str
    agents_data: List[Dict[str, Any]]
    tasks_data: List[Dict[str, Any]]
    petri_net_data: Dict[str, Any]
    framework_choice: str  # crewai, autogen, langgraph, custom

    # Task outputs (raw JSON strings)
    yaml_files_json: str
    code_generation_json: str

    # Parsed data (structured)
    agents_yaml: str                    # Complete agents.yaml content
    tasks_yaml: str                     # Complete tasks.yaml content
    generated_code: str                 # Main Python file content
    generated_files: Dict[str, str]     # {filename: content}
    requirements_txt: str               # Python dependencies
    readme_md: str                      # Usage documentation

    # Workflow metadata
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    timestamp: str
    errors: List[Dict[str, Any]]


class LangNetFullState(TypedDict, total=False):
    """
    Complete state for full LangNet pipeline

    This accumulates ALL fields from all workflow states above.
    Used when executing the complete end-to-end pipeline.

    Flow: Document → Requirements → Agents → Tasks → Workflow → Code
    """
    # Project context
    project_id: str
    project_name: str
    project_domain: str
    additional_instructions: str  # Custom instructions from user

    # Document Analysis State
    document_id: str
    document_path: str
    document_type: str
    document_analysis_json: str
    document_content: str
    document_structure: Dict[str, Any]
    document_metadata: Dict[str, Any]

    # Requirements Extraction State
    requirements_json: str
    research_findings_json: str  # Web research results
    validation_json: str
    requirements_document_md: str  # Generated Requirements Document (Section 2.1)
    specification_md: str  # Functional Specification Document (Section 2.2)
    requirements_data: Dict[str, Any]
    research_findings_data: Dict[str, Any]  # Parsed research data
    validation_data: Dict[str, Any]
    specification_data: Dict[str, Any]

    # Agent Design State
    agents_suggestions_json: str
    tasks_decomposition_json: str
    agents_data: List[Dict[str, Any]]
    tasks_data: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    execution_order: List[str]
    parallel_groups: List[List[str]]

    # Workflow Design State
    petri_net_json: str
    petri_net_data: Dict[str, Any]

    # Code Generation State
    framework_choice: str
    yaml_files_json: str
    code_generation_json: str
    agents_yaml: str
    tasks_yaml: str
    generated_code: str
    generated_files: Dict[str, str]
    requirements_txt: str
    readme_md: str

    # Workflow metadata (shared across all states)
    execution_log: List[Dict[str, Any]]
    current_task: Optional[str]
    current_phase: Optional[str]  # document_analysis, requirements_extraction, agent_design, workflow_design, code_generation
    timestamp: str
    started_at: str
    completed_at: Optional[str]
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]

    # Progress tracking
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    progress_percentage: float


# Helper functions for state management

def init_execution_log() -> List[Dict[str, Any]]:
    """Initialize execution log with empty array"""
    return []


def log_task_start(state: Dict[str, Any], task_name: str) -> Dict[str, Any]:
    """Log task start in execution log"""
    execution_log = state.get("execution_log", [])
    execution_log.append({
        "task": task_name,
        "status": "started",
        "timestamp": datetime.now().isoformat(),
        "phase": state.get("current_phase", "unknown")
    })

    return {
        **state,
        "execution_log": execution_log,
        "current_task": task_name,
        "timestamp": datetime.now().isoformat()
    }


def log_task_complete(state: Dict[str, Any], task_name: str, output: Any = None) -> Dict[str, Any]:
    """Log task completion in execution log"""
    execution_log = state.get("execution_log", [])

    log_entry = {
        "task": task_name,
        "status": "completed",
        "timestamp": datetime.now().isoformat(),
        "phase": state.get("current_phase", "unknown")
    }

    if output:
        log_entry["output_preview"] = str(output)[:200]  # First 200 chars

    execution_log.append(log_entry)

    completed_tasks = state.get("completed_tasks", 0) + 1
    total_tasks = state.get("total_tasks", 1)
    progress_percentage = (completed_tasks / total_tasks) * 100

    return {
        **state,
        "execution_log": execution_log,
        "current_task": None,
        "completed_tasks": completed_tasks,
        "progress_percentage": progress_percentage,
        "timestamp": datetime.now().isoformat()
    }


def log_task_error(state: Dict[str, Any], task_name: str, error: Exception) -> Dict[str, Any]:
    """Log task error in execution log"""
    execution_log = state.get("execution_log", [])
    errors = state.get("errors", [])

    execution_log.append({
        "task": task_name,
        "status": "failed",
        "timestamp": datetime.now().isoformat(),
        "phase": state.get("current_phase", "unknown")
    })

    errors.append({
        "task": task_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat()
    })

    failed_tasks = state.get("failed_tasks", 0) + 1

    return {
        **state,
        "execution_log": execution_log,
        "errors": errors,
        "current_task": None,
        "failed_tasks": failed_tasks,
        "timestamp": datetime.now().isoformat()
    }


def init_full_state(
    project_id: str,
    document_id: str,
    document_path: str,
    framework_choice: str = "crewai",
    project_name: str = "",
    project_description: str = "",
    project_domain: str = "",
    additional_instructions: str = "",
    document_type: str = "pdf",
    document_content: str = ""
) -> LangNetFullState:
    """
    Initialize a complete LangNetFullState for full pipeline execution

    Args:
        project_id: UUID of the project
        document_id: UUID of the document being analyzed
        document_path: File path to the uploaded document
        framework_choice: Target framework for code generation (crewai, autogen, langgraph, custom)
        project_name: Name of the project
        project_description: Description of the project
        project_domain: Domain/industry of the project
        additional_instructions: User instructions for analysis
        document_type: Type of document being analyzed
        document_content: Pre-extracted and chunked document content (optional)

    Returns:
        Initialized LangNetFullState with empty fields and metadata
    """
    now = datetime.now().isoformat()

    return {
        # Project context
        "project_id": project_id,
        "project_name": project_name,
        "project_domain": project_domain,
        "project_description": project_description,
        "additional_instructions": additional_instructions,

        # Document context
        "document_id": document_id,
        "document_path": document_path,
        "document_type": document_type,
        "document_content": document_content,  # Pre-extracted text
        "framework_choice": framework_choice,

        # Initialize metadata
        "execution_log": [],
        "errors": [],
        "warnings": [],
        "current_task": None,
        "current_phase": "document_analysis",
        "timestamp": now,
        "started_at": now,
        "completed_at": None,

        # Initialize progress tracking
        "total_tasks": 9,  # Total tasks in full pipeline
        "completed_tasks": 0,
        "failed_tasks": 0,
        "progress_percentage": 0.0
    }

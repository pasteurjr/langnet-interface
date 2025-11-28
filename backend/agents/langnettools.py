"""
LangNet Custom Tools
Tools for document parsing, database access, and code generation
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# Tool for reading and parsing documents
class DocumentReaderToolInput(BaseModel):
    """Input schema for DocumentReaderTool"""
    document_path: str = Field(description="Path to the document file")
    document_type: str = Field(description="Type of document: pdf, docx, txt, md")


class DocumentReaderTool(BaseTool):
    """
    Tool for reading and parsing documents of various formats
    """
    name: str = "document_reader"
    description: str = """
    Read and parse documents in various formats (PDF, DOCX, TXT, MD).
    Returns the full text content and document structure.
    Input: document_path (str), document_type (str)
    """
    args_schema: type[BaseModel] = DocumentReaderToolInput

    def _run(self, document_path: str, document_type: str) -> str:
        """Execute the tool"""
        try:
            from app.parsers import DocumentParser

            result = DocumentParser.parse(document_path)

            if not result["success"]:
                return json.dumps({
                    "error": result["error"],
                    "success": False
                })

            return json.dumps({
                "content": result["text"],
                "metadata": result["metadata"],
                "format": result["format"],
                "success": True
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "success": False
            })

    async def _arun(self, document_path: str, document_type: str) -> str:
        """Async version"""
        return self._run(document_path, document_type)


# Tool for writing YAML files
class YAMLWriterToolInput(BaseModel):
    """Input schema for YAMLWriterTool"""
    content: str = Field(description="YAML content as Python dict string or JSON")
    file_path: str = Field(description="Path where to save the YAML file")


class YAMLWriterTool(BaseTool):
    """
    Tool for writing YAML configuration files
    """
    name: str = "yaml_writer"
    description: str = """
    Write YAML configuration files with proper formatting.
    Input: content (str - JSON or dict), file_path (str)
    """
    args_schema: type[BaseModel] = YAMLWriterToolInput

    def _run(self, content: str, file_path: str) -> str:
        """Execute the tool"""
        try:
            # Parse content if it's JSON string
            if isinstance(content, str):
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    # If not JSON, try to eval as Python dict
                    data = eval(content)
            else:
                data = content

            # Write YAML file
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            return json.dumps({
                "success": True,
                "file_path": str(path),
                "message": f"YAML file written successfully to {path}"
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    async def _arun(self, content: str, file_path: str) -> str:
        """Async version"""
        return self._run(content, file_path)


# Tool for writing Markdown files
class MarkdownWriterToolInput(BaseModel):
    """Input schema for MarkdownWriterTool"""
    content: str = Field(description="Markdown content to write")
    file_path: str = Field(description="Path where to save the Markdown file")


class MarkdownWriterTool(BaseTool):
    """
    Tool for writing Markdown documentation files
    """
    name: str = "markdown_writer"
    description: str = """
    Write Markdown documentation files.
    Input: content (str), file_path (str)
    """
    args_schema: type[BaseModel] = MarkdownWriterToolInput

    def _run(self, content: str, file_path: str) -> str:
        """Execute the tool"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return json.dumps({
                "success": True,
                "file_path": str(path),
                "message": f"Markdown file written successfully to {path}"
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    async def _arun(self, content: str, file_path: str) -> str:
        """Async version"""
        return self._run(content, file_path)


# Tool for writing Python code files
class PythonCodeWriterToolInput(BaseModel):
    """Input schema for PythonCodeWriterTool"""
    code: str = Field(description="Python code to write")
    file_path: str = Field(description="Path where to save the Python file")


class PythonCodeWriterTool(BaseTool):
    """
    Tool for writing Python code files
    """
    name: str = "python_code_writer"
    description: str = """
    Write Python code files with proper formatting.
    Input: code (str), file_path (str)
    """
    args_schema: type[BaseModel] = PythonCodeWriterToolInput

    def _run(self, code: str, file_path: str) -> str:
        """Execute the tool"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(code)

            return json.dumps({
                "success": True,
                "file_path": str(path),
                "message": f"Python file written successfully to {path}"
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    async def _arun(self, code: str, file_path: str) -> str:
        """Async version"""
        return self._run(code, file_path)


# Tool for querying LangNet database
class DatabaseQueryToolInput(BaseModel):
    """Input schema for DatabaseQueryTool"""
    query: str = Field(description="SQL query to execute")
    params: Optional[List] = Field(default=None, description="Query parameters")


class DatabaseQueryTool(BaseTool):
    """
    Tool for querying the LangNet MySQL database
    """
    name: str = "database_query"
    description: str = """
    Query the LangNet database to retrieve projects, agents, tasks, documents, etc.
    Input: query (str), params (list, optional)
    Returns: JSON array of results
    """
    args_schema: type[BaseModel] = DatabaseQueryToolInput

    def _run(self, query: str, params: Optional[List] = None) -> str:
        """Execute the tool"""
        try:
            from app.database import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Fetch results
            rows = cursor.fetchall()

            # Convert to list of dicts
            results = []
            for row in rows:
                results.append(row)

            cursor.close()
            conn.close()

            return json.dumps({
                "success": True,
                "results": results,
                "count": len(results)
            }, indent=2, default=str)

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    async def _arun(self, query: str, params: Optional[List] = None) -> str:
        """Async version"""
        return self._run(query, params)


# Tool for validating YAML syntax
class YAMLValidatorToolInput(BaseModel):
    """Input schema for YAMLValidatorTool"""
    yaml_content: str = Field(description="YAML content to validate")


class YAMLValidatorTool(BaseTool):
    """
    Tool for validating YAML syntax
    """
    name: str = "yaml_validator"
    description: str = """
    Validate YAML syntax and structure.
    Input: yaml_content (str)
    Returns: validation result with errors if any
    """
    args_schema: type[BaseModel] = YAMLValidatorToolInput

    def _run(self, yaml_content: str) -> str:
        """Execute the tool"""
        try:
            # Try to parse YAML
            data = yaml.safe_load(yaml_content)

            return json.dumps({
                "valid": True,
                "message": "YAML is valid",
                "parsed_keys": list(data.keys()) if isinstance(data, dict) else None
            })

        except yaml.YAMLError as e:
            return json.dumps({
                "valid": False,
                "error": str(e),
                "error_type": "YAMLError"
            })
        except Exception as e:
            return json.dumps({
                "valid": False,
                "error": str(e),
                "error_type": type(e).__name__
            })

    async def _arun(self, yaml_content: str) -> str:
        """Async version"""
        return self._run(yaml_content)


# ============================================================================
# WEB SEARCH TOOLS
# ============================================================================

class SerperSearchToolInput(BaseModel):
    """Input schema for SerperSearchTool"""
    query: str = Field(description="Search query string")
    num_results: int = Field(default=10, description="Number of results to return")


class SerperSearchTool(BaseTool):
    """
    🔍 Serper (Google) Search - Use for SPECIFIC & UP-TO-DATE information:
    - Specific technologies, frameworks, and libraries
    - Regulatory and compliance information (LGPD, GDPR, PCI-DSS)
    - Corporate and product-specific documentation
    - Latest news, updates, and current best practices
    - Official documentation and standards

    WHEN TO USE: Need most current, specific, or regulatory information
    BEST FOR: Compliance requirements, specific tech docs, latest standards
    AVOID FOR: General tutorials, common patterns, academic research

    EXAMPLES:
    ✅ "LGPD data protection requirements Brazil 2024"
    ✅ "React 19 new features official documentation"
    ✅ "PCI-DSS compliance requirements e-commerce"
    ❌ "how to build REST API tutorial" (use DuckDuckGo)
    ❌ "microservices architecture research" (use Tavily)
    """
    name: str = "serper_search"
    description: str = """
    🔍 Serper (Google) Search - Use for SPECIFIC & UP-TO-DATE info:
    - Specific technologies, frameworks, libraries, official docs
    - Regulatory/compliance (LGPD, GDPR, PCI-DSS, HIPAA)
    - Corporate/product documentation, latest standards

    WHEN TO USE: Need current, specific, or regulatory information
    BEST FOR: Compliance, specific tech, latest updates

    Input: query (str), num_results (int, default=10)
    Returns: JSON with search results including title, link, snippet
    """
    args_schema: type[BaseModel] = SerperSearchToolInput

    def _run(self, query: str, num_results: int = 10) -> str:
        """Execute web search"""
        try:
            import os
            import requests

            api_key = os.getenv("SERPER_API_KEY")
            if not api_key:
                return json.dumps({
                    "success": False,
                    "error": "SERPER_API_KEY not configured"
                })

            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": query,
                "num": num_results
            })
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract organic results
            results = []
            for item in data.get("organic", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "position": item.get("position", 0)
                })

            return json.dumps({
                "success": True,
                "query": query,
                "total_results": len(results),
                "results": results,
                "search_metadata": {
                    "engine": "google",
                    "api": "serper"
                }
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "query": query
            })

    async def _arun(self, query: str, num_results: int = 10) -> str:
        """Async version"""
        return self._run(query, num_results)


class SerpAPISearchToolInput(BaseModel):
    """Input schema for SerpAPISearchTool"""
    query: str = Field(description="Search query string")
    num_results: int = Field(default=10, description="Number of results to return")
    search_engine: str = Field(default="duckduckgo", description="Search engine: duckduckgo, google, bing")


class SerpAPISearchTool(BaseTool):
    """
    🦆 SerpAPI (DuckDuckGo) Search - Use for GENERAL web searches:
    - Common development patterns and best practices
    - Public documentation, tutorials, and how-to guides
    - General technical concepts and explanations
    - Open source projects and community knowledge
    - Programming languages, frameworks basics

    WHEN TO USE: Default choice for most searches, privacy-focused, general knowledge
    BEST FOR: Tutorials, common patterns, general best practices, how-to guides
    AVOID FOR: Regulatory info, academic research, specific corporate docs

    EXAMPLES:
    ✅ "how to implement JWT authentication Node.js"
    ✅ "React best practices component structure"
    ✅ "microservices vs monolithic architecture pros cons"
    ❌ "LGPD compliance requirements" (use Serper)
    ❌ "security architecture research papers" (use Tavily)
    """
    name: str = "serpapi_search"
    description: str = """
    🦆 SerpAPI (DuckDuckGo) Search - Use for GENERAL searches:
    - Common patterns, best practices, tutorials, how-to guides
    - Public documentation, general technical concepts
    - Open source projects, community knowledge

    WHEN TO USE: Default for most searches, general knowledge
    BEST FOR: Tutorials, common patterns, general best practices

    Input: query (str), num_results (int), search_engine (str, default='duckduckgo')
    Returns: JSON with search results
    """
    args_schema: type[BaseModel] = SerpAPISearchToolInput

    def _run(self, query: str, num_results: int = 10, search_engine: str = "duckduckgo") -> str:
        """Execute web search"""
        try:
            import os
            import requests

            api_key = os.getenv("SERPAPI_API_KEY")
            if not api_key:
                return json.dumps({
                    "success": False,
                    "error": "SERPAPI_API_KEY not configured"
                })

            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "engine": search_engine,
                "api_key": api_key,
                "num": num_results
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract organic results
            results = []
            for item in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "position": item.get("position", 0),
                    "displayed_link": item.get("displayed_link", "")
                })

            return json.dumps({
                "success": True,
                "query": query,
                "search_engine": search_engine,
                "total_results": len(results),
                "results": results,
                "search_metadata": data.get("search_metadata", {})
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "query": query,
                "search_engine": search_engine
            })

    async def _arun(self, query: str, num_results: int = 10, search_engine: str = "duckduckgo") -> str:
        """Async version"""
        return self._run(query, num_results, search_engine)


class TavilySearchToolInput(BaseModel):
    """Input schema for TavilySearchTool"""
    query: str = Field(description="Search query string")
    search_depth: str = Field(default="basic", description="Search depth: 'basic' or 'advanced'")
    max_results: int = Field(default=5, description="Maximum number of results to return")


class TavilySearchTool(BaseTool):
    """
    🔬 Tavily Search - Use for DEEP RESEARCH and authoritative analysis:
    - Academic papers and scientific articles
    - In-depth technical analysis and whitepapers
    - Market trends and industry research reports
    - Research-backed information with citations

    WHEN TO USE: Need authoritative, well-researched, credible content
    BEST FOR: Requirements analysis, compliance research, technical specifications
    AVOID FOR: Quick lookups, general tutorials, common patterns

    EXAMPLES:
    ✅ "microservices architecture research papers security"
    ✅ "LGPD compliance requirements academic analysis"
    ✅ "healthcare system regulations Brazil ANVISA"
    ❌ "how to implement JWT authentication" (use DuckDuckGo)
    ❌ "React best practices tutorial" (use DuckDuckGo)
    """
    name: str = "tavily_search"
    description: str = """
    🔬 Tavily Search - Use for DEEP RESEARCH and analysis:
    - Academic papers, scientific articles, research studies
    - In-depth technical analysis, whitepapers, industry reports
    - Regulatory and compliance research with citations
    - Market trends backed by authoritative sources

    WHEN TO USE: Need credible, well-researched, authoritative information
    BEST FOR: Requirements analysis, regulatory compliance, technical specs

    Input: query (str), search_depth ('basic' or 'advanced'), max_results (int)
    Returns: JSON with detailed results including content, citations, relevance scores
    """
    args_schema: type[BaseModel] = TavilySearchToolInput

    def _run(self, query: str, search_depth: str = "basic", max_results: int = 5) -> str:
        """Execute Tavily deep search"""
        try:
            import os
            import requests

            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                return json.dumps({
                    "success": False,
                    "error": "TAVILY_API_KEY not configured"
                })

            url = "https://api.tavily.com/search"
            payload = {
                "api_key": api_key,
                "query": query,
                "search_depth": search_depth,  # "basic" or "advanced"
                "max_results": max_results,
                "include_answer": True,
                "include_raw_content": False
            }

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Extract results
            results = []
            for item in data.get("results", [])[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score", 0.0),
                    "published_date": item.get("published_date", "")
                })

            return json.dumps({
                "success": True,
                "query": query,
                "search_depth": search_depth,
                "answer": data.get("answer", ""),  # AI-generated summary
                "total_results": len(results),
                "results": results,
                "search_metadata": {
                    "engine": "tavily",
                    "response_time": data.get("response_time", 0)
                }
            })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "query": query,
                "search_depth": search_depth
            })

    async def _arun(self, query: str, search_depth: str = "basic", max_results: int = 5) -> str:
        """Async version"""
        return self._run(query, search_depth, max_results)


# Factory function to create all tools
def create_langnet_tools() -> Dict[str, BaseTool]:
    """
    Create all LangNet custom tools

    Returns:
        Dictionary mapping tool names to tool instances
    """
    return {
        "document_reader": DocumentReaderTool(),
        "yaml_writer": YAMLWriterTool(),
        "markdown_writer": MarkdownWriterTool(),
        "python_code_writer": PythonCodeWriterTool(),
        "database_query": DatabaseQueryTool(),
        "yaml_validator": YAMLValidatorTool(),
        "serper_search": SerperSearchTool(),
        "serpapi_search": SerpAPISearchTool(),
        "tavily_search": TavilySearchTool()
    }


# Export all tools
__all__ = [
    "DocumentReaderTool",
    "YAMLWriterTool",
    "MarkdownWriterTool",
    "PythonCodeWriterTool",
    "DatabaseQueryTool",
    "YAMLValidatorTool",
    "SerperSearchTool",
    "SerpAPISearchTool",
    "create_langnet_tools"
]

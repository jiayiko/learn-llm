"""Pydantic models and data schemas for Scout Agent."""
from typing import List, TypedDict, Annotated
import operator
from pydantic import BaseModel, Field


class RepoAnalysis(BaseModel):
    """Structured analysis of a GitHub repository."""
    name: str = Field(description="Full name of the repository")
    summary: str = Field(description="A brief technical overview")
    language: str = Field(description="Programming language used")
    tech_stack: List[str] = Field(description="Specific libraries found in requirements.txt, README, package.json, or other similar files")
    core_workflow: str = Field(description="Logic workflow summary of how the project works end-to-end based on the core_code_context and README")
    key_learnings: List[str] = Field(description="3-4 specific concepts or patterns a user will learn by doing this project")
    complexity_level: str = Field(description="Beginner, Intermediate, or Advanced based on code structure")
    activity_status: str = Field(description="Maintenance status based on commit dates")
    stars: int = Field(description="Number of stars")
    forks: int = Field(description="Number of forks")


class SearchStrategy(BaseModel):
    """Search strategy with query expansion."""
    queries: List[str] = Field(
        description="A list of 3 distinct GitHub search strings (Broad, Formal, and Academic)."
    )
    expanded_terms: List[str] = Field(
        description="Technical synonyms, acronyms, and related algorithms identified from the intent."
    )
    reasoning: str = Field(
        description="Brief technical justification for why these specific expansion terms were chosen."
    )
    keywords: List[str] = Field(
        description="Core keywords strictly derived from the user input. These should closely match the user's original wording or very near paraphrases, without introducing new technical concepts."
    )


class FileSelection(BaseModel):
    """Selected files for core logic extraction."""
    selected_files: List[str] = Field(description="List of 3-5 specific file paths to read for core logic.")
    reasoning: str = Field(description="Short explanation of why these files look like the entry points.")


class AgentState(TypedDict):
    """State object for the agentic graph."""
    user_query: str
    search_strategy: SearchStrategy
    raw_repos: List[dict]
    analyzed_results: Annotated[List[RepoAnalysis], operator.add]  # Appends results
    error_count: int
    comparison_table: str

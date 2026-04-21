"""Repository analysis utilities."""
import time
from typing import Optional, Tuple
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.models import RepoAnalysis, FileSelection
from src.llm import get_llm_client
from src.api import get_file_structure


def extract_core_logic_agentic(repo_full_name: str, user_intent: str) -> Tuple[str, str]:
    """
    Extract core logic from a repository using agentic approach.
    
    Args:
        repo_full_name: Repository full name (owner/repo)
        user_intent: User's search intent
        
    Returns:
        Tuple of (combined_code, reasoning)
    """
    llm = get_llm_client(temperature=0)
    parser = PydanticOutputParser(pydantic_object=FileSelection)
    
    # Pass 1: Get the Map
    file_map = get_file_structure(repo_full_name)
    
    # Pass 2: LLM Decides which files to 'open'
    selection_prompt = ChatPromptTemplate.from_template(
        "You are a Senior Architect. Given this file list from a GitHub repo, identify the 3-5 files that contain the CORE implementation logic for: '{intent}'\n\n"
        "File List:\n{files}\n\n"
        "{format_instructions}"
    )
    
    selection_chain = selection_prompt | llm | parser
    selection = selection_chain.invoke({
        "intent": user_intent,
        "files": file_map,
        "format_instructions": parser.get_format_instructions()
    })
    
    # Pass 3: Fetch content and summarize workflow
    from github import Github
    import base64
    import os
    
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    combined_code = ""

    st.write("Selected files for core logic extraction:", selection.selected_files)
    
    for path in selection.selected_files:
        try:
            content = repo.get_contents(path)
            combined_code += f"\n--- FILE: {path} ---\n{base64.b64decode(content.content).decode('utf-8')[:2000]}"
        except Exception:
            continue
            
    return combined_code, selection.reasoning


def analyze_single_repo(
    repo_metadata: dict,
    core_code: str,
    user_query: str
) -> Optional[RepoAnalysis]:
    """
    Analyze a single repository and return structured analysis.
    
    Acts as the 'Technical Lead' to synthesize metadata and source code 
    into a structured RepoAnalysis object.
    
    Args:
        repo_metadata: Repository metadata dictionary
        core_code: Core source code context
        user_query: User's search query
        
    Returns:
        RepoAnalysis object or None if analysis fails
    """
    llm = get_llm_client(temperature=0)
    parser = PydanticOutputParser(pydantic_object=RepoAnalysis)
    
    prompt = ChatPromptTemplate.from_template(
        "You are a Senior Technical Lead. A researcher is looking for: '{query}'\n\n"
        "### REPOSITORY METADATA\n"
        "Name: {name}\n"
        "Description: {desc}\n"
        "Stars: {stars}\n"
        "Requirements: {reqs}\n\n"
        "### CORE SOURCE CODE CONTEXT\n"
        "{code}\n\n"
        "### TASK\n"
        "Analyze the provided data. Your 'core_workflow' must be a step-by-step logic workflow "
        "tracing how the code actually processes input, based on the provided source code.\n\n"
        "{format_instructions}"
    )
    
    chain = prompt | llm | parser
    
    try:
        response = chain.invoke({
            "query": user_query,
            "name": repo_metadata.get('full_name'),
            "desc": repo_metadata.get('description'),
            "stars": repo_metadata.get('stars'),
            "reqs": repo_metadata.get('requirements'),
            "code": core_code,
            "format_instructions": parser.get_format_instructions()
        })
        return response
    except Exception as e:
        st.write(f"Error analyzing {repo_metadata.get('full_name')}: {e}")
        return None


def compare_top_projects(analyses: list) -> str:
    """
    Compare and generate comparison table for multiple repository analyses.
    
    Args:
        analyses: List of RepoAnalysis objects
        
    Returns:
        Markdown-formatted comparison table
    """
    llm = get_llm_client(temperature=0)
    st.write(f"Comparing {len(analyses)} projects")
    
    # Context building
    detailed_context = ""
    for idx, a in enumerate(analyses):
        detailed_context += f"""
        PROJECT {idx+1}: {a.name}
        SUMMARY: {a.summary}
        KEY LEARNINGS: {', '.join(a.key_learnings)}
        COMPLEXITY: {a.complexity_level}
        TECH STACK: {', '.join(a.tech_stack)}
        -----------------------
        """
    
    compare_prompt = f"""
    You are a Technical Mentor. Compare these projects specifically to help user determine which project is the best fit for their needs.
    
    Data:
    {detailed_context}

    STRICT FORMATTING RULES:
    1. Output a Markdown table.
    2. DO NOT use HTML tags like <br> or <div> inside the table.
    3. For multiple items in a cell, use a comma-separated list or plain text.
    
    Table Columns:
    | Project | Complexity | You Will Learn How To | Best If You Want To |
    """
    
    try:
        response = llm.invoke(compare_prompt)
        return response.content
    except Exception as e:
        st.write(f"Error during comparison: {e}")
        return "Comparison failed due to an error."

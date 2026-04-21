"""GitHub API client utilities."""
import base64
import os
from typing import List, Dict, Any
from github import Github
import streamlit as st


def search_github(query: str, fetch_limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search GitHub repositories by query.
    
    Args:
        query: GitHub search query string
        fetch_limit: Maximum number of repositories to fetch
        
    Returns:
        List of repository data dictionaries
    """
    g = Github(os.getenv("GITHUB_TOKEN"))
    repos = g.search_repositories(query=query, sort="stars", order="desc")
    
    results = []
    # Using a simple counter to respect the fetch_limit
    for i, repo in enumerate(repos):
        if i >= fetch_limit:
            break

        # --- HEURISTIC FILTERING ---
        low_quality_terms = ["awesome-", "-list", "curated", "collection"]
        if any(term in repo.full_name.lower() for term in low_quality_terms):
            continue

        if repo.size < 100:
            continue
    
        if repo.fork:
            continue
        
        results.append({
            "full_name": repo.full_name,
            "description": repo.description or "",
            "readme": get_readme(repo.full_name) or "",
            "topics": repo.get_topics(),
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "language": repo.language,
            "last_commit": repo.pushed_at.strftime("%Y-%m-%d")
        })

    st.write("Query: ", query)
    for r in results:
        st.write("- ", r['full_name'])
    return results


def get_readme(repo_full_name: str) -> str:
    """
    Retrieve README content from a repository.
    
    Args:
        repo_full_name: Repository full name (owner/repo)
        
    Returns:
        README content (first 1500 chars) or "Not found"
    """
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    
    try:
        readme = repo.get_readme()
        decoded_readme = base64.b64decode(readme.content).decode('utf-8')
        return decoded_readme[:1500]  # First 1500 chars
    except Exception:
        return "Not found"


def get_requirements(repo_full_name: str) -> str:
    """
    Retrieve requirements.txt content if available.
    
    Args:
        repo_full_name: Repository full name (owner/repo)
        
    Returns:
        Requirements content or "Not found"
    """
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    
    try:
        reqs = repo.get_contents("requirements.txt")
        decoded_reqs = base64.b64decode(reqs.content).decode('utf-8')
        return decoded_reqs
    except Exception:
        return "Not found"


def get_file_structure(repo_full_name: str) -> str:
    """
    Retrieve file tree structure from a repository.
    
    Args:
        repo_full_name: Repository full name (owner/repo)
        
    Returns:
        File list (newline-separated, max 300 files)
    """
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    try:
        # Recursive tree avoids multiple API calls for subfolders
        tree = repo.get_git_tree(repo.default_branch, recursive=True).tree
        file_list = [f.path for f in tree if f.type == "blob"]
        
        # Filter noise to save LLM context/tokens
        noise = ['.git', '.github', 'node_modules', 'venv', 'images', 'assets', '.png', '.jpg', '.pdf']
        filtered = [f for f in file_list if not any(x in f.lower() for x in noise)]
        
        return "\n".join(filtered[:300])  # Limit to 300 files to avoid token overflow
    except Exception as e:
        return f"Error mapping tree: {e}"

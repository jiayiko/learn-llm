"""Graph nodes for Scout Agent workflow."""
import streamlit as st
from sentence_transformers import SentenceTransformer

from src.models import AgentState, SearchStrategy
from src.agents.query_strategist import query_expansion_strategist
from src.api import search_github
from src.utils import rank_weighted_semantic, analyze_single_repo, compare_top_projects
from src.utils.analysis import extract_core_logic_agentic


def strategist_node(state: AgentState) -> dict:
    """
    Strategist node: Expand user query into search strategies.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with search strategy
    """
    with st.spinner("Strategist is planning the search..."):
        strategy = query_expansion_strategist(state["user_query"])

        # Logging
        st.write("**Generated Search Queries:**")
        for i, query in enumerate(strategy.queries, start=1):
            st.write(f"{i}. {query}")
        st.write(f"**Keywords:** {', '.join(strategy.keywords)}")
        st.write(f"**Expanded Terms:** {', '.join(strategy.expanded_terms)}")
        st.write(f"**Strategy Reasoning:** {strategy.reasoning}")

    return {"search_strategy": strategy}


def retriever_node(state: AgentState) -> dict:
    """
    Retriever node: Search GitHub and rank results.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with ranked repositories
    """
    all_raw_data = []
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    strategy = state.get("search_strategy")

    # --- Safety check ---
    if strategy is None:
        return {"raw_repos": []}
    
    # 1. Broad Retrieval from GitHub API
    for q in strategy.queries:
        all_raw_data.extend(search_github(q, fetch_limit=10))
    
    # 2. Deduplicate
    unique_repos = list({r['full_name']: r for r in all_raw_data}.values())

    # 3. Multi-Vector Re-Ranking
    ranked_repos = rank_weighted_semantic(
        repos=unique_repos,
        keywords=strategy.keywords or [],
        expansions=strategy.expanded_terms or [],
        embedder=embedder,
        w1=0.7,  # Priority on user's specific keywords
        w2=0.3   # Additional for technical depth/synonyms
    )
    filtered_ranked_repos = [repo for repo in ranked_repos if repo['semantic_score'] > 0.5]
    
    # Take top 3 for the Architect Node to analyze
    return {"raw_repos": filtered_ranked_repos[:3]}


def architect_node(state: AgentState) -> dict:
    """
    Architect node: Deep code extraction and analysis.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with analyzed results
    """
    results = []
    try:
        for repo_item in state["raw_repos"]:
            # Deep code extraction
            st.write("Analyzing repo ", repo_item['full_name'])
            core_code, reasoning = extract_core_logic_agentic(
                repo_item['full_name'], 
                state["user_query"]
            )
            # Final individual analysis
            analysis = analyze_single_repo(repo_item, core_code, state["user_query"])
            if analysis:
                results.append(analysis)
                st.write(f"Analysis complete for {repo_item['full_name']}")

    except Exception as e:
        st.write(f"General error in architect node: {e}")

    return {"analyzed_results": results}


def mentor_node(state: AgentState) -> dict:
    """
    Mentor node: Compare and summarize findings.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with comparison table
    """
    table = compare_top_projects(state["analyzed_results"])
    return {"comparison_table": table}

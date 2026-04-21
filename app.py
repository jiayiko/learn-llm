# Second iteration (prototype simple solution)

import base64
import os
import time
from typing import List
from github import Github
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import streamlit as st
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
import operator
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()

model_name = "gemini-2.5-flash-lite"

@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

# --- 1. PROXY ML SYSTEM: Structured Data Schema ---
class RepoAnalysis(BaseModel):
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
    selected_files: List[str] = Field(description="List of 3-5 specific file paths to read for core logic.")
    reasoning: str = Field(description="Short explanation of why these files look like the entry points.")

class AgentState(TypedDict):
    user_query: str
    search_strategy: SearchStrategy
    raw_repos: List[dict]
    analyzed_results: Annotated[List[RepoAnalysis], operator.add] # Appends results
    error_count: int
    comparison_table: str

def create_scout_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("mentor", mentor_node)

    # Define Edges
    workflow.set_entry_point("strategist")
    workflow.add_edge("strategist", "retriever")

    # Conditional Logic: Should we continue?
    def should_analyze(state: AgentState):
        if not state["raw_repos"]:
            return "end"
        return "continue"

    workflow.add_conditional_edges(
        "retriever",
        should_analyze,
        {
            "continue": "architect",
            "end": END
        }
    )

    workflow.add_edge("architect", "mentor")
    workflow.add_edge("mentor", END)

    return workflow.compile()

# --- New Node: Strategist ---
def strategist_node(state: AgentState):
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

def retriever_node(state: AgentState):
    all_raw_data = []
    embedder = load_embedder() # Assumes cached SentenceTransformer('all-MiniLM-L6-v2')

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
        w1=0.7, # Priority on user's specific keywords
        w2=0.3  # Additional for technical depth/synonyms
    )
    filtered_ranked_repos = [repo for repo in ranked_repos if repo['semantic_score'] > 0.5]
    
    # Take top 3 for the Architect Node to analyze
    return {"raw_repos": filtered_ranked_repos[:3]}

def architect_node(state: AgentState):
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

def mentor_node(state: AgentState):
    table = compare_top_projects(state["analyzed_results"])
    return {"comparison_table": table}

def safe_invoke(chain, payload, retries=5):
    for i in range(retries):
        try:
            return chain.invoke(payload)
        except Exception as e:
            if "429" in str(e) or "503" in str(e):
                wait = 2 ** i
                st.write(f"Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise e
            
# --- TOOL: File Tree Mapper ---
def get_file_structure(repo_full_name: str):
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    try:
        # Recursive tree avoids multiple API calls for subfolders
        tree = repo.get_git_tree(repo.default_branch, recursive=True).tree
        file_list = [f.path for f in tree if f.type == "blob"]
        
        # Filter noise to save LLM context/tokens
        noise = ['.git', '.github', 'node_modules', 'venv', 'images', 'assets', '.png', '.jpg', '.pdf']
        filtered = [f for f in file_list if not any(x in f.lower() for x in noise)]
        
        return "\n".join(filtered[:300]) # Limit to 300 files to avoid token overflow
    except Exception as e:
        return f"Error mapping tree: {e}"
    
def extract_core_logic_agentic(repo_full_name: str, user_intent: str):
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
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
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    combined_code = ""

    st.write("Selected files for core logic extraction:", selection.selected_files)
    
    for path in selection.selected_files:
        try:
            content = repo.get_contents(path)
            combined_code += f"\n--- FILE: {path} ---\n{base64.b64decode(content.content).decode('utf-8')[:2000]}"
        except:
            continue
            
    return combined_code, selection.reasoning

def query_expansion_strategist(user_intent: str):
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)
    parser = PydanticOutputParser(pydantic_object=SearchStrategy)

    prompt_content = """
    You are a Technical Search Architect. Your goal is to map a user's research intent into 
    highly accurate GitHub search queries by expanding technical semantics.

    ---
    
    ## OUTPUT COMPONENTS
    ### 1. Keywords (STRICT INTENT ANCHOR)
    - **Scope**: Extract 4-8 core keywords EXPLICITLY mentioned in the user's input that are essential to the topic.
    - **Rule**: DO NOT introduce new concepts or inferred terms here.
    - **Purpose**: ensure strict alignment with user intent
    Examples: "rag chatbot with memory" → ["rag", "chatbot", "memory"]

    ### 2. Expanded Terms (SEMANTIC EXPANSION)
    - **Scope**: Generate 5-10 inferred technical synonyms, acronyms, underlying algorithms, frameworks, or field-specific terminology.
    - **Purpose**: These ensure we find repos that use different but standard naming conventions.
    Examples: "Pathfinding" -> "A*", "Dijkstra", "Search Algorithm"

    ### 3. Queries (SEARCH STRATEGY)
    Generate distinct 3 GitHub search queries:
    - Query 1: **Acronym & Short-hand Focus** (High precision for community-standard terms).
    - Query 2: **Formal Name & Documentation Focus** (Targeting full terminology in target documentation (`in:readme`, `in:description`)).
    - Query 3: **Academic/Problem-Space Focus** (Targeting the underlying methods, architectures, or problem framing).
    - **STRICTLY NO** filters for stars, dates, or maintenance. Focus purely on technical content match.

    ---

    ### EXAMPLES
    User Input: "Self-driving car lane detection using computer vision"
    Query 1: "lane detection CV autonomous"
    Query 2: "'hough transform' lane-marking in:readme"
    Query 3: "perception-pipeline 'semantic segmentation' automotive"
    Keywords: ["lane detection", "self-driving car", "computer vision"]
    Expanded Terms: ["hough transform", "semantic segmentation", "edge detection", "perception pipeline"]

    User Input: "Low latency key-value store in Rust"
    Query 1: "kv-store rust latency"
    Query 2: "'key value store' storage engine in:description"
    Query 3: "LSM-tree storage-engine 'zero-copy' language:rust"
    Keywords: ["low latency", "key-value store", "rust"]
    Expanded Terms: ["kv-store", "distributed hash table", "lsm-tree", "storage engine", "zero-copy"]

    User Input: "{intent}"

    {format_instructions}
    """
    prompt = ChatPromptTemplate.from_template(prompt_content)

    chain = prompt | llm | parser
    
    strategy = chain.invoke({
        "intent": user_intent,
        "format_instructions": parser.get_format_instructions()
    })
    
    return strategy

# --- 2. TOOL: Deep File Inspector ---
def get_requirements(repo_full_name: str):
    """Retrieves requirements.txt content if available."""
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    
    try:
        reqs = repo.get_contents("requirements.txt")
        decoded_reqs = base64.b64decode(reqs.content).decode('utf-8')
        return decoded_reqs
    except:
        return "Not found"
    
def get_readme(repo_full_name: str):
    """Retrieves actual file content in repository."""
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_full_name)
    
    # Try to read README for workflow
    try:
        readme = repo.get_readme()
        decoded_readme = base64.b64decode(readme.content).decode('utf-8')
        return decoded_readme[:1500] # First 1500 chars
    except:
        return "Not found"

def search_github(query: str, fetch_limit: int = 10):
    g = Github(os.getenv("GITHUB_TOKEN"))
    repos = g.search_repositories(query=query, sort="stars", order="desc")
    
    results = []
    # Using a simple counter to respect the fetch_limit
    for i, repo in enumerate(repos):
        if i >= fetch_limit: break

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

def rank_weighted_semantic(repos, keywords, expansions, embedder, w1=0.7, w2=0.3):
    """
    Computes two separate scores and merges them using a weighted sum.
    w1: Weight for User Keywords (The Anchor)
    w2: Weight for Expanded Terms (The Context)
    """
    if not repos:
        return []

    # 1. Prepare Target Strings
    keyword_target = " ".join(keywords)
    expansion_target = " ".join(expansions)

    # 2. Prepare Corpus (Metadata + README snippet)
    corpus = [
        f"{r['full_name'].split('/')[1]} {r['description']} {' '.join(r['topics'])} {r['readme'][:1500]}"
        for r in repos
    ]

    # 3. Generate Embeddings
    kw_emb = embedder.encode(keyword_target, convert_to_tensor=True)
    ex_emb = embedder.encode(expansion_target, convert_to_tensor=True)
    corpus_embs = embedder.encode(corpus, convert_to_tensor=True)

    # 4. Compute Separate Cosine Similarities
    # util.cos_sim returns a matrix; we take the first row and convert to list
    kw_scores = util.cos_sim(kw_emb, corpus_embs)[0].tolist()
    ex_scores = util.cos_sim(ex_emb, corpus_embs)[0].tolist()

    # 5. Calculate Weighted Sum and Log Metrics
    for i, repo in enumerate(repos):
        s_kw = float(kw_scores[i])
        s_ex = float(ex_scores[i])
        
        # The Final Weighted Score
        repo["semantic_score"] = round((s_kw * w1) + (s_ex * w2), 4)
        
        # Individual scores for logging/debugging
        repo["kw_match"] = round(s_kw, 4)
        repo["ex_match"] = round(s_ex, 4)
        
        st.write(f"[{repo['full_name']}] Total: {repo['semantic_score']} (KW: {s_kw} | EX: {s_ex})")

    # 6. Sort by the combined weighted score
    return sorted(repos, key=lambda x: x["semantic_score"], reverse=True)

# --- 3. AGENT: Multi-Stage Analysis ---
def analyze_repos(repo_list: list, user_query: str):
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
    parser = PydanticOutputParser(pydantic_object=RepoAnalysis)
    
    prompt = ChatPromptTemplate.from_template(
        "You are a Technical Lead. The user want to deep search projects: '{query}'\n. Analyze the following Github repository data and provide a structured analysis to help the user.\n"
        "Repository data provided: {data}\n"
        "Format instructions: {format_instructions}"
    )
    
    analyses = []
    for repo in repo_list:
        st.write(f"🔍 Inspecting code for {repo['full_name']}...")
        chain = prompt | llm | parser
        
        try:
            response = chain.invoke({
                "query": user_query,
                "data": str(repo),
                "format_instructions": parser.get_format_instructions()
            })
            analyses.append(response)
        except Exception as e:
            st.error(f"Failed to parse {repo['full_name']}: {e}")
        
        time.sleep(5) # Stay under 15 RPM
    return analyses

def analyze_single_repo(repo_metadata: dict, core_code: str, user_query: str):
    """
    Acts as the 'Technical Lead' to synthesize metadata and source code 
    into a structured RepoAnalysis object.
    """
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
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
        # If the LLM fails to parse, we return None so the graph can continue to the next repo
        st.write(f"Error analyzing {repo_metadata.get('full_name')}: {e}")
        return None
    
# --- 4. NEW: COMPARISON LOGIC ---
def compare_top_projects(analyses: List[RepoAnalysis]):
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
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
    You are a Technical Mentor. Compare these 3 projects specifically to help user determine which project is the best fit for their needs.
    
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

# --- 4. UI: Streamlit Interface ---
st.set_page_config(page_title="GitHub Project Scout", page_icon="🚀")
st.title("🔍 GitHub Project Finder Agent")

user_input = st.text_input("What kind of project are you looking for?", 
                         placeholder="e.g., GNN for protein classification")

if st.button("Search & Analyze"):
    if not os.getenv("GITHUB_TOKEN"):
        st.error("Please set your GITHUB_TOKEN in the .env file.")
    elif not os.getenv("GOOGLE_API_KEY"):
        st.error("Please set your GOOGLE_API_KEY in the .env file.")
    else:
        # Initialize Graph
        scout_app = create_scout_graph()
        
        initial_state = {
            "user_query": user_input,
            "search_strategy": None,
            "raw_repos": [],
            "analyzed_results": [],
            "comparison_table": ""
        }

        with st.spinner("🚀 Agentic Graph in progress..."):
            # Run the entire graph
            final_state = scout_app.invoke(initial_state)
                
        if final_state.get("comparison_table"):
            st.header("✨ Comparison of Top Projects")
            st.markdown(final_state["comparison_table"])

        if final_state.get("analyzed_results"):
            # Step 4: Individual Expanders
            st.header("📂 Detailed Results")
            for res in final_state["analyzed_results"]:
                with st.expander(f"📁 {res.name} ({res.stars} ⭐)"):
                    st.write(f"**Summary:** {res.summary}")
                    st.write(f"**Workflow:** {res.core_workflow}")
                    st.write(f"**Techstack:** `{', '.join(res.tech_stack)}`")
                    st.write(f"**Key learnings:** {', '.join(res.key_learnings)}")
                    st.write(f"**Activity status:** {res.activity_status}")
        else:
            st.warning("No relevant projects found.")
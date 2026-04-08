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

load_dotenv()

# --- 1. PROXY ML SYSTEM: Structured Data Schema ---
class RepoAnalysis(BaseModel):
    name: str = Field(description="Full name of the repository")
    summary: str = Field(description="A brief technical overview")
    tech_stack: List[str] = Field(description="Specific libraries found in requirements.txt or README")
    key_learnings: List[str] = Field(description="3-4 specific concepts or patterns a user will learn from this code (e.g., 'How to implement Custom Loss Functions', 'Efficient Data Batching')")
    complexity_level: str = Field(description="Beginner, Intermediate, or Advanced based on code structure")
    activity_status: str = Field(description="Maintenance status based on commit dates")
    stars: int = Field(description="Number of stars")

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

def search_github(query: str, limit: int = 3):
    g = Github(os.getenv("GITHUB_TOKEN"))
    repos = g.search_repositories(query=query, sort="stars", order="desc")
    
    results = []
    for repo in repos[:limit]:
        readme = get_readme(repo.full_name)
        requirements = get_requirements(repo.full_name)

        results.append({
            "full_name": repo.full_name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "last_commit": repo.pushed_at.strftime("%Y-%m-%d"),
            "readme": readme,
            "requirements": requirements
        })
    return results

# --- 3. AGENT: Multi-Stage Analysis ---
def analyze_repos(repo_list: list, user_query: str):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
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

# --- 4. NEW: COMPARISON LOGIC ---
def compare_top_projects(analyses: List[RepoAnalysis]):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    
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
    
    Output a Markdown table:
    | Project | Complexity | You Will Learn How To... | Best If You Want To... |
    """
    
    response = llm.invoke(compare_prompt)
    return response.content

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
        with st.spinner("Agent is scouting GitHub..."):
            # Step 1: Search & Deep Fetch
            raw_data = search_github(user_input)
            
            if raw_data:
                # Step 2: Individual Analysis
                results = analyze_repos(raw_data, user_input)
                
                # Step 3: Synthesis Table
                st.header("✨Comparison of Top Projects")
                table = compare_top_projects(results)
                st.markdown(table)
                
                # Step 4: Individual Expanders
                st.header("📂 Detailed Results")
                for res in results:
                    with st.expander(f"📁 {res.name} ({res.stars} ⭐)"):
                        st.write(f"**Summary:** {res.summary}")
                        st.write(f"**Techstack:** `{', '.join(res.tech_stack)}`")
                        st.write(f"**Key learnings:** `{', '.join(res.key_learnings)}`")
                        st.write(f"**Activity status:** {res.activity_status}")
            else:
                st.warning("No relevant projects found.")
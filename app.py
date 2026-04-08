# First iteration (prototype simple solution)

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
    summary: str = Field(description="A 2-sentence summary of what the project does")
    tech_stack: List[str] = Field(description="List of main libraries and languages used")
    activity_status: str = Field(description="Summary of recent activity (e.g., Active, Stale, Archived)")
    stars: int = Field(description="Number of stars")

# --- 2. TOOL: GitHub Search Logic ---
def search_github(query: str, limit: int = 3):
    g = Github(os.getenv("GITHUB_TOKEN"))
    # The agentic part: we search based on the user's natural language
    repos = g.search_repositories(query=query, sort="stars", order="desc")
    
    results = []
    for repo in repos[:limit]:
        # Basic metadata extraction
        results.append({
            "full_name": repo.full_name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "last_commit": repo.pushed_at.strftime("%Y-%m-%d"),
            "url": repo.html_url
        })
    return results

# --- 3. AGENT: Analysis Logic ---
def analyze_repos(repo_list: list, user_query: str):
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    parser = PydanticOutputParser(pydantic_object=RepoAnalysis)
    
    prompt = ChatPromptTemplate.from_template(
        "Analyze the following GitHub repositories found for the query: '{query}'\n"
        "Data: {data}\n"
        "{format_instructions}"
    )
    
    analyses = []
    for repo in repo_list:
        chain = prompt | llm | parser
        response = chain.invoke({
            "query": user_query,
            "data": str(repo),
            "format_instructions": parser.get_format_instructions()
        })
        analyses.append(response)
        st.write(f"Analyzed: {repo['full_name']}")

        time.sleep(5)
    return analyses

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
            # Step 1: Retrieval
            raw_data = search_github(user_input)
            
            # Step 2: Analysis
            if raw_data:
                results = analyze_repos(raw_data, user_input)
                
                # Step 3: Display
                for res in results:
                    with st.expander(f"📁 {res.name} ({res.stars} ⭐)"):
                        st.write(f"**Summary:** {res.summary}")
                        st.write(f"**Tech Stack:** {', '.join(res.tech_stack)}")
                        st.write(f"**Status:** {res.activity_status}")
            else:
                st.warning("No projects found for that query.")
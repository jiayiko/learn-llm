"""Streamlit UI for Scout Agent."""
import os
import streamlit as st
from dotenv import load_dotenv

from src import create_scout_graph

load_dotenv()

# --- UI Configuration ---
st.set_page_config(
    page_title="GitHub Project Scout",
    page_icon="🚀",
    layout="wide"
)

st.title("🔍 GitHub Project Scout Agent")
st.markdown(
    """
    Intelligent agent for discovering and analyzing GitHub projects aligned with your learning goals.
    """
)

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    st.info("Ensure `GITHUB_TOKEN` and `GOOGLE_API_KEY` are set in `.env` file")

# --- Main UI ---
user_input = st.text_input(
    "What kind of project are you looking for?",
    placeholder="e.g., GNN for protein classification, RAG with memory, low-latency KV store",
    label_visibility="visible"
)

col1, col2 = st.columns(2)
with col1:
    search_button = st.button("🔍 Search & Analyze", type="primary")
with col2:
    reset_button = st.button("🔄 Clear Results")

if reset_button:
    st.rerun()

if search_button:
    if not os.getenv("GITHUB_TOKEN"):
        st.error("❌ Please set `GITHUB_TOKEN` in your `.env` file")
    elif not os.getenv("GOOGLE_API_KEY"):
        st.error("❌ Please set `GOOGLE_API_KEY` in your `.env` file")
    elif not user_input.strip():
        st.warning("⚠️ Please enter a search query")
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

        with st.spinner("🚀 Scout Agent analyzing projects..."):
            try:
                # Run the entire graph
                final_state = scout_app.invoke(initial_state)
                    
                if final_state.get("comparison_table"):
                    st.header("✨ Comparison of Top Projects")
                    st.markdown(final_state["comparison_table"])

                if final_state.get("analyzed_results"):
                    # Individual Expanders
                    st.header("📂 Detailed Results")
                    for res in final_state["analyzed_results"]:
                        with st.expander(f"📁 {res.name} ({res.stars} ⭐)"):
                            st.write(f"**Summary:** {res.summary}")
                            st.write(f"**Workflow:** {res.core_workflow}")
                            st.write(f"**Techstack:** `{', '.join(res.tech_stack)}`")
                            st.write(f"**Key learnings:** {', '.join(res.key_learnings)}")
                            st.write(f"**Activity status:** {res.activity_status}")
                            st.write(f"**Complexity:** {res.complexity_level}")
                else:
                    st.warning("⚠️ No relevant projects found matching your query.")
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")

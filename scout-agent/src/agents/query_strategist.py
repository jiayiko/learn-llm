"""Query expansion strategist node."""
import time
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import streamlit as st

from src.models import SearchStrategy
from src.llm import get_llm_client


def query_expansion_strategist(user_intent: str) -> SearchStrategy:
    """
    Expand user query into multiple search strategies.
    
    Args:
        user_intent: User's search intent/query
        
    Returns:
        SearchStrategy with queries, keywords, and expanded terms
    """
    llm = get_llm_client(temperature=0.2)
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

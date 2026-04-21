"""Semantic ranking utilities for repository scoring."""
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
import streamlit as st


def rank_weighted_semantic(
    repos: List[Dict[str, Any]],
    keywords: List[str],
    expansions: List[str],
    embedder: SentenceTransformer,
    w1: float = 0.7,
    w2: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Compute weighted semantic scores for repositories.
    
    Computes two separate scores and merges them using a weighted sum:
    - w1: Weight for User Keywords (The Anchor)
    - w2: Weight for Expanded Terms (The Context)
    
    Args:
        repos: List of repository dictionaries
        keywords: Core keywords from user query
        expansions: Expanded technical terms
        embedder: SentenceTransformer embedder instance
        w1: Weight for keywords matching
        w2: Weight for expansion matching
        
    Returns:
        List of repositories sorted by weighted semantic score
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

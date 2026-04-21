# Architecture Overview

## System Design

Scout Agent is built on a **multi-agent workflow architecture** using LangGraph. The system orchestrates four specialized agents that work together to discover and analyze GitHub projects.

## Workflow

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ STRATEGIST: Query Expansion             │
│ - Extract core keywords                 │
│ - Generate semantic expansions          │
│ - Create 3 search strategies            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ RETRIEVER: GitHub Search & Ranking      │
│ - Execute searches with all queries     │
│ - Deduplicate results                   │
│ - Semantic ranking with embeddings      │
│ - Filter by relevance threshold         │
└────────┬────────────────────────────────┘
         │
         ▼
    ┌────────────────────────┐
    │ Results Found?         │
    └────────┬───────────────┘
             │
        No   │   Yes
        │    │
        │    ▼
        │ ┌──────────────────────────┐
        │ │ ARCHITECT: Code Analysis │
        │ │ - Extract file structure │
        │ │ - Identify core files    │
        │ │ - Analyze workflows      │
        │ │ - Generate analysis      │
        │ └────────┬─────────────────┘
        │          │
        │          ▼
        │  ┌──────────────────────┐
        │  │ MENTOR: Comparison   │
        │  │ - Create comparison  │
        │  │ - Generate summary   │
        │  └────────┬─────────────┘
        │           │
        └───────────┼─────────────┐
                    │             │
                    ▼             ▼
            ┌──────────────┐  ┌──────────┐
            │ Comparison   │  │ Empty    │
            │ Table        │  │ Results  │
            └──────────────┘  └──────────┘
```

## Agent Responsibilities

### 1. Strategist Agent
**Purpose**: Convert unstructured user intent into structured search strategies

**Inputs**:
- User's natural language query

**Process**:
1. Extract core keywords (strict intent anchor)
2. Generate expanded terms (semantic synonyms, acronyms, related algorithms)
3. Create 3 distinct GitHub search queries:
   - Query 1: Acronym & short-hand focus
   - Query 2: Formal name & documentation focus
   - Query 3: Academic/problem-space focus

**Outputs**:
- `SearchStrategy` with queries, keywords, and expanded terms

**Key Files**:
- `src/agents/query_strategist.py`: `query_expansion_strategist()`
- `src/agents/nodes.py`: `strategist_node()`

### 2. Retriever Agent
**Purpose**: Find relevant repositories using semantic ranking

**Inputs**:
- Search strategy with queries

**Process**:
1. Execute each search query against GitHub API
2. Collect all results (with heuristic filtering)
3. Deduplicate repositories
4. Generate embeddings for:
   - User keywords
   - Expanded technical terms
   - Repository metadata (name, description, topics, README snippet)
5. Compute weighted semantic scores:
   ```
   score = (keyword_similarity × w1) + (expansion_similarity × w2)
   ```
6. Sort by score and filter by threshold
7. Return top N repositories

**Outputs**:
- List of ranked repositories with semantic scores

**Key Files**:
- `src/utils/ranking.py`: `rank_weighted_semantic()`
- `src/agents/nodes.py`: `retriever_node()`

### 3. Architect Agent
**Purpose**: Deep-dive code analysis and structure extraction

**Inputs**:
- Repository metadata
- User query context

**Process**:
1. Map repository file structure (with filtering)
2. Use LLM to identify 3-5 core logic files
3. Extract content from selected files
4. Synthesize metadata + code into structured analysis
5. Generate:
   - Technical summary
   - Core workflow description
   - Key learning outcomes
   - Complexity assessment
   - Maintenance status

**Outputs**:
- `RepoAnalysis` with structured insights

**Key Files**:
- `src/utils/analysis.py`: `extract_core_logic_agentic()`, `analyze_single_repo()`
- `src/agents/nodes.py`: `architect_node()`

### 4. Mentor Agent
**Purpose**: Compare findings and generate recommendations

**Inputs**:
- List of repository analyses

**Process**:
1. Format all analysis data
2. Generate comparison table highlighting:
   - Project complexity levels
   - Learning outcomes
   - Technology stacks
   - Best use cases

**Outputs**:
- Markdown formatted comparison table

**Key Files**:
- `src/utils/analysis.py`: `compare_top_projects()`
- `src/agents/nodes.py`: `mentor_node()`

## Data Flow

### State Object (AgentState)
```python
{
    "user_query": str,                    # User's original query
    "search_strategy": SearchStrategy,    # Expanded search strategies
    "raw_repos": List[dict],              # Retrieved repositories
    "analyzed_results": List[RepoAnalysis], # Analyzed repositories
    "error_count": int,                   # Error tracking
    "comparison_table": str                # Final comparison output
}
```

### Key Data Models

**RepoAnalysis**: Comprehensive analysis of a single repository
```python
{
    "name": str,                    # Full repo name
    "summary": str,                 # Technical overview
    "language": str,                # Main programming language
    "tech_stack": List[str],        # Libraries and frameworks
    "core_workflow": str,           # End-to-end logic description
    "key_learnings": List[str],     # What users will learn (3-4 items)
    "complexity_level": str,        # Beginner/Intermediate/Advanced
    "activity_status": str,         # Maintenance status
    "stars": int,                   # GitHub stars count
    "forks": int                    # GitHub forks count
}
```

**SearchStrategy**: Query expansion output
```python
{
    "queries": List[str],           # 3 distinct search queries
    "keywords": List[str],          # Core keywords from user input
    "expanded_terms": List[str],    # Technical synonyms (5-10 items)
    "reasoning": str                # Strategy justification
}
```

## Configuration

Key parameters in `config/default_config.py`:

- **MODEL_NAME**: LLM model selection
- **SEMANTIC_SCORE_THRESHOLD**: Minimum relevance cutoff
- **KEYWORD_WEIGHT (w1)**: Importance of user keywords in ranking
- **EXPANSION_WEIGHT (w2)**: Importance of technical expansions in ranking
- **GITHUB_TOP_RESULTS**: Number of repos to analyze deeply

## External Dependencies

- **LangChain**: LLM chain orchestration
- **LangGraph**: Graph-based workflow management
- **PyGithub**: GitHub API client
- **Sentence Transformers**: Semantic embeddings
- **Google Gemini**: LLM for analysis and expansion
- **Streamlit**: Web UI framework

## Error Handling

Each agent includes error handling:
- **Strategist**: LLM parsing errors logged but non-blocking
- **Retriever**: GitHub API errors with retry logic (exponential backoff)
- **Architect**: File extraction errors gracefully skipped
- **Mentor**: Comparison errors return fallback message

## Performance Considerations

1. **Caching**: SentenceTransformer model cached in Streamlit
2. **Rate Limiting**: Delays between API calls to respect GitHub rate limits
3. **Token Optimization**: File trees and content truncated to manage LLM tokens
4. **Early Stopping**: Conditional edges to skip unnecessary processing

## Security

- API tokens stored in `.env` file (excluded from git)
- No sensitive data logged
- GitHub API calls validated
- Input validation on user queries

## Future Enhancements

- Local LLM model support
- Advanced caching strategies
- Parallel repository analysis
- Export formats (PDF, JSON, CSV)
- Custom ranking formulas
- Repository cloning and local analysis

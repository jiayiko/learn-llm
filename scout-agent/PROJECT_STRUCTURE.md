"""Scout Agent project structure reference.

Generated from refactoring of app.py into modular architecture.
"""

PROJECT_STRUCTURE = """
scout-agent/
├── src/                              # Main source code
│   ├── __init__.py                   # Package initialization
│   ├── agents/                       # Multi-agent workflow
│   │   ├── __init__.py               # Agent exports
│   │   ├── nodes.py                  # Agent node implementations
│   │   │   ├── strategist_node()     # Query expansion
│   │   │   ├── retriever_node()      # GitHub search & ranking
│   │   │   ├── architect_node()      # Code analysis
│   │   │   └── mentor_node()         # Comparison & summary
│   │   ├── graph.py                  # Graph orchestration
│   │   │   └── create_scout_graph()  # Graph construction
│   │   └── query_strategist.py       # Query expansion logic
│   │       └── query_expansion_strategist()
│   │
│   ├── api/                          # External API clients
│   │   ├── __init__.py               # API exports
│   │   └── github_client.py          # GitHub API utilities
│   │       ├── search_github()       # Repository search
│   │       ├── get_readme()          # Fetch README
│   │       ├── get_requirements()    # Fetch requirements.txt
│   │       └── get_file_structure()  # Map file tree
│   │
│   ├── llm/                          # LLM configuration
│   │   ├── __init__.py               # LLM exports
│   │   └── gemini_client.py          # Gemini initialization
│   │       └── get_llm_client()      # LLM factory
│   │
│   ├── models/                       # Data models
│   │   ├── __init__.py               # Model exports
│   │   └── schemas.py                # Pydantic models
│   │       ├── RepoAnalysis          # Repository analysis output
│   │       ├── SearchStrategy        # Query expansion output
│   │       ├── FileSelection         # Selected files for analysis
│   │       └── AgentState            # Agentic state
│   │
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py               # Utils exports
│   │   ├── ranking.py                # Semantic ranking
│   │   │   └── rank_weighted_semantic()
│   │   └── analysis.py               # Repository analysis
│   │       ├── extract_core_logic_agentic()
│   │       ├── analyze_single_repo()
│   │       └── compare_top_projects()
│   │
│   └── ui/                           # User interface
│       ├── __init__.py               # UI package
│       └── app.py                    # Streamlit application
│
├── config/                           # Configuration
│   ├── __init__.py                   # Config package
│   └── default_config.py             # Default settings
│
├── tests/                            # Unit and integration tests
│   ├── __init__.py                   # Test package
│   └── test_core.py                  # Core tests
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # System design & workflow
│   └── GETTING_STARTED.md            # Setup & usage guide
│
├── requirements.txt                  # Python dependencies
├── setup.py                          # Package setup script
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore patterns
├── README.md                         # Project overview
├── CHANGELOG.md                      # Version history
├── CONTRIBUTING.md                   # Contribution guidelines
├── LICENSE                           # MIT License
└── project_structure.txt             # This file

DEPENDENCY MAP:
==============

agents/
  ├── depends on: models/, utils/, api/, llm/
  ├── imports: SearchStrategy, AgentState, RepoAnalysis
  └── uses: GitHub API, LLM, ranking, analysis

utils/
  ├── ranking.py: depends on sentence_transformers
  └── analysis.py: depends on models/, api/, llm/

ui/
  ├── depends on: agents/, models/
  ├── imports: create_scout_graph, AgentState
  └── entry point: streamlit run src/ui/app.py

api/
  ├── depends on: PyGithub
  └── standalone module

llm/
  ├── depends on: langchain_google_genai
  └── factory for LLM clients

models/
  ├── depends on: pydantic
  └── standalone schemas

DATA FLOW:
==========

User Input
    ↓
UI (app.py)
    ├── calls: create_scout_graph()
    └── initializes: AgentState
         ↓
    Graph.invoke(state)
         ├─→ strategist_node()
         │    ├── uses: query_expansion_strategist()
         │    └── returns: SearchStrategy
         │
         ├─→ retriever_node()
         │    ├── uses: search_github()
         │    ├── uses: rank_weighted_semantic()
         │    └── returns: ranked repositories
         │
         ├─→ architect_node()
         │    ├── uses: extract_core_logic_agentic()
         │    ├── uses: analyze_single_repo()
         │    └── returns: RepoAnalysis[]
         │
         └─→ mentor_node()
              ├── uses: compare_top_projects()
              └── returns: comparison_table
                   ↓
                Results displayed in UI

FILE ORGANIZATION PRINCIPLES:
=============================

1. Separation of Concerns
   - Each module has single responsibility
   - Clear interfaces between modules
   - Minimal coupling

2. Logical Grouping
   - agents/: Workflow orchestration
   - api/: External integrations
   - models/: Data schemas
   - utils/: Reusable functions
   - ui/: User interface
   - config/: Configuration management

3. Easy Testing
   - Pure functions where possible
   - Dependency injection patterns
   - Mockable external services

4. Scalability
   - Easy to add new agents
   - Easy to swap LLM providers
   - Pluggable API clients
   - Extensible analysis features

5. Maintainability
   - Clear module boundaries
   - Comprehensive documentation
   - Type hints throughout
   - Consistent naming conventions

KEY FILES FOR EACH ROLE:
=======================

For Users:
  - README.md: Start here
  - docs/GETTING_STARTED.md: Setup guide
  - src/ui/app.py: Run this

For Developers:
  - docs/ARCHITECTURE.md: How it works
  - src/agents/graph.py: Main workflow
  - src/models/schemas.py: Data structures
  - tests/test_core.py: Testing examples

For Contributors:
  - CONTRIBUTING.md: Guidelines
  - setup.py: Development setup
  - requirements.txt: Dependencies

ORIGINAL APP.PY REFACTORING:
============================

Original monolithic structure:
├── Pydantic models (→ models/schemas.py)
├── Agent nodes (→ agents/nodes.py)
├── Graph creation (→ agents/graph.py)
├── GitHub tools (→ api/github_client.py)
├── LLM configuration (→ llm/gemini_client.py)
├── Ranking logic (→ utils/ranking.py)
├── Analysis logic (→ utils/analysis.py)
├── Streamlit UI (→ ui/app.py)
└── Configuration (→ config/default_config.py)

Benefits of refactoring:
✓ Modular and maintainable
✓ Testable components
✓ Clear responsibilities
✓ Reusable utilities
✓ Professional structure
✓ Ready for GitHub
✓ Easy to extend
✓ Better documentation
"""

if __name__ == "__main__":
    print(PROJECT_STRUCTURE)

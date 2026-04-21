# Scout Agent 🔍

Intelligent GitHub project discovery and analysis agent powered by LangChain, LangGraph, and Google Gemini.

## 🎯 Overview

Scout Agent helps developers discover, analyze, and understand GitHub projects aligned with their learning goals. It uses a multi-agent workflow to:

1. **Strategist**: Expand your search query into multiple semantic search strategies
2. **Retriever**: Search GitHub and rank projects by semantic relevance
3. **Architect**: Deep-dive into repository code and extract core logic
4. **Mentor**: Compare and summarize findings for easy decision-making

## ✨ Features

- **Intelligent Query Expansion**: Converts user intent into multiple search strategies
- **Semantic Ranking**: Uses embedding models to rank repositories by relevance
- **Code Analysis**: Extracts and analyzes core logic from repositories
- **Structured Analysis**: Generates detailed technical analysis of each project
- **Comparison Tables**: Creates side-by-side comparisons to help with decisions
- **Streamlit UI**: Beautiful web interface for easy interaction

## 📋 Prerequisites

- Python 3.9+
- GitHub API token ([Get one here](https://github.com/settings/tokens))
- Google API key for Gemini ([Get one here](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

### 1. Clone the Repository
\`\`\`bash
git clone https://github.com/yourusername/scout-agent.git
cd scout-agent
\`\`\`

### 2. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Set Up Environment Variables
\`\`\`bash
cp .env.example .env
# Edit .env and add your tokens
\`\`\`

### 4. Run the Application
\`\`\`bash
streamlit run src/ui/app.py
\`\`\`

## 📁 Project Structure

\`\`\`
scout-agent/
├── src/
│   ├── agents/          # Agent nodes and graph orchestration
│   │   ├── nodes.py     # Agent node implementations
│   │   ├── graph.py     # Graph creation and workflow
│   │   └── query_strategist.py
│   ├── api/             # External API clients
│   │   └── github_client.py
│   ├── llm/             # LLM configuration
│   │   └── gemini_client.py
│   ├── models/          # Pydantic schemas
│   │   └── schemas.py
│   ├── utils/           # Utility functions
│   │   ├── ranking.py   # Semantic ranking
│   │   └── analysis.py  # Repository analysis
│   └── ui/              # Streamlit interface
│       └── app.py
├── config/              # Configuration files
├── tests/               # Unit tests
├── docs/                # Documentation
├── requirements.txt     # Dependencies
├── setup.py             # Package setup
├── .env.example         # Environment template
└── .gitignore
\`\`\`

## 🔧 Configuration

Key settings can be found in \`config/default_config.py\`:

- **MODEL_NAME**: Gemini model to use (default: gemini-2.5-flash-lite)
- **SEMANTIC_SCORE_THRESHOLD**: Minimum relevance score (default: 0.5)
- **KEYWORD_WEIGHT**: Weight for user keywords (default: 0.7)
- **EXPANSION_WEIGHT**: Weight for expanded terms (default: 0.3)

## 💡 Usage Examples

### Example 1: Graph Neural Networks
\`\`\`
Search: "GNN for protein classification"
\`\`\`

### Example 2: RAG Systems
\`\`\`
Search: "RAG chatbot with memory and vector store"
\`\`\`

### Example 3: Performance-Critical Systems
\`\`\`
Search: "low latency key-value store in Rust"
\`\`\`

## 🏗️ Architecture

The agent uses a **LangGraph** workflow with four stages:

```
User Query → Strategist → Retriever → Architect → Mentor → Comparison
                ↓           ↓          ↓           ↓
            SearchStrategy  Repos    Analysis    Summary
```

### Agent Workflows

**Strategist**: Expands query intent into multiple search strategies
- Extracts core keywords from user input
- Generates technical synonyms and expanded terms
- Creates 3 distinct GitHub search queries

**Retriever**: Fetches and ranks repositories
- Searches GitHub API with multiple queries
- Deduplicates results
- Uses semantic embeddings to rank by relevance

**Architect**: Performs deep code analysis
- Maps repository file structure
- Selects core logic files using LLM
- Extracts and summarizes workflows
- Generates structured analysis

**Mentor**: Compares findings
- Creates comparison table
- Highlights key differences
- Provides recommendations

## 🧪 Testing

Run tests with:
\`\`\`bash
pytest tests/
\`\`\`

## 📚 API Documentation

### Main Classes

#### \`RepoAnalysis\`
Structured analysis output for a single repository:
- \`name\`: Repository name
- \`summary\`: Technical overview
- \`language\`: Programming language
- \`tech_stack\`: List of libraries/frameworks
- \`core_workflow\`: End-to-end logic summary
- \`key_learnings\`: Learning outcomes
- \`complexity_level\`: Beginner/Intermediate/Advanced
- \`activity_status\`: Maintenance status
- \`stars\`: GitHub stars
- \`forks\`: GitHub forks

#### \`SearchStrategy\`
Query expansion strategy:
- \`queries\`: List of 3 search queries
- \`keywords\`: Core keywords from user input
- \`expanded_terms\`: Technical synonyms
- \`reasoning\`: Strategy justification

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (\`git checkout -b feature/amazing-feature\`)
3. Commit changes (\`git commit -m 'Add amazing feature'\`)
4. Push to branch (\`git push origin feature/amazing-feature\`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Workflow management by [LangGraph](https://github.com/langchain-ai/langgraph)
- LLM powered by [Google Gemini](https://deepmind.google/technologies/gemini/)
- Embeddings by [Sentence Transformers](https://www.sbert.net/)
- GitHub integration via [PyGithub](https://pygithub.readthedocs.io/)

## ⚠️ Important Notes

- **Rate Limiting**: GitHub API has rate limits. Consider using a personal access token with higher limits
- **API Costs**: Using Google Gemini API may incur costs based on your usage plan
- **Rate Limiting**: The agent includes delays between requests to respect API rate limits

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation in \`docs/\`
- Review the architecture design in \`docs/architecture.md\`

## 🗺️ Roadmap

- [ ] Add caching for API responses
- [ ] Support for local LLM models
- [ ] Advanced filtering options
- [ ] Export analysis to various formats
- [ ] Integration with VS Code extension
- [ ] Multi-language support
- [ ] Performance optimization for large repositories

---

**Happy exploring! 🚀**

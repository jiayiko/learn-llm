# Quick Reference

## Directory Structure

```
scout-agent/
├── src/                    # Application source code
├── config/                 # Configuration files
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation
├── .github/                # GitHub configuration
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
├── README.md              # Project overview
└── .gitignore             # Git ignore patterns
```

## Running the Application

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 3. Run the app
streamlit run src/ui/app.py
```

## Project Organization

| Directory | Purpose |
|-----------|---------|
| `src/agents/` | Multi-agent workflow and orchestration |
| `src/api/` | External API clients (GitHub) |
| `src/llm/` | LLM configuration and clients |
| `src/models/` | Pydantic data models |
| `src/utils/` | Utility functions (ranking, analysis) |
| `src/ui/` | Streamlit user interface |
| `config/` | Application configuration |
| `tests/` | Unit and integration tests |
| `docs/` | Comprehensive documentation |
| `.github/` | GitHub Actions workflows |

## Key Files

| File | Purpose |
|------|---------|
| `src/ui/app.py` | Main Streamlit application |
| `src/agents/graph.py` | Graph workflow orchestration |
| `docs/ARCHITECTURE.md` | System design and workflows |
| `docs/GETTING_STARTED.md` | Setup and usage guide |
| `README.md` | Project overview |
| `.env.example` | Environment variable template |

## Common Commands

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Format code
black src/ tests/

# Check imports
isort src/ tests/

# Run linting
flake8 src/ tests/

# Run app
streamlit run src/ui/app.py
```

## Configuration

Main settings in `config/default_config.py`:
- `MODEL_NAME` - Gemini model to use
- `SEMANTIC_SCORE_THRESHOLD` - Minimum relevance score
- `KEYWORD_WEIGHT` - Weight for user keywords
- `EXPANSION_WEIGHT` - Weight for technical terms

## Dependencies

Key packages:
- `langchain` - LLM framework
- `langgraph` - Graph-based workflows
- `PyGithub` - GitHub API
- `sentence-transformers` - Semantic embeddings
- `streamlit` - Web UI
- `pydantic` - Data validation

## Pushing to GitHub

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: refactored scout-agent"

# Add remote
git remote add origin https://github.com/yourusername/scout-agent.git

# Push
git push -u origin main
```

## Getting Help

1. Read `docs/GETTING_STARTED.md` for setup
2. Check `docs/ARCHITECTURE.md` for how it works
3. Review `CONTRIBUTING.md` for development
4. See `README.md` for feature overview

## Agent Workflow

```
User Query
    ↓
Strategist (expand query)
    ↓
Retriever (search & rank)
    ↓
Architect (analyze code)
    ↓
Mentor (compare & summarize)
    ↓
Results
```

## Important Notes

- **Environment Variables**: Required `GITHUB_TOKEN` and `GOOGLE_API_KEY`
- **Rate Limiting**: GitHub API has rate limits; agent includes delays
- **First Run**: Embedding models download on first run (~500MB)
- **API Costs**: Google Gemini API may incur costs
- **Credentials**: Never commit `.env` file; use `.env.example` as template

## Next Steps

1. ✅ Project structure created
2. ✅ Code refactored and organized
3. ✅ Documentation complete
4. ⏭️ Create GitHub repository
5. ⏭️ Push code
6. ⏭️ Set up Actions
7. ⏭️ Tag first release

---

**Ready to push to GitHub!** 🚀

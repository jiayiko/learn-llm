# Getting Started Guide

## Installation

### 1. Prerequisites
- Python 3.9 or higher
- Git
- GitHub account with API token
- Google account with API access

### 2. Clone the Repository
\`\`\`bash
git clone https://github.com/yourusername/scout-agent.git
cd scout-agent
\`\`\`

### 3. Create Virtual Environment
\`\`\`bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
\`\`\`

### 4. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 5. Set Up API Keys

#### GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select scopes: \`public_repo\`, \`read:user\`
4. Copy the token

#### Google API Key
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy the key

### 6. Configure Environment
\`\`\`bash
cp .env.example .env
\`\`\`

Edit \`.env\`:
\`\`\`
GITHUB_TOKEN=your_github_token_here
GOOGLE_API_KEY=your_google_api_key_here
\`\`\`

## Running the Application

### Start the Streamlit App
\`\`\`bash
streamlit run src/ui/app.py
\`\`\`

The application will open at \`http://localhost:8501\`

## Usage Examples

### Example 1: Find Graph Neural Network Projects
Query: \`Graph Neural Networks for protein structure prediction\`

The agent will:
1. Expand to terms like: "GNN", "message passing", "graph convolution", "protein folding"
2. Search: "GNN protein", "'graph neural network' protein in:readme", "message-passing protein"
3. Rank results by relevance
4. Analyze top 3 projects
5. Compare findings

### Example 2: Find RAG Systems
Query: \`Retrieval Augmented Generation chatbot with memory\`

The agent will discover projects using:
- Acronyms: RAG, LLM
- Synonyms: semantic search, vector store, prompt engineering
- Frameworks: LangChain, LlamaIndex, CrewAI

### Example 3: Find Performance-Critical Databases
Query: \`Low latency in-memory database written in Rust\`

The agent will search for:
- Technologies: Rust, memory-mapped IO, B-trees
- Patterns: embedded databases, KV stores
- Concepts: zero-copy, lock-free algorithms

## Features Tour

### 1. Query Expansion
The strategist intelligently converts your natural language query into multiple search angles:
- **Exact keywords**: Strictly from your input
- **Technical synonyms**: Domain-specific terminology
- **Search strategies**: Formal, informal, and academic variations

### 2. Semantic Ranking
Results are ranked not just by stars, but by semantic relevance:
- Your keywords get priority (default 70% weight)
- Technical expansions provide context (default 30% weight)
- Uses modern embedding models for accuracy

### 3. Deep Code Analysis
Instead of just reading READMEs, the agent:
- Maps the repository structure
- Identifies core implementation files
- Analyzes workflows and patterns
- Extracts learning outcomes

### 4. Comparative Analysis
Get a side-by-side comparison table showing:
- Complexity levels
- Key learning topics
- Technology stacks
- Best use cases for each project

## Customization

### Adjust Ranking Weights
Edit `config/default_config.py`:
\`\`\`python
KEYWORD_WEIGHT = 0.7      # Increase for stricter matching
EXPANSION_WEIGHT = 0.3    # Increase for broader discovery
\`\`\`

### Change the LLM Model
\`\`\`python
MODEL_NAME = "gemini-pro"  # For more powerful analysis
MODEL_TEMPERATURE = 0.1    # Increase for more creative analysis
\`\`\`

### Adjust Search Depth
\`\`\`python
GITHUB_FETCH_LIMIT = 20    # Search more results per query
GITHUB_TOP_RESULTS = 5     # Analyze more projects
SEMANTIC_SCORE_THRESHOLD = 0.3  # Lower threshold = broader results
\`\`\`

## Troubleshooting

### Issue: "Please set GITHUB_TOKEN in .env"
**Solution**: Verify your `.env` file exists and contains:
\`\`\`
GITHUB_TOKEN=your_actual_token
\`\`\`

### Issue: "API Rate Limit Exceeded"
**Solution**: GitHub limits unauthenticated requests. Ensure:
1. Your token is correctly set
2. Wait a while before trying again
3. Use a personal access token for higher limits

### Issue: "No relevant projects found"
**Solutions**:
1. Try more specific queries
2. Lower the SEMANTIC_SCORE_THRESHOLD
3. Increase GITHUB_FETCH_LIMIT

### Issue: Slow Response Times
**Solutions**:
1. This is normal for first-time embeddings (model downloads)
2. Subsequent runs are faster (cached models)
3. Try reducing GITHUB_TOP_RESULTS

## Next Steps

1. **Explore Results**: Review detailed analyses in the expandable sections
2. **Visit Projects**: Click repository links to explore code on GitHub
3. **Compare**: Use the comparison table to decide which project to study
4. **Learn**: Start with beginner-level projects and work up
5. **Contribute**: Found improvements? Consider contributing back

## Additional Resources

- [LangChain Documentation](https://docs.langchain.com)
- [LangGraph Documentation](https://github.com/langchain-ai/langgraph)
- [PyGithub Documentation](https://pygithub.readthedocs.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Sentence Transformers](https://www.sbert.net/)

## Tips for Best Results

1. **Be Specific**: More specific queries yield better results
2. **Use Technical Terms**: Include domain-specific keywords
3. **Combine Concepts**: "algorithm + language + use case" works well
4. **Start Simple**: Begin with your main topic, refine if needed
5. **Review Multiple Results**: Compare several projects before deciding

## Performance Notes

- First run may be slow (downloads embedding models)
- Subsequent runs are much faster (caching)
- GitHub API calls respect rate limits (delays built-in)
- Large repositories may take time to analyze

## Getting Help

- Check the [Architecture Guide](ARCHITECTURE.md)
- Review [README.md](../README.md)
- Open an issue on GitHub with:
  - Your query
  - Error message (if any)
  - Python version
  - Operating system

Happy exploring! 🚀

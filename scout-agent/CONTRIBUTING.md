# Contributing to Scout Agent

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Welcome diverse perspectives
- Report issues responsibly

## Getting Started

### Fork and Clone
\`\`\`bash
git clone https://github.com/yourusername/scout-agent.git
cd scout-agent
\`\`\`

### Create a Branch
\`\`\`bash
git checkout -b feature/your-feature-name
\`\`\`

### Set Up Development Environment
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
pip install -e .  # Install in development mode
\`\`\`

## Development Workflow

### 1. Make Changes
- Write clear, concise code
- Follow Python PEP 8 style guide
- Add docstrings to functions and classes
- Include type hints where possible

### 2. Test Your Changes
\`\`\`bash
pytest tests/
\`\`\`

### 3. Commit with Clear Messages
\`\`\`bash
git commit -m "feat: add query caching for performance improvement"
\`\`\`

### 4. Push and Create Pull Request
\`\`\`bash
git push origin feature/your-feature-name
\`\`\`

## Commit Message Format

Use clear, descriptive commit messages:

- \`feat:\` A new feature
- \`fix:\` A bug fix
- \`docs:\` Documentation changes
- \`style:\` Code style changes (no logic change)
- \`refactor:\` Code restructuring
- \`test:\` Test additions or changes
- \`perf:\` Performance improvements

Example:
\`\`\`
feat: implement local model support for offline analysis

- Add support for ollama integration
- Add configuration option for local models
- Update documentation with setup instructions
\`\`\`

## Types of Contributions

### Bug Reports
Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Error messages/logs

### Feature Requests
Include:
- Clear description of the feature
- Use case and why it's useful
- Possible implementation approach
- Examples of similar features

### Documentation Improvements
- Fix typos and clarify explanations
- Add examples and use cases
- Improve code comments
- Add troubleshooting guides

### Code Contributions
- Follow the existing code style
- Add tests for new features
- Update documentation
- Keep commits focused and atomic

## Pull Request Process

1. Update documentation if needed
2. Add or update tests
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Provide clear PR description:
   - What changes are made
   - Why the changes are needed
   - How to test the changes

## Code Style

### Python Style
- Follow PEP 8
- Use type hints: \`def func(x: str) -> bool:\`
- Max line length: 88 characters
- Use meaningful variable names

### Documentation
- Clear, concise docstrings
- Use Google-style docstrings
- Include examples for complex functions
- Keep README up to date

### Example
\`\`\`python
def analyze_repository(repo_name: str, user_query: str) -> RepoAnalysis:
    \"\"\"
    Perform deep analysis of a GitHub repository.
    
    Args:
        repo_name: Full repository name (owner/repo)
        user_query: User's search query for context
        
    Returns:
        RepoAnalysis object with structured insights
        
    Raises:
        ValueError: If repository not found
        RuntimeError: If analysis fails
        
    Example:
        >>> analysis = analyze_repository("facebook/react", "state management")
        >>> print(analysis.complexity_level)
        Advanced
    \"\"\"
    ...
\`\`\`

## Testing Guidelines

- Write tests for new features
- Maintain or improve code coverage
- Use descriptive test names
- Include docstrings explaining test purpose

\`\`\`python
def test_query_expansion_generates_three_queries(self):
    \"\"\"Verify that strategist generates exactly 3 search queries.\"\"\"
    strategy = query_expansion_strategist("machine learning")
    assert len(strategy.queries) == 3
\`\`\`

## Performance Considerations

- Optimize expensive operations
- Consider caching strategies
- Profile before optimizing
- Document performance implications

## Security

- Never commit API keys or secrets
- Use .env for configuration
- Validate user inputs
- Report security issues privately

## Documentation

Update documentation when:
- Adding new features
- Changing behavior
- Fixing bugs that were undocumented
- Adding new configuration options

## Areas for Contribution

### High Priority
- [ ] Local LLM model support
- [ ] Advanced caching strategies
- [ ] Performance optimization
- [ ] Additional test coverage
- [ ] Export functionality (PDF, JSON)

### Medium Priority
- [ ] UI improvements
- [ ] Better error messages
- [ ] Additional analysis features
- [ ] Extended documentation

### Low Priority
- [ ] Minor bug fixes
- [ ] Code style improvements
- [ ] Documentation corrections

## Questions?

- Check existing issues and discussions
- Read the documentation
- Open a discussion on GitHub
- Contact the maintainers

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page

Thank you for contributing to Scout Agent! 🎉

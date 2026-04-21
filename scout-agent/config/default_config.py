"""Default configuration for Scout Agent."""

# Model Configuration
MODEL_NAME = "gemini-2.5-flash-lite"
MODEL_TEMPERATURE = 0

# GitHub Search Configuration
GITHUB_FETCH_LIMIT = 10
GITHUB_TOP_RESULTS = 3

# Semantic Ranking Configuration
SEMANTIC_SCORE_THRESHOLD = 0.5
KEYWORD_WEIGHT = 0.7
EXPANSION_WEIGHT = 0.3

# File Processing Configuration
MAX_FILES_TO_RETURN = 300
MAX_FILE_CONTENT_LENGTH = 2000
README_PREVIEW_LENGTH = 1500

# Repository Filtering
QUALITY_FILTERS = {
    "min_size": 100,  # Minimum repo size in KB
    "exclude_forks": True,
    "exclude_terms": ["awesome-", "-list", "curated", "collection"]
}

# Noise Filtering for File Trees
NOISE_PATTERNS = [
    '.git', '.github', 'node_modules', 'venv', 
    'images', 'assets', '.png', '.jpg', '.pdf'
]

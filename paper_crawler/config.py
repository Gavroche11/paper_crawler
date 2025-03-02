"""
Configuration settings for the PubMed crawler.
"""
from typing import List

# Journal and date range configuration
JOURNAL_TITLE: str = "Radiol Artif Intell"  # Journal title to search
FROM_YEAR: str = "2019"  # Start year for search
TO_YEAR: str = "3000"  # End year for search (a large number to include all future years)

# Result limitations
MAX_ARTICLES: int = -1  # If set to -1, the code will attempt to fetch all articles

# Keywords to search for in titles and abstracts
KEYWORDS: List[str] = [
    "language model", "llm", "gpt", "bert", "transformer", 
    "nlp", "natural language processing", "chatgpt", "claude", "prompt",
    "llama", "mistral", "gemini", "text-to-text", "text generation", "text embedding",
    "foundation model", "generative ai"
]

# Output configuration
OUTPUT_PATH: str = "outputs/radiol_ai_lang_model_papers.json"

# Article type filtering
RESEARCH_ARTICLES_ONLY: bool = True  # Set to True to exclude reviews, editorials, letters, and comments

# Execution configuration
BATCH_SIZE: int = 100  # Number of articles to fetch per request
ABSTRACT_BATCH_SIZE: int = 10  # Number of abstracts to fetch per request
DELAY: float = 0.34  # Delay between requests to avoid hitting API rate limits
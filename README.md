# Paper Crawler

A flexible tool for searching and retrieving academic papers from PubMed based on configurable criteria.

## Features

- Search PubMed for articles from specific journals
- Filter by date range and publication type
- Keyword filtering to find relevant papers
- Full article metadata retrieval (title, authors, abstract, etc.)
- Structured abstract parsing
- JSON output for further analysis
- Configurable search parameters

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Gavroche11/paper_crawler.git
cd paper_crawler

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

### Command-line Interface

```bash
# Run as a module
python -m paper_crawler

# Or use the convenience script
python scripts/run_crawler.py
```

### Command-line Options

```
--journal TEXT         Journal title to search (default: "Radiol Artif Intell")
--from-year TEXT       Start year for search (default: "2019")
--to-year TEXT         End year for search (default: "3000")
--max-articles INT     Maximum articles to fetch, -1 for all (default: -1)
--output TEXT          Output JSON file path (default: "outputs/radiol_ai_lang_model_papers.json")
--include-all-types    Include all article types (reviews, editorials, etc.)
                       Without this flag, only research articles are included (default behavior)
```

### Example

```bash
# Search for language model papers in Radiology from 2020 to present, max 50 articles
python -m paper_crawler --journal "Radiology" --from-year "2020" --max-articles 50

# Include all article types (not just research articles)
python -m paper_crawler --journal "Radiology" --include-all-types
```

## Configuration

You can customize the default search parameters by editing the `config.py` file in the `paper_crawler` directory. This allows you to change the behavior without modifying the command-line arguments each time.

### Search Parameters

```python
# Journal and date range configuration
JOURNAL_TITLE: str = "Radiol Artif Intell"  # Journal title to search
FROM_YEAR: str = "2019"  # Start year for search (when the journal started)
TO_YEAR: str = "3000"  # End year for search (using a large number for all future articles)

# Article type filtering
RESEARCH_ARTICLES_ONLY: bool = True  # Exclude reviews, editorials, letters, and comments

# Result limitations
MAX_ARTICLES: int = -1  # Maximum number of articles to retrieve (-1 for all)
```

### Keyword Configuration

Customize the list of keywords used to filter articles. The tool will find articles that contain any of these keywords in their title or abstract:

```python
# Keywords to search for in titles and abstracts
KEYWORDS: List[str] = [
    "language model", "llm", "gpt", "bert", "transformer", 
    "nlp", "natural language processing", "chatgpt", "claude", "prompt",
    "llama", "mistral", "gemini", "text-to-text", "text generation", "text embedding",
    "foundation model", "generative ai", "generative model"
]
```

### Output and Performance Settings

```python
# Output configuration
OUTPUT_PATH: str = "outputs/radiol_ai_lang_model_papers.json"  # Path for results

# Execution configuration
BATCH_SIZE: int = 100  # Number of articles to fetch per request
ABSTRACT_BATCH_SIZE: int = 10  # Number of abstracts to fetch per request
DELAY: float = 0.34  # Delay between requests to avoid hitting API rate limits
TIMEOUT: float = 30.0  # Timeout for API requests in seconds
MAX_RETRIES: int = 5  # Maximum number of retries for failed requests
BASE_WAIT_TIME: float = 1.0  # Base wait time for exponential backoff
```

## Output

The tool generates a JSON file containing:
- Search query used
- Number of total articles found
- Keywords used for filtering
- Number of of relevant articles
- Full details of each article (title, authors, abstract, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
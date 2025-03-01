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
--journal TEXT        Journal title to search (default: "Radiol Artif Intell")
--from-year TEXT      Start year for search (default: "2019")
--to-year TEXT        End year for search (default: "3000")
--max-articles INT    Maximum articles to fetch, -1 for all (default: -1)
--output TEXT         Output JSON file path (default: "paper_crawler_results.json")
--research-only       Include only research articles (exclude reviews, editorials, etc.)
--verbose             Enable verbose output
```

### Example

```bash
# Search for papers in Radiology from 2020 to 2023, max 50 articles
python -m paper_crawler --journal "Radiology" --from-year "2020" --to-year "2023" --max-articles 50
```

## Configuration

You can customize the default search parameters by editing the `config.py` file:

- `JOURNAL_TITLE`: Default journal to search
- `FROM_YEAR` & `TO_YEAR`: Date range for the search
- `MAX_ARTICLES`: Maximum number of articles to retrieve (-1 for all)
- `KEYWORDS`: List of keywords to filter articles by
- `RESEARCH_ARTICLES_ONLY`: Whether to exclude reviews, editorials, etc.
- `VERBOSE`: Enable detailed logging
- `DELAY`: Delay between API requests to respect rate limits

## Output

The tool generates a JSON file containing:
- Search query used
- Total articles found
- Keywords used for filtering
- Count of relevant articles
- Full details of each article (title, authors, abstract, etc.)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
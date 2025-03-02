"""
Command-line interface for the crawler.
"""
import argparse
from argparse import Namespace
from typing import List, Dict, Any, Optional

from . import config
from .pubmed_client import get_all_pubmed_ids, fetch_article_details, fetch_abstracts
from .article_processor import filter_articles_by_keywords, display_article_summary
from .utils import build_search_query, save_results_to_json


def parse_arguments(args=None) -> Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Command line arguments (None to use sys.argv)
        
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(description="Search PubMed for papers in academic journals")
    
    parser.add_argument("--journal", type=str, default=config.JOURNAL_TITLE,
                        help=f"Journal title to search (default: {config.JOURNAL_TITLE})")
    
    parser.add_argument("--from-year", type=str, default=config.FROM_YEAR,
                        help=f"Start year for search (default: {config.FROM_YEAR})")
    
    parser.add_argument("--to-year", type=str, default=config.TO_YEAR,
                        help=f"End year for search (default: {config.TO_YEAR})")
    
    parser.add_argument("--max-articles", type=int, default=config.MAX_ARTICLES,
                        help=f"Maximum articles to fetch, -1 for all (default: {config.MAX_ARTICLES})")
    
    parser.add_argument("--output", type=str, default=config.OUTPUT_PATH,
                        help=f"Output JSON file path (default: {config.OUTPUT_PATH})")
    
    parser.add_argument("--include-all-types", action="store_false", dest="research_only",
                        default=config.RESEARCH_ARTICLES_ONLY,
                        help="Include all article types (reviews, editorials, etc.)")
    
    return parser.parse_args(args)


def run_crawler(args: Optional[Namespace] = None) -> None:
    """
    Run the paper crawler with the given arguments.
    
    Args:
        args: Command line arguments (if None, will parse from command line)
    """
    # Parse command line arguments if not provided
    if args is None:
        args = parse_arguments()
    
    # Update config variables from arguments
    journal_title = args.journal
    from_year = args.from_year
    to_year = args.to_year
    max_articles = args.max_articles
    output_path = args.output
    research_only = args.research_only
    
    # Build the search query
    query = build_search_query(journal_title, from_year, to_year, research_only)
    
    print(f"Searching PubMed for articles from '{journal_title}' between {from_year} and {to_year}...")
    if research_only:
        print("Filtering for research articles only (excluding reviews, editorials, letters, and comments).")
    
    if max_articles == -1:
        print("No maximum limit specified; will fetch all results until none remain.")
    else:
        print(f"Will fetch up to {max_articles} articles.")
    
    # Search PubMed for matching PMIDs
    pmids = get_all_pubmed_ids(query, max_articles, config.BATCH_SIZE)
    print(f"Retrieved {len(pmids)} PubMed IDs.\n")
    
    if not pmids:
        print("No articles found.")
        return
    
    # Fetch article details
    articles = fetch_article_details(pmids, config.BATCH_SIZE)
    print(f"Retrieved details for {len(articles)} articles.\n")
    
    # Fetch abstracts for articles
    fetch_abstracts(articles, config.ABSTRACT_BATCH_SIZE)
    
    # Filter for language model related articles
    relevant_articles = filter_articles_by_keywords(articles, config.KEYWORDS)
    
    print(f"Found {len(relevant_articles)} articles that contain at least one keyword:\n")
    
    # Display results
    for article in relevant_articles[:5]:
        display_article_summary(article)
    
    # Save results as JSON
    save_results_to_json(output_path, query, len(pmids), config.KEYWORDS, relevant_articles)


def main() -> None:
    """Main entry point for the crawler."""
    run_crawler()


if __name__ == "__main__":
    main()
"""
Functions for fetching citation counts for papers.
"""
import time
import requests
from typing import Dict, List, Optional, Any
from tqdm import tqdm

from . import config


def fetch_citation_count_by_doi(doi: str, 
                               max_retries: int = 3, 
                               base_wait_time: float = 1.0) -> Optional[int]:
    """
    Fetch citation count for a paper using its DOI via Semantic Scholar API.
    
    Args:
        doi: Digital Object Identifier for the paper
        max_retries: Maximum number of retry attempts
        base_wait_time: Base wait time between retries in seconds
        
    Returns:
        Citation count as integer or None if not found/error
    """
    if not doi:
        return None
    
    # Clean the DOI
    doi = doi.strip()
    if doi.lower().startswith("doi:"):
        doi = doi[4:].strip()
    
    # Semantic Scholar API endpoint
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=citationCount"
    
    headers = {
        "User-Agent": "Paper-Crawler/0.1.0 (https://github.com/Gavroche11/paper_crawler)"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=config.TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data and "citationCount" in data:
                    return data["citationCount"]
                return 0
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = base_wait_time * (2 ** attempt)
                time.sleep(wait_time)
                continue
                
            # For other errors, try crossref as fallback
            return fetch_citation_count_from_crossref(doi)
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = base_wait_time * (2 ** attempt)
                time.sleep(wait_time)
            else:
                # Try crossref as fallback
                return fetch_citation_count_from_crossref(doi)
    
    return None


def fetch_citation_count_from_crossref(doi: str, 
                                      max_retries: int = 2, 
                                      base_wait_time: float = 1.0) -> Optional[int]:
    """
    Fetch citation count from Crossref as a fallback.
    
    Args:
        doi: Digital Object Identifier for the paper
        max_retries: Maximum number of retry attempts
        base_wait_time: Base wait time between retries in seconds
        
    Returns:
        Citation count as integer or None if not found/error
    """
    if not doi:
        return None
    
    # Clean the DOI
    doi = doi.strip()
    if doi.lower().startswith("doi:"):
        doi = doi[4:].strip()
    
    # Crossref API endpoint
    url = f"https://api.crossref.org/works/{doi}"
    
    headers = {
        "User-Agent": "Paper-Crawler/0.1.0 (mailto:example@domain.com)"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=config.TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data and "message" in data and "is-referenced-by-count" in data["message"]:
                    return data["message"]["is-referenced-by-count"]
                return 0
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = base_wait_time * (2 ** attempt)
                time.sleep(wait_time)
                continue
                
            # For other errors
            return None
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = base_wait_time * (2 ** attempt)
                time.sleep(wait_time)
            else:
                return None
    
    return None


def fetch_citation_count_by_pmid(pmid: str, 
                                max_retries: int = 3, 
                                base_wait_time: float = 1.0) -> Optional[int]:
    """
    Fetch citation count for a paper using its PMID via the iCite API.
    
    Args:
        pmid: PubMed ID for the paper
        max_retries: Maximum number of retry attempts
        base_wait_time: Base wait time between retries in seconds
        
    Returns:
        Citation count as integer or None if not found/error
    """
    if not pmid:
        return None
    
    # NIH iCite API endpoint
    base_url = "https://icite.od.nih.gov/api/pubs"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{base_url}/{pmid}", timeout=config.TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data and "data" in data and "citation_count" in data["data"]:
                    return data["data"]["citation_count"]
                return 0
                
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = base_wait_time * (2 ** attempt)
                time.sleep(wait_time)
                continue
                
            # For other errors
            return None
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = base_wait_time * (2 ** attempt)
                time.sleep(wait_time)
            else:
                return None
    
    return None


def fetch_citation_count_by_title_authors(title: str, authors: List[str], 
                                        max_retries: int = 2,
                                        base_wait_time: float = 1.0) -> Optional[int]:
    """
    Fetch citation count using paper title and authors as a last resort.
    
    Args:
        title: Paper title
        authors: List of author names
        max_retries: Maximum number of retry attempts
        base_wait_time: Base wait time between retries in seconds
        
    Returns:
        Citation count as integer or None if not found/error
    """
    if not title:
        return None
    
    # Use first author's last name if available
    first_author = ""
    if authors and len(authors) > 0:
        first_author = authors[0].split()[-1]  # Get last name of first author
    
    # Semantic Scholar API search endpoint
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    params = {
        "query": f"{title} {first_author}",
        "fields": "citationCount",
        "limit": 1
    }
    
    headers = {
        "User-Agent": "Paper-Crawler/0.1.0 (https://github.com/Gavroche11/paper_crawler)"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=config.TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data and "data" in data and len(data["data"]) > 0:
                    paper = data["data"][0]
                    if "citationCount" in paper:
                        return paper["citationCount"]
                return 0
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = base_wait_time * (2 ** attempt)
                time.sleep(wait_time)
                continue
                
            # For other errors
            return None
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = base_wait_time * (2 ** attempt)
                time.sleep(wait_time)
            else:
                return None
    
    return None


def enrich_articles_with_citations(articles: List[Dict[str, Any]], 
                                 batch_size: int = 5) -> None:
    """
    Fetch citation counts for a list of articles and add them directly to the article dictionaries.
    Uses multiple sources to maximize chances of finding citation data.
    
    Args:
        articles: List of article dictionaries to enrich with citation data
        batch_size: Number of articles to process in each batch for progress display
    """
    print(f"Fetching citation counts for {len(articles)} articles...")
    
    # Process citations with a progress bar
    with tqdm(total=len(articles), desc="Fetching citations") as pbar:
        for i, article in enumerate(articles):
            citation_count = None
            
            # Try DOI first (Semantic Scholar)
            if "doi" in article and article["doi"]:
                citation_count = fetch_citation_count_by_doi(article["doi"])
                
            # Try PMID as second option (iCite)
            if citation_count is None and "pmid" in article and article["pmid"]:
                citation_count = fetch_citation_count_by_pmid(article["pmid"])
                
            # Try title and authors as last resort
            if citation_count is None and "title" in article:
                citation_count = fetch_citation_count_by_title_authors(
                    article["title"], 
                    article.get("authors", [])
                )
                
            # Set citation count in article
            if citation_count is not None:
                article["citation_count"] = citation_count
            else:
                article["citation_count"] = 0  # Default to 0 if we couldn't get data
                
            # Add citation source info
            if "doi" in article and article["doi"] and citation_count is not None:
                article["citation_source"] = "semantic_scholar"
            elif "pmid" in article and article["pmid"] and citation_count is not None:
                article["citation_source"] = "icite"
            elif citation_count is not None:
                article["citation_source"] = "title_search"
            else:
                article["citation_source"] = "none"
                
            pbar.update(1)
            
            # Add a small delay between requests to avoid overwhelming the APIs
            time.sleep(config.DELAY)
            
            # Additional delay every batch_size articles
            if (i + 1) % batch_size == 0:
                time.sleep(config.DELAY * 2)
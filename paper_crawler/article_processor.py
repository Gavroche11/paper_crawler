"""
Functions for processing and filtering articles.
"""
from typing import List, Dict, Any

def contains_any_keyword(text: str, keywords: List[str]) -> bool:
    """
    Returns True if any of the keywords appear in the given text (case-insensitive).
    
    Args:
        text: Text to search in
        keywords: List of keywords to search for
        
    Returns:
        True if any keyword is found, False otherwise
    """
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


def filter_articles_by_keywords(articles: List[Dict[str, Any]], 
                               keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Filter articles that contain any of the specified keywords in their title or abstract.
    
    Args:
        articles: List of article dictionaries
        keywords: List of keywords to search for
        
    Returns:
        Filtered list of articles
    """
    relevant_articles = []
    
    for article in articles:
        title = article.get("title", "")
        abstract = article.get("abstract", "")
        
        if contains_any_keyword(f"{title} {abstract}", keywords):
            relevant_articles.append(article)
    
    return relevant_articles


def display_article_summary(article: Dict[str, Any], max_abstract_length: int = 150) -> None:
    """
    Print a summary of an article.
    
    Args:
        article: Article dictionary
        max_abstract_length: Maximum length of abstract snippet to display
    """
    print(f"- Title: {article['title']}")
    
    if 'abstract' in article and article['abstract']:
        abstract_snippet = article['abstract'][:max_abstract_length]
        if len(article['abstract']) > max_abstract_length:
            abstract_snippet += "..."
        print(f"  Abstract: {abstract_snippet}")
    else:
        print("  Abstract: N/A")
        
    print(f"  PMID: {article['pmid']}")
    print(f"  DOI: {article['doi']}")
    print(f"  URL: {article['url']}")
    print(f"  Date: {article['pub_date']}")
    if 'citation_count' in article:
        print(f"  Citations: {article['citation_count']}")
    print(f"  Authors: {', '.join(article['authors']) if article['authors'] else 'N/A'}")
    print("")
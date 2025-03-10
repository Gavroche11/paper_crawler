"""
Utility functions for the crawler.
"""
import json

def build_search_query(journal_title: str, 
                       from_year: str, 
                       to_year: str, 
                       research_articles_only: bool = True) -> str:
    """
    Build a PubMed search query based on the provided parameters.
    
    Args:
        journal_title: Journal title to search
        from_year: Start year for the search range
        to_year: End year for the search range
        research_articles_only: Whether to filter for research articles only
        
    Returns:
        Formatted PubMed search query
    """
    query = f'"{journal_title}"[Journal] AND {from_year}:{to_year}[pdat]'
    
    if research_articles_only:
        query += ' AND ("Journal Article"[Publication Type] ' \
                 'NOT "Review"[Publication Type] ' \
                 'NOT "Editorial"[Publication Type] ' \
                 'NOT "Letter"[Publication Type] ' \
                 'NOT "Comment"[Publication Type])'
    
    return query


def save_results_to_json(output_path: str, 
                        search_query: str, 
                        total_count: int, 
                        keywords: list, 
                        filtered_articles: list) -> None:
    """
    Save search results to a JSON file.
    
    Args:
        output_path: Path to save the JSON file
        search_query: The search query used
        total_count: Total number of articles found
        keywords: Keywords used for filtering
        filtered_articles: List of filtered articles
    """
    
    result = {
        "search_query": search_query,
        "num_total_articles": total_count,
        "keywords": keywords,
        "num_relevant_articles": len(filtered_articles),
        "relevant_articles": filtered_articles
    }
    
    # Create directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Results saved to {output_path}")
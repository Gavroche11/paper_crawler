"""
Client functions for interacting with the PubMed API.
"""
import time
import requests
from typing import List, Dict, Optional, Any
from xml.etree import ElementTree as ET
from tqdm import tqdm

from . import config

def fetch_pubmed_ids(query: str,
                     retmax: int = 100,
                     retstart: int = 0) -> Optional[Dict]:
    """
    Fetch PubMed IDs matching the query using the esearch endpoint.
    
    Args:
        query: PubMed search query
        retmax: Maximum number of results to return
        retstart: Starting index for retrieved results
        
    Returns:
        Dict containing search results or None if request failed
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retstart": retstart,
        "retmode": "json",
        "sort": "date"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data from PubMed: {e}")
        return None


def get_all_pubmed_ids(query: str,
                       max_articles: int = 100,
                       max_step: int = 100) -> List[str]:
    """
    Fetches PubMed IDs in pages of 'step' items with a progress bar.
    If max_articles == -1, fetch all results up to the total count.
    
    Args:
        query: PubMed search query
        max_articles: Maximum number of articles to retrieve (-1 for all)
        max_step: Number of articles to fetch per request
        
    Returns:
        List of PubMed IDs
    """
    # First make a request to get the total count
    initial_data = fetch_pubmed_ids(query, retmax=1)
    if not initial_data:
        print("Failed to get initial results count")
        return []
        
    total_count = int(initial_data.get("esearchresult", {}).get("count", 0))
    print(f"Total matching articles: {total_count}")
    
    if total_count == 0:
        return []
    
    # If max_articles is -1, set it to total_count
    if max_articles == -1:
        max_articles = total_count
    
    # Calculate number of batches needed
    num_batches = (min(total_count, max_articles) + max_step - 1) // max_step

    all_pmids = []
    
    # Create progress bar
    with tqdm(total=min(total_count, max_articles), desc="Fetching PubMed IDs") as pbar:
        for batch_idx in range(num_batches):
            retstart = batch_idx * max_step
            
            # Calculate how many items to fetch in this batch
            remaining = max_articles - len(all_pmids)
            if remaining <= 0:
                break
                
            to_fetch = min(max_step, remaining)
            
            # vprint(f"Fetching batch {batch_idx+1} - results {retstart+1} to {retstart+to_fetch}...")
            
            data = fetch_pubmed_ids(query, retmax=to_fetch, retstart=retstart)
            if not data or "esearchresult" not in data or "idlist" not in data["esearchresult"]:
                break  # no more valid data
            
            id_list = data["esearchresult"]["idlist"]
            all_pmids.extend(id_list)
            
            # Update progress bar
            pbar.update(len(id_list))
            
            # If PubMed returns fewer items than requested, we've reached the end
            if len(id_list) < to_fetch:
                break
            
            # Respect PubMed API rate limits (max 3 requests per second)
            time.sleep(config.DELAY)
    
    return all_pmids


def fetch_article_details(pmids: List[str], batch_size: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch details for articles with the given PMIDs.
    
    Args:
        pmids: List of PubMed IDs
        batch_size: Number of PMIDs to process per request
        
    Returns:
        List of article details dictionaries
    """
    if not pmids:
        return []
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    articles = []
    
    # Process in batches to avoid exceeding URL length limits
    total_batches = (len(pmids) + batch_size - 1) // batch_size
    
    # Create a progress bar
    with tqdm(total=len(pmids), desc="Fetching article details") as pbar:
        for batch_idx in range(total_batches):
            batch_pmids = pmids[batch_idx*batch_size:(batch_idx+1)*batch_size]
            pmid_string = ",".join(batch_pmids)
            
            params = {
                "db": "pubmed",
                "id": pmid_string,
                "retmode": "json"
            }
            
            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                
                summary_data = response.json()
                result = summary_data.get("result", {})
                
                # Remove the UIDs list which contains duplicate information
                uids = result.pop("uids", []) if "uids" in result else []
                
                # Process each article in this batch
                for pmid in uids:
                    try:
                        article_data = result.get(pmid, {})
                        
                        # Create a cleaner article object
                        clean_article = {
                            "pmid": pmid,
                            "title": " ".join(article_data.get("title", "").split()),
                            "journal": article_data.get("fulljournalname", ""),
                            "pub_date": article_data.get("pubdate", ""),
                            "doi": article_data.get("elocationid", "").replace("doi: ", "") if "elocationid" in article_data else "",
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
                            "authors": [author.get("name", "") for author in article_data.get("authors", [])],
                            "abstract": ""  # Will fetch separately
                        }
                        
                        articles.append(clean_article)
                    except Exception as e:
                        print(f"Error processing article {pmid}: {e}")
                
                # Update progress bar with the number of articles processed in this batch
                pbar.update(len(batch_pmids))
            
            except Exception as e:
                print(f"Error fetching batch {batch_idx + 1}: {e}")
            
            # Respect API rate limits
            time.sleep(config.DELAY)
    
    return articles


def extract_abstracts_from_xml(xml_content: str) -> Dict[str, str]:
    """
    Extract abstracts from PubMed XML response, handling structured abstracts.
    
    Args:
        xml_content: XML content from PubMed
        pmids: List of PMIDs in the batch
        
    Returns:
        Dictionary mapping PMIDs to their abstracts
    """
    abstracts = {}
    
    try:
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Find all PubmedArticle elements
        articles = root.findall(".//PubmedArticle")
        
        for article in articles:
            # Get PMID
            pmid_elem = article.find(".//PMID")
            if pmid_elem is None:
                continue
                
            pmid = pmid_elem.text
            
            # Handle structured abstract
            abstract_parts = []
            
            # First try to find structured abstract sections
            abstract_sections = article.findall(".//Abstract/AbstractText")
            
            for section in abstract_sections:
                # Get section label if it exists
                label = section.get("Label", "")
                section_text = section.text or ""
                
                if label and section_text:
                    abstract_parts.append(f"{label}: {section_text}")
                elif section_text:
                    abstract_parts.append(section_text)
            
            # If no structured sections found, try to get plain abstract text
            if not abstract_parts:
                abstract_elem = article.find(".//Abstract/AbstractText")
                if abstract_elem is not None and abstract_elem.text:
                    abstract_parts.append(abstract_elem.text)
            
            # Join all parts with newlines for readability
            if abstract_parts:
                abstracts[pmid] = " ".join(abstract_parts)
            else:
                abstracts[pmid] = ""
                
    except Exception as e:
        print(f"Error parsing XML for abstracts: {e}")
    
    return abstracts


def extract_abstract_from_text(text_content: str) -> str:
    """
    Extract abstract from PubMed text response.
    
    Args:
        text_content: Text content from PubMed
        
    Returns:
        Extracted abstract
    """
    abstract = ""
    
    # Look for the abstract section
    if "Abstract" in text_content:
        abstract_parts = text_content.split("Abstract", 1)
        if len(abstract_parts) > 1:
            # Try to find the end of the abstract by looking for common section headers
            abstract_text = abstract_parts[1].strip()
            for term in ["\n\nMeSH", "\n\nPMID", "\n\nCopyright", "\n\nAuthor", "\n\n20"]:
                if term in abstract_text:
                    abstract_text = abstract_text.split(term, 1)[0]
            
            # Handle potential structured abstract by preserving section headers
            lines = abstract_text.split("\n")
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    cleaned_lines.append(line)
            
            abstract = " ".join(cleaned_lines)
    
    return abstract


def fetch_abstracts(articles: List[Dict],
                    batch_size: int = 10,
                    ) -> None:
    """
    Fetch abstracts for articles and add them to the article dictionaries.
    Handles both regular and structured abstracts.
    
    Args:
        articles: List of article dictionaries
        batch_size: Number of articles to process per batch
    """
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    total_batches = (len(articles) + batch_size - 1) // batch_size
    
    print(f"Fetching abstracts for {len(articles)} articles...")
    
    # Create a progress bar
    with tqdm(total=len(articles), desc="Fetching abstracts") as pbar:
        for batch_idx in range(total_batches):
            batch_articles = articles[batch_idx*batch_size:(batch_idx+1)*batch_size]
            batch_pmids = [article["pmid"] for article in batch_articles]
            pmid_string = ",".join(batch_pmids)
            
            # First try to get XML format which better preserves structured abstracts
            xml_params = {
                "db": "pubmed",
                "id": pmid_string,
                "rettype": "abstract",
                "retmode": "xml"
            }
            
            try:
                xml_response = requests.get(base_url, params=xml_params, timeout=30)
                xml_response.raise_for_status()
                xml_content = xml_response.text
                
                # Parse XML to extract abstracts
                abstracts_by_pmid = extract_abstracts_from_xml(xml_content)
                
                # Update articles with abstracts from XML
                for article in batch_articles:
                    pmid = article["pmid"]
                    if pmid in abstracts_by_pmid and abstracts_by_pmid[pmid]:
                        article["abstract"] = abstracts_by_pmid[pmid]
                        continue
                        
                    # If we didn't get an abstract from XML, try plain text as fallback
                    text_params = {
                        "db": "pubmed",
                        "id": pmid,
                        "rettype": "abstract",
                        "retmode": "text"
                    }
                    
                    text_response = requests.get(base_url, params=text_params, timeout=30)
                    text_response.raise_for_status()
                    text_content = text_response.text
                    
                    # Extract abstract from text
                    abstract = extract_abstract_from_text(text_content)
                    article["abstract"] = abstract
                    
                    # Add a small delay between individual requests
                    time.sleep(config.DELAY)
                
                # Update progress bar
                pbar.update(len(batch_articles))
                    
            except Exception as e:
                print(f"Error fetching abstracts for batch {batch_idx + 1}: {e}")
            
            # Delay between batches
            time.sleep(config.DELAY)
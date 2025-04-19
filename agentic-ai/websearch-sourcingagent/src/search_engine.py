import os
import requests
import logging
from googleapiclient.discovery import build
from typing import Dict, List, Optional, Tuple

class SearchQuery:
    """Class to handle search query generation and execution"""
    
    def __init__(
        self, 
        api_key: str, 
        custom_search_id: str,
        min_results: int = 100
    ):
        """
        Initialize the search engine
        
        Args:
            api_key: Google API key
            custom_search_id: Google Custom Search Engine ID
            min_results: Minimum number of results to fetch (default: 100)
        """
        self.api_key = api_key
        self.custom_search_id = custom_search_id
        self.min_results = min_results
        self.service = build("customsearch", "v1", developerKey=api_key)
        self.logger = logging.getLogger('sourcing_agent.search_engine')
    
    def _build_query(
        self, 
        must_have: List[str],
        should_have: Optional[List[str]] = None,
        wont_have: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Build a search query string based on keywords and location
        
        Args:
            must_have: List of keywords that must be included
            should_have: List of keywords that should be included if possible
            wont_have: List of keywords to exclude
            location: Location to search for candidates
            
        Returns:
            Formatted search query string
        """
        # Format must-have keywords with quotes and concatenate with AND
        query_parts = [f'"{keyword}"' for keyword in must_have]
        
        # Add location if provided
        if location:
            query_parts.append(f'"{location}"')
        
        # Add should-have keywords if provided
        if should_have:
            should_parts = [f'"{keyword}"' for keyword in should_have]
            query_parts.extend(should_parts)
        
        # Add won't-have keywords with minus sign
        if wont_have:
            wont_parts = [f'-"{keyword}"' for keyword in wont_have]
            query_parts.extend(wont_parts)
        
        # Format for search: resume OR cv OR profile OR "work experience"
        search_terms = " OR ".join(['"resume"', '"CV"', '"profile"', '"work experience"', '"LinkedIn"'])
        query_parts.append(f'({search_terms})')
        
        # Add exclusion terms for job postings
        exclusion_terms = ['-"job"', '-"jobs"']
        query_parts.extend(exclusion_terms)
        
        return " ".join(query_parts)
    
    def execute_search(
        self, 
        keywords: Dict[str, List[str]],
        location: Optional[str] = None,
        expand_search: bool = True
    ) -> List[Dict]:
        """
        Execute search using the provided keywords and location
        
        Args:
            keywords: Dictionary with must-have, should-have, and wont-have keywords
            location: Location to search for candidates
            expand_search: Whether to expand search if not enough results
            
        Returns:
            List of search result items
        """
        must_have = keywords.get('must-have', [])
        should_have = keywords.get('should-have', [])
        wont_have = keywords.get('wont-have', [])
        
        # Start with strict search (must-have only)
        query = self._build_query(must_have, wont_have=wont_have, location=location)
        self.logger.info(f"Executing search with query: {query}")
        results = self._execute_search_query(query)
        
        # If expand_search is True and we didn't get enough results, add should-have keywords
        if expand_search and len(results) < self.min_results and should_have:
            query = self._build_query(must_have, should_have, wont_have, location)
            results = self._execute_search_query(query)
            
        return results
    
    def _execute_search_query(self, query: str) -> List[Dict]:
        """
        Execute the actual search using Google Custom Search API
        
        Args:
            query: The formatted search query string
            
        Returns:
            List of search result items
        """
        results = []
        start_index = 1
        
        # Google Custom Search API allows max 10 results per query and max 100 results total
        while len(results) < self.min_results and start_index <= 91:  # 91 + 10 - 1 = 100 (max)
            try:
                search_results = self.service.cse().list(
                    q=query,
                    cx=self.custom_search_id,
                    start=start_index
                ).execute()
                
                if 'items' in search_results:
                    results.extend(search_results['items'])
                else:
                    self.logger.warning(f"No search results found for query '{query}' at index {start_index}")
                    break
                
                start_index += len(search_results.get('items', []))
                self.logger.info(f"Found {len(results)} results so far")
                
            except Exception as e:
                self.logger.error(f"Error executing search query: {str(e)}")
                break
        
        self.logger.info(f"Completed search with {len(results)} total results")
        return results
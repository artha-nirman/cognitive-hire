import os
import requests
from typing import Dict, List, Optional, Set
from bs4 import BeautifulSoup
import re
import time
import json
import logging
from urllib.parse import urlparse

from llm_parser import BaseLLM

# Configure logger for this module
logger = logging.getLogger('sourcing_agent.candidate_scraper')

class CandidateScraper:
    """Class to scrape candidate information from search results"""
    
    def __init__(
        self, 
        llm: BaseLLM,
        headers: Optional[Dict[str, str]] = None,
        delay: float = 1.0
    ):
        """
        Initialize the candidate scraper
        
        Args:
            llm: Language model instance for parsing content
            headers: HTTP headers to use for requests
            delay: Delay between requests in seconds
        """
        self.llm = llm
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.delay = delay
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Configure LinkedIn access failures logger
        self.linkedin_logger = logging.getLogger('sourcing_agent.linkedin_failures')
        linkedin_handler = logging.FileHandler('logs/linkedin_access_failures.log')
        linkedin_formatter = logging.Formatter('%(asctime)s | %(message)s')
        linkedin_handler.setFormatter(linkedin_formatter)
        self.linkedin_logger.addHandler(linkedin_handler)
        self.linkedin_logger.setLevel(logging.INFO)
        
    def extract_candidates_from_search_results(
        self, 
        search_results: List[Dict],
        keywords: Dict[str, List[str]]
    ) -> List[Dict]:
        """
        Extract candidate information from search results
        
        Args:
            search_results: List of search result items
            keywords: Dictionary of keywords for candidate matching
            
        Returns:
            List of dictionaries with candidate information
        """
        candidates = []
        processed_urls = set()
        
        logger.info(f"Processing {len(search_results)} search results...")
        
        # Get the keywords for pre-screening
        must_have_keywords = [kw.lower() for kw in keywords.get('must-have', [])]
        should_have_keywords = [kw.lower() for kw in keywords.get('should-have', [])]
        all_keywords = must_have_keywords + should_have_keywords
        
        for idx, result in enumerate(search_results):
            try:
                url = result.get('link')
                if not url or url in processed_urls:
                    continue
                
                processed_urls.add(url)
                
                logger.info(f"Processing result {idx+1}/{len(search_results)}: {url}")
                
                # Extract initial data from search result
                snippet = result.get('snippet', '')
                title = result.get('title', '')
                
                # Combine title and snippet for initial analysis
                initial_content = f"{title}\n\n{snippet}"
                
                # First pass: check if the search result seems to be about a candidate
                logger.debug(f"Parsing initial content: {initial_content[:100]}...")
                
                # Pre-screening based on keywords and patterns
                should_scrape = False
                reason = ""
                
                # Check for LinkedIn URLs which are very likely candidate profiles
                if self._is_linkedin_profile(url):
                    should_scrape = True
                    reason = "LinkedIn profile URL detected"
                
                # Check if the content contains professional terms
                elif self._contains_professional_terms(initial_content):
                    should_scrape = True
                    reason = "Professional terms detected"
                
                # Check if the content contains partial matches of keywords
                elif self._check_partial_keyword_match(initial_content, all_keywords):
                    should_scrape = True
                    reason = "Keyword match detected"
                
                logger.info(f"Should scrape: {should_scrape} - {reason if should_scrape else 'No relevant information found'}")
                
                # If pre-screening detected a potential candidate, proceed
                if should_scrape:
                    # Get full page content
                    page_content = self._get_page_content(url)
                    if page_content:
                        logger.info(f"Fetched page content: {len(page_content)} characters")
                        
                        # Debug check for LinkedIn login walls
                        if "join now to see" in page_content.lower() or "sign in to continue" in page_content.lower():
                            logger.warning(f"LinkedIn login wall detected. Using fallback extraction.")
                        
                        # Special handling for LinkedIn profiles
                        is_linkedin = 'linkedin.com' in url.lower()
                        
                        # For LinkedIn profiles, always add search snippet to the content for LLM context
                        if is_linkedin:
                            # Enhance page content with search snippet information
                            page_content = f"{page_content}\n\nSEARCH SNIPPET: {initial_content}"
                        
                        # Deep parse with the LLM
                        candidate_data = self.llm.parse_candidate_data(page_content, keywords)
                        
                        # Add source URL
                        candidate_data['source_url'] = url
                        
                        # Add original snippet data
                        candidate_data['snippet'] = snippet
                            
                        # Add title as name if name not found and it's a LinkedIn profile
                        if (candidate_data.get('full_name', 'Not found') == 'Not found' or 
                            candidate_data.get('name', 'Not found') == 'Not found') and is_linkedin:
                            # Extract name from LinkedIn title
                            if ' - ' in title:
                                name = title.split(' - ')[0].strip()
                            elif ' | ' in title:
                                name = title.split(' | ')[0].strip()
                            else:
                                name = title
                                
                            # Clean up the name if needed
                            if 'linkedin' in name.lower():
                                name = name.split('|')[0].strip()
                                
                            # Store in both potential field names for compatibility
                            candidate_data['full_name'] = name
                            candidate_data['name'] = name
                            logger.info(f"Extracted name '{name}' from LinkedIn title")
                            
                        # Extract skills from snippet for LinkedIn if not found by LLM
                        if is_linkedin and (not candidate_data.get('skills') or candidate_data.get('skills', '') == 'Not found'):
                            # Look for skills in snippet
                            skills = []
                            for keyword in all_keywords:
                                if keyword.lower() in snippet.lower() or keyword.lower() in title.lower():
                                    skills.append(keyword)
                            if skills:
                                candidate_data['skills'] = skills
                                logger.info(f"Extracted skills from snippet: {skills}")
                        
                        # Special handling for LinkedIn profiles - always include them
                        has_name = (candidate_data.get('full_name', 'Not found') != 'Not found' or 
                                   candidate_data.get('name', 'Not found') != 'Not found')
                        has_skills = candidate_data.get('skills') and candidate_data.get('skills') != 'Not found'
                        
                        # Always include LinkedIn profiles, regardless of other criteria
                        if is_linkedin or has_name or has_skills:
                            candidates.append(candidate_data)
                            name_display = candidate_data.get('full_name', candidate_data.get('name', 'Unknown name'))
                            logger.info(f"Candidate added: {name_display} - URL: {url}")
                        else:
                            logger.info(f"Candidate skipped - insufficient information. URL: {url}")
                    else:
                        logger.warning(f"Failed to fetch page content for {url}")
                        
                        # For LinkedIn profiles, create a candidate entry even if page fetch fails
                        if 'linkedin.com' in url.lower():
                            logger.info(f"Creating fallback candidate entry for LinkedIn profile")
                            candidate_data = {
                                'source_url': url,
                                'snippet': snippet,
                                'access_error': "Could not access full profile"
                            }
                            
                            # Try to extract name from title
                            if ' - ' in title:
                                name = title.split(' - ')[0].strip()
                            elif ' | ' in title:
                                name = title.split(' | ')[0].strip()
                            else:
                                name = title
                                
                            candidate_data['full_name'] = name
                            candidate_data['name'] = name
                            
                            # Extract skills from search snippet
                            skills = []
                            for keyword in all_keywords:
                                if keyword.lower() in snippet.lower() or keyword.lower() in title.lower():
                                    skills.append(keyword)
                                    
                            if skills:
                                candidate_data['skills'] = skills
                            
                            candidates.append(candidate_data)
                            logger.info(f"Added fallback LinkedIn candidate: {name} with skills: {skills}")
                
                # Sleep to avoid overloading servers
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error processing result {idx}: {str(e)}")
                logger.error(f"URL: {result.get('link', 'Unknown')}")
                logger.error(f"Title: {result.get('title', 'Unknown')}")
        
        return candidates
    
    def _get_page_content(self, url: str) -> Optional[str]:
        """
        Get the content of a web page
        
        Args:
            url: URL of the page to get
            
        Returns:
            HTML content of the page, or None if the request fails
        """
        # Special handling for LinkedIn URLs
        if 'linkedin.com' in url.lower():
            return self._get_linkedin_content(url)
            
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Break into lines and remove leading and trailing space
            lines = (line.strip() for line in text.splitlines())
            
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return None
            
    def _get_linkedin_content(self, url: str) -> str:
        """
        Special handling for LinkedIn profiles with enhanced browser-like headers
        and fallback mechanisms when full access fails
        
        Args:
            url: LinkedIn profile URL
            
        Returns:
            Content extracted from LinkedIn or placeholder with profile info
        """
        try:
            # Use more browser-like headers to avoid detection
            linkedin_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            # Try to get the page with enhanced headers
            logger.info(f"Attempting to access LinkedIn profile with enhanced browser-like headers")
            response = requests.get(url, headers=linkedin_headers, timeout=15)
            
            # Check if we might have hit a login wall
            if 'login' in response.url.lower() or response.status_code != 200:
                logger.warning(f"LinkedIn is requiring login. Status: {response.status_code}")
                # Fall back to extracted information
                return self._create_linkedin_fallback_content(url)
                
            # Check if we got a valid response
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for login wall indicators in parsed content
            login_indicators = ['please log in', 'join now to see', 'sign in to continue']
            page_text = soup.get_text().lower()
            
            if any(indicator in page_text for indicator in login_indicators):
                logger.warning(f"Detected LinkedIn login wall in page content")
                # Fall back to extracted information
                return self._create_linkedin_fallback_content(url)
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Break into lines and remove leading and trailing space
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            logger.info(f"Successfully extracted LinkedIn profile content: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Exception when accessing LinkedIn profile: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            # Fall back to our extracted information
            return self._create_linkedin_fallback_content(url)
            
    def _create_linkedin_fallback_content(self, url: str) -> str:
        """
        Create fallback content for a LinkedIn profile when direct access fails
        
        Args:
            url: LinkedIn profile URL
            
        Returns:
            Structured content with LinkedIn profile information extracted from the URL
        """
        # Extract username from URL
        username = url.split('/in/')[-1].split('/')[0] if '/in/' in url else url.split('/')[-1]
        username = username.split('?')[0]  # Remove any query parameters
        
        # Get country code from URL
        country_code = urlparse(url).netloc.split('.')[0]
        if country_code == 'www' or country_code == 'linkedin':
            country_code = 'Global'
        
        # Create structured content with what we know
        logger.info(f"Creating fallback LinkedIn profile content for {username} ({country_code})")
        
        fallback_content = f"""
LinkedIn Profile Information (Extracted from URL)
Username: {username}
Profile URL: {url}
Country/Region: {country_code}

Note: Full LinkedIn profile content could not be accessed due to LinkedIn's security measures.
The following information was extracted from search results and the URL.

This is a placeholder for the LinkedIn profile that would normally be accessed.
The LLM should extract any relevant information from the profile URL and search snippet.
"""

        # Store this URL for later reference as a profile that needs manual checking
        self._log_linkedin_access_failure(url, username, country_code)
        
        return fallback_content
        
    def _log_linkedin_access_failure(self, url: str, username: str, country_code: str) -> None:
        """
        Log LinkedIn access failures for later review
        
        Args:
            url: LinkedIn profile URL
            username: LinkedIn username
            country_code: Country code from URL
        """
        try:
            # Log to the structured LinkedIn failures log
            self.linkedin_logger.info(f"{url} | {username} | {country_code}")
            
            # Also maintain the original flat file for backwards compatibility
            log_file = "data/linkedin_access_failures.log"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            with open(log_file, "a") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp} | {url} | {username} | {country_code}\n")
                
        except Exception as e:
            logger.error(f"Error logging LinkedIn access failure: {str(e)}")
    
    def save_candidates(self, candidates: List[Dict], output_file: str) -> None:
        """
        Save candidate data to a JSON file
        
        Args:
            candidates: List of candidate dictionaries
            output_file: Path to output file
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(candidates, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(candidates)} candidates to {output_file}")
        except Exception as e:
            logger.error(f"Error saving candidates to {output_file}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Number of candidates: {len(candidates)}")
    
    def match_skills(self, candidate_data: Dict, keywords: Dict[str, List[str]]) -> Dict:
        """
        Match candidate skills against required keywords
        
        Args:
            candidate_data: Dictionary with candidate information
            keywords: Dictionary with must-have and should-have keywords
            
        Returns:
            Updated candidate data with matched skills
        """
        skills = candidate_data.get('skills', [])
        if isinstance(skills, str):
            # Try to parse skills as a list if it's a string
            if skills.startswith('[') and skills.endswith(']'):
                try:
                    skills = json.loads(skills)
                except:
                    skills = [s.strip() for s in skills.split(',')]
            else:
                skills = [s.strip() for s in skills.split(',')]
        
        must_have = set(k.lower() for k in keywords.get('must-have', []))
        should_have = set(k.lower() for k in keywords.get('should-have', []))
        
        # Convert skills to lowercase for matching
        skills_lower = [s.lower() for s in skills]
        
        # Find matches
        must_have_matches = [skill for skill in must_have if any(skill in s for s in skills_lower)]
        should_have_matches = [skill for skill in should_have if any(skill in s for s in skills_lower)]
        
        # Update candidate data
        candidate_data['matched_must_have'] = must_have_matches
        candidate_data['matched_should_have'] = should_have_matches
        candidate_data['match_score'] = len(must_have_matches) + (0.5 * len(should_have_matches))
        
        return candidate_data

    def _is_linkedin_profile(self, url: str) -> bool:
        """
        Check if a URL is a LinkedIn profile
        
        Args:
            url: URL to check
            
        Returns:
            True if the URL is a LinkedIn profile, False otherwise
        """
        # Normalize URL to lowercase
        url_lower = url.lower()
        
        # Check for LinkedIn profile patterns
        # This covers both international domains (like in.linkedin.com) and standard format
        if re.search(r'linkedin\.com/in/', url_lower) or re.search(r'\.linkedin\.com/in/', url_lower):
            return True
            
        # Also check for public profile format
        if re.search(r'linkedin\.com/pub/', url_lower) or re.search(r'\.linkedin\.com/pub/', url_lower):
            return True
            
        return False
    
    def _contains_professional_terms(self, text: str) -> bool:
        """
        Check if text contains common professional terms indicating a candidate
        
        Args:
            text: Text to check
            
        Returns:
            True if professional terms are found, False otherwise
        """
        # Generic professional terms that apply across industries
        professional_terms = [
            # Resume and CV related terms
            'resume', 'cv', 'curriculum vitae', 'work experience', 'work history',
            'professional profile', 'professional summary', 'career summary', 
            'career objective', 'professional background',
            
            # Generic professional indicators
            'years of experience', 'certified', 'professional experience',
            'expertise', 'proficient in', 'experienced in', 'skilled in',
            'qualifications', 'achievements', 'accomplishments',
            'portfolio', 'references', 'education', 'degree',
            'bachelor', 'master', 'phd', 'mba', 'graduate',
            
            # IT/Tech specific
            'software engineer', 'developer', 'programmer', 'coder', 'github',
            'coding', 'programming', 'development', 'technical skills',
            'full stack', 'back end', 'front end', 'data scientist',
            
            # Engineering fields
            'mechanical engineer', 'civil engineer', 'electrical engineer',
            'chemical engineer', 'biomedical engineer', 'aerospace engineer',
            'industrial engineer', 'environmental engineer', 'engineering degree',
            'design engineer', 'project engineer',
            
            # Healthcare/Medical
            'physician', 'doctor', 'nurse', 'pharmacist', 'medical',
            'healthcare', 'clinical', 'patient care', 'medical degree',
            'hospital', 'clinic', 'treatment', 'diagnosis', 'therapy',
            
            # Finance/Accounting
            'accountant', 'financial analyst', 'auditor', 'tax', 'cpa',
            'accounting', 'bookkeeping', 'controller', 'treasurer',
            'finance manager', 'investment', 'portfolio manager',
            
            # Legal
            'attorney', 'lawyer', 'legal counsel', 'paralegal',
            'law degree', 'jd', 'legal experience', 'practice',
            'law firm', 'legal services',
            
            # Sales/Marketing
            'marketing specialist', 'sales representative', 'account manager',
            'digital marketing', 'seo', 'social media', 'brand manager',
            'product marketing', 'market research', 'advertising',
            
            # Management
            'manager', 'director', 'supervisor', 'team lead',
            'executive', 'chief', 'ceo', 'cto', 'cfo', 'coo',
            'vp', 'vice president', 'head of', 'leadership',
            
            # Human Resources
            'hr', 'human resources', 'recruiter', 'talent acquisition',
            'people operations', 'hiring', 'employee relations',
            'compensation', 'benefits',
            
            # Research/Science
            'scientist', 'researcher', 'analyst', 'laboratory',
            'research and development', 'r&d', 'postdoctoral',
            'experimentation', 'investigation',
            
            # Education
            'teacher', 'professor', 'instructor', 'educator',
            'academic', 'teaching experience', 'lecturer', 
            'faculty', 'curriculum', 'educational',
            
            # Design/Creative
            'designer', 'graphic designer', 'ux designer', 'ui designer',
            'creative director', 'art director', 'artist',
            'illustrator', 'photographer', 'videographer',
            
            # Project Management
            'project manager', 'program manager', 'scrum master',
            'agile', 'waterfall', 'kanban', 'project coordination',
            'pmp', 'prince2', 'project delivery'
        ]
        
        # Normalize text to lowercase
        text_lower = text.lower()
        
        # Check for professional terms
        for term in professional_terms:
            if term in text_lower:
                return True
                
        return False
    
    def _check_partial_keyword_match(self, text: str, keywords: List[str]) -> bool:
        """
        Check if text contains partial matches for keywords or technical terms
        
        Args:
            text: Text to check
            keywords: List of keywords to check for
            
        Returns:
            True if any keyword partially matches, False otherwise
        """
        # Normalize text to lowercase
        text_lower = text.lower()
        
        # Common tech prefixes and suffixes that might indicate a skill
        tech_qualifiers = [
            'programming', 'development', 'software', 'engineer', 'developer',
            'specialist', 'expert', 'professional', 'consultant',
            'experience with', 'knowledge of', 'skills in', 'using', 
            'certified', 'trained in', 'proficient', 'familiar with'
        ]
        
        # Check for tech qualifiers
        for qualifier in tech_qualifiers:
            if qualifier in text_lower:
                return True
        
        # Check for partial keyword matches - this helps catch variations of keywords
        # For example, "Python programming" would match the keyword "python"
        for keyword in keywords:
            # Skip very short keywords to avoid false positives
            if len(keyword) < 3:
                continue
                
            # Check if keyword is contained in text as a part of a word
            if keyword in text_lower:
                return True
                
            # For common programming languages and tools, check for version numbers
            # E.g., "Python 3.9" contains "python"
            for word in text_lower.split():
                if word.startswith(keyword) and (len(word) == len(keyword) or not word[len(keyword)].isalpha()):
                    return True
        
        return False
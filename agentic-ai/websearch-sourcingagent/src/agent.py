import os
import json
import logging.config
from datetime import datetime
from typing import Dict, List, Optional, Any
import dotenv
from pathlib import Path

# Import local modules
from search_engine import SearchQuery
from llm_parser import LLMFactory, BaseLLM
from candidate_scraper import CandidateScraper

class WebsearchSourcingAgent:
    """Top-level agent class for candidate recruitment and screening"""
    
    def __init__(
        self,
        config_file: str = "config/config.json",
        log_config_file: Optional[str] = None,
        log_level: str = "INFO"
    ):
        """
        Initialize the recruitment agent
        
        Args:
            config_file: Path to the configuration file
            log_config_file: Path to the logging configuration file
            log_level: Default logging level if no config file is provided
        """
        # Load environment variables
        dotenv.load_dotenv()
        
        # Initialize configuration
        self.config_file = config_file
        self.config = self._load_config(config_file)
        
        # Set up logging
        self._configure_logging(log_config_file, log_level)
        self.logger = logging.getLogger('sourcing_agent')
        
        # Initialize components to None (lazy initialization)
        self._search_engine = None
        self._llm = None
        self._scraper = None

    def _load_config(self, config_file: str) -> Dict:
        """
        Load configuration from a JSON file
        
        Args:
            config_file: Path to the configuration file
            
        Returns:
            Dictionary with configuration
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config
        except Exception as e:
            # Can't log yet as logging is not set up
            print(f"Error loading configuration from {config_file}: {str(e)}")
            return {}
    
    def save_config(self) -> None:
        """Save the current configuration to the config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration to {self.config_file}: {str(e)}")

    def _configure_logging(self, log_config_file: Optional[str], log_level: str) -> None:
        """
        Configure logging for the application
        
        Args:
            log_config_file: Path to the logging configuration file
            log_level: Default logging level if no config file is provided
        """
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        if log_config_file and os.path.exists(log_config_file):
            # Load logging configuration from file
            try:
                logging.config.fileConfig(log_config_file)
                return
            except Exception as e:
                print(f"Error loading logging configuration from {log_config_file}: {str(e)}")
                print("Falling back to default logging configuration")
        
        # Default logging configuration
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'linkedin_formatter': {
                    'format': '%(asctime)s | %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                },
                'file': {
                    'level': log_level,
                    'class': 'logging.FileHandler',
                    'filename': 'logs/sourcing_agent.log',
                    'formatter': 'standard'
                },
                'linkedin_handler': {
                    'level': 'INFO',
                    'class': 'logging.FileHandler',
                    'filename': 'logs/linkedin_access_failures.log',
                    'formatter': 'linkedin_formatter'
                }
            },
            'loggers': {
                'sourcing_agent': {
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': True
                },
                'sourcing_agent.linkedin_failures': {
                    'handlers': ['linkedin_handler'],
                    'level': 'INFO',
                    'propagate': False
                },
                'sourcing_agent.candidate_scraper': {
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                },
                'sourcing_agent.search_engine': {
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                },
                'sourcing_agent.llm_parser': {
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                }
            }
        }
        
        # Apply the configuration
        logging.config.dictConfig(logging_config)

    @property
    def search_engine(self) -> SearchQuery:
        """Lazy initialization of search engine"""
        if self._search_engine is None:
            google_api_key = self.config.get('google_api_key') or os.getenv('GOOGLE_API_KEY')
            google_cse_id = self.config.get('google_cse_id') or os.getenv('GOOGLE_CSE_ID')
            min_results = self.config.get('min_results', 20)
            
            if not google_api_key or not google_cse_id:
                self.logger.error("Google API key and Custom Search Engine ID are required")
                raise ValueError("Google API key and Custom Search Engine ID are required")
                
            self._search_engine = SearchQuery(
                api_key=google_api_key,
                custom_search_id=google_cse_id,
                min_results=min_results
            )
            
        return self._search_engine
    
    @property
    def llm(self) -> BaseLLM:
        """Lazy initialization of LLM"""
        if self._llm is None:
            llm_type = self.config.get('llm_type') or os.getenv('LLM_TYPE', 'openai').lower()
            self.logger.info(f"Initializing {llm_type.capitalize()} LLM...")
            
            # Set up LLM parameters
            llm_params = {}
            
            try:
                # For Llama or Ollama
                if llm_type in ['llama', 'ollama']:
                    llm_params['api_url'] = (
                        self.config.get('ollama_api_url') or 
                        os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
                    )
                    llm_params['model_name'] = (
                        self.config.get('ollama_model_name') or 
                        os.getenv('OLLAMA_MODEL_NAME', 'llama3')
                    )
                
                # For OpenAI
                elif llm_type == 'openai':
                    llm_params['api_key'] = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
                    if not llm_params['api_key']:
                        self.logger.error("OpenAI API key is required")
                        raise ValueError("OpenAI API key is required")
                
                # For Anthropic
                elif llm_type == 'anthropic':
                    llm_params['api_key'] = self.config.get('anthropic_api_key') or os.getenv('ANTHROPIC_API_KEY')
                    if not llm_params['api_key']:
                        self.logger.error("Anthropic API key is required")
                        raise ValueError("Anthropic API key is required")
                
                self._llm = LLMFactory.create_llm(llm_type, **llm_params)
                
                # Check if Ollama server is available
                if (llm_type in ['ollama', 'llama']) and hasattr(self._llm, 'server_available') and not self._llm.server_available:
                    self.logger.warning("Ollama server is not available. Attempting to fall back to OpenAI...")
                    
                    # Check if OpenAI API key is available for fallback
                    openai_api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
                    if openai_api_key:
                        self._llm = LLMFactory.create_llm('openai', api_key=openai_api_key)
                        self.logger.info("Successfully switched to OpenAI as fallback LLM provider.")
                    else:
                        self.logger.error("No OpenAI API key available for fallback")
                        raise ValueError("No OpenAI API key available for fallback")
                
            except Exception as e:
                self.logger.error(f"Error initializing LLM: {str(e)}")
                self.logger.error(f"LLM type: {llm_type}, Parameters: {llm_params}")
                raise
        
        return self._llm

    @property
    def scraper(self) -> CandidateScraper:
        """Lazy initialization of candidate scraper"""
        if self._scraper is None:
            # Initialize the scraper with the LLM
            self._scraper = CandidateScraper(
                llm=self.llm,
                delay=self.config.get('scraper_delay', 1.0)
            )
        
        return self._scraper
    
    def validate_keywords(self, keywords: Dict[str, List[str]]) -> bool:
        """
        Validate that keywords dictionary has the required structure
        
        Args:
            keywords: Dictionary with must-have, should-have, and wont-have keywords
            
        Returns:
            True if keywords are valid, False otherwise
        """
        # Check if at least one category exists
        if not any(k in keywords for k in ['must-have', 'should-have', 'wont-have']):
            self.logger.error("Keywords must include at least one of 'must-have', 'should-have', or 'wont-have'")
            return False
        
        # Check if 'must-have' is empty
        if 'must-have' not in keywords or not keywords['must-have']:
            self.logger.error("'must-have' keywords are required")
            return False
        
        # Ensure all values are lists
        for key, value in keywords.items():
            if not isinstance(value, list):
                self.logger.error(f"'{key}' must be a list of strings")
                return False
        
        return True
    
    def search_candidates(
        self,
        keywords: Dict[str, List[str]],
        location: Optional[str] = None,
        min_results: Optional[int] = None,
        output_file: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for candidates based on keywords and location
        
        Args:
            keywords: Dictionary with must-have, should-have, and wont-have keywords
            location: Location to search for candidates
            min_results: Minimum number of results to fetch (overrides config)
            output_file: Path to output file (default: data/candidates_YYYY-MM-DD.json)
            
        Returns:
            List of candidate dictionaries
        """
        # Validate keywords
        if not self.validate_keywords(keywords):
            return []
        
        # Log search parameters
        self.logger.info(f"Searching for candidates with the following keywords:")
        self.logger.info(f"Must have: {', '.join(keywords.get('must-have', []))}")
        if 'should-have' in keywords:
            self.logger.info(f"Should have: {', '.join(keywords.get('should-have', []))}")
        if 'wont-have' in keywords:
            self.logger.info(f"Won't have: {', '.join(keywords.get('wont-have', []))}")
        if location:
            self.logger.info(f"Location: {location}")
        
        # Update min_results if provided
        if min_results is not None:
            self.search_engine.min_results = min_results
        
        # Execute search
        search_results = self.search_engine.execute_search(keywords, location=location)
        
        if not search_results:
            self.logger.warning("No search results found")
            return []
        
        self.logger.info(f"Found {len(search_results)} search results")
        
        # Extract candidates
        self.logger.info("Extracting candidate information from search results...")
        candidates = self.scraper.extract_candidates_from_search_results(search_results, keywords)
        
        # Match skills
        for candidate in candidates:
            candidate = self.scraper.match_skills(candidate, keywords)
        
        # Sort candidates by match score
        candidates.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Save candidates
        if output_file is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_file = f"data/candidates_{date_str}.json"
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        self.scraper.save_candidates(candidates, output_file)
        self.logger.info(f"Saved {len(candidates)} candidates to {output_file}")
        
        return candidates

    def get_top_candidates(
        self, 
        candidates: List[Dict], 
        top_n: int = 3
    ) -> List[Dict]:
        """
        Get the top N candidates by match score
        
        Args:
            candidates: List of candidate dictionaries
            top_n: Number of top candidates to return
            
        Returns:
            List of top N candidate dictionaries
        """
        if not candidates:
            return []
            
        # Return top N candidates sorted by match score
        return sorted(candidates, key=lambda x: x.get('match_score', 0), reverse=True)[:top_n]
    
    def print_candidates_summary(
        self, 
        candidates: List[Dict], 
        top_n: int = 3
    ) -> None:
        """
        Print a summary of the top N candidates
        
        Args:
            candidates: List of candidate dictionaries
            top_n: Number of top candidates to summarize
        """
        if not candidates:
            self.logger.info("No candidates found")
            return
        
        top_candidates = self.get_top_candidates(candidates, top_n)
        self.logger.info(f"\nSummary: Found {len(candidates)} potential candidates")
        self.logger.info(f"Top {top_n} candidates by match score:")
        
        for i, candidate in enumerate(top_candidates, 1):
            name = candidate.get('name', 'Unknown')
            skills = ', '.join(candidate.get('matched_must_have', []))
            score = candidate.get('match_score', 0)
            self.logger.info(f"{i}. {name} (Match score: {score:.1f}) - Matched skills: {skills}")
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update the configuration with new values
        
        Args:
            updates: Dictionary with configuration updates
        """
        self.config.update(updates)
        self.save_config()
        
        # Reset components that might depend on the updated config
        if any(key in updates for key in ['google_api_key', 'google_cse_id', 'min_results']):
            self._search_engine = None
            
        if any(key in updates for key in ['llm_type', 'openai_api_key', 'anthropic_api_key', 
                                          'ollama_api_url', 'ollama_model_name']):
            self._llm = None
            self._scraper = None
            
        if 'scraper_delay' in updates:
            self._scraper = None
            
    def continue_iteration(
        self,
        previous_candidates: Optional[List[Dict]] = None,
        previous_keywords: Optional[Dict[str, List[str]]] = None,
        previous_location: Optional[str] = None,
        iteration_history: Optional[List[Dict]] = None
    ) -> bool:
        """
        Ask whether to continue iterating with refined search parameters
        
        Args:
            previous_candidates: List of candidate dictionaries from previous iteration
            previous_keywords: Keywords dictionary from previous iteration
            previous_location: Location string from previous iteration
            iteration_history: List of iteration data dictionaries
            
        Returns:
            True if iteration should continue, False otherwise
        """
        # Initialize iteration history if not provided
        if iteration_history is None:
            iteration_history = []
            
        # Add previous iteration to history if available
        if previous_candidates and previous_keywords:
            iteration_data = {
                "timestamp": datetime.now().isoformat(),
                "keywords": previous_keywords,
                "location": previous_location,
                "candidates_count": len(previous_candidates),
                "top_candidates": [
                    {
                        "name": c.get("name", "Unknown"),
                        "match_score": c.get("match_score", 0),
                        "matched_skills": c.get("matched_must_have", []) + c.get("matched_should_have", [])
                    }
                    for c in self.get_top_candidates(previous_candidates, top_n=3)
                ]
            }
            iteration_history.append(iteration_data)
            
            # Log iteration statistics
            self.logger.info(f"Iteration {len(iteration_history)} completed with {len(previous_candidates)} candidates found")
            
            if previous_candidates:
                avg_score = sum(c.get("match_score", 0) for c in previous_candidates) / len(previous_candidates)
                self.logger.info(f"Average match score: {avg_score:.2f}")
                
        # Ask user whether to continue iterating
        print("\n" + "="*50)
        print(f"Recruitment Agent - Iteration {len(iteration_history) + 1}")
        print("="*50)
        
        if iteration_history:
            print(f"\nPrevious iteration found {iteration_history[-1]['candidates_count']} candidates")
            if iteration_history[-1]['top_candidates']:
                print("\nTop candidates from previous iteration:")
                for i, c in enumerate(iteration_history[-1]['top_candidates'], 1):
                    skills = ", ".join(c['matched_skills'])
                    print(f"{i}. {c['name']} (Match score: {c['match_score']:.1f}) - Skills: {skills}")
        
        # Get user input
        while True:
            response = input("\nContinue to iterate? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                self.logger.info("User chose to end iterations")
                return False
            else:
                print("Please enter 'y' or 'n'")
        
    def iterate_search(
        self,
        initial_keywords: Dict[str, List[str]],
        initial_location: Optional[str] = None,
        min_results: Optional[int] = None,
        max_iterations: int = 5
    ) -> List[Dict]:
        """
        Perform iterative searches with refinements between iterations
        
        Args:
            initial_keywords: Initial dictionary with must-have, should-have, and wont-have keywords
            initial_location: Initial location to search for candidates
            min_results: Minimum number of results to fetch (overrides config)
            max_iterations: Maximum number of iterations to perform
            
        Returns:
            List of candidate dictionaries from the final iteration
        """
        iteration_history = []
        current_keywords = initial_keywords.copy()
        current_location = initial_location
        current_iteration = 0
        candidates = []
        
        while current_iteration < max_iterations:
            current_iteration += 1
            self.logger.info(f"\nStarting iteration {current_iteration} of {max_iterations}")
            
            # Perform search
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_file = f"data/candidates_iteration_{current_iteration}_{date_str}.json"
            candidates = self.search_candidates(
                current_keywords,
                location=current_location,
                min_results=min_results,
                output_file=output_file
            )
            
            # Print summary
            self.print_candidates_summary(candidates)
            
            # Ask whether to continue
            if not self.continue_iteration(
                previous_candidates=candidates,
                previous_keywords=current_keywords,
                previous_location=current_location,
                iteration_history=iteration_history
            ):
                self.logger.info("Iteration process ended by user")
                break
                
            # Get refined search parameters for next iteration
            print("\nRefine search parameters for next iteration:")
            
            # Allow refinement of must-have keywords
            print("\nCurrent must-have keywords:", ", ".join(current_keywords.get("must-have", [])))
            new_must_have = input("Enter new must-have keywords (comma-separated, leave empty to keep current): ").strip()
            if new_must_have:
                current_keywords["must-have"] = [k.strip() for k in new_must_have.split(",") if k.strip()]
                
            # Allow refinement of should-have keywords
            print("\nCurrent should-have keywords:", ", ".join(current_keywords.get("should-have", [])))
            new_should_have = input("Enter new should-have keywords (comma-separated, leave empty to keep current): ").strip()
            if new_should_have:
                current_keywords["should-have"] = [k.strip() for k in new_should_have.split(",") if k.strip()]
                
            # Allow refinement of wont-have keywords
            print("\nCurrent won't-have keywords:", ", ".join(current_keywords.get("wont-have", [])))
            new_wont_have = input("Enter new won't-have keywords (comma-separated, leave empty to keep current): ").strip()
            if new_wont_have:
                current_keywords["wont-have"] = [k.strip() for k in new_wont_have.split(",") if k.strip()]
                
            # Allow refinement of location
            print(f"\nCurrent location: {current_location or 'None'}")
            new_location = input("Enter new location (leave empty to keep current): ").strip()
            if new_location:
                current_location = new_location
        
        # Return candidates from final iteration
        return candidates
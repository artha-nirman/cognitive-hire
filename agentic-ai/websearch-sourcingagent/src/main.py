import os
import json
import argparse
import logging
import logging.config
from datetime import datetime
from typing import Dict, List, Optional
import dotenv
import sys
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Now import the local modules
from search_engine import SearchQuery
from llm_parser import LLMFactory
from candidate_scraper import CandidateScraper

# Initialize logger
logger = logging.getLogger('sourcing_agent.main')

def load_config(config_file: str, environment: Optional[str] = None) -> Dict:
    """
    Load configuration from a JSON file with optional environment-specific overrides
    
    Args:
        config_file: Path to the configuration file
        environment: Optional environment name (dev, test, prod)
        
    Returns:
        Dictionary with configuration
    """
    try:
        # Load base configuration
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check for environment-specific config
        if environment:
            env_config_file = config_file.replace('.json', f'.{environment}.json')
            if os.path.exists(env_config_file):
                with open(env_config_file, 'r') as f:
                    env_config = json.load(f)
                # Merge configs, with environment-specific values taking precedence
                config = {**config, **env_config}
                logger.info(f"Loaded environment-specific configuration from {env_config_file}")
        
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_file}: {str(e)}")
        return {}

def save_config(config_file: str, config: Dict) -> None:
    """
    Save configuration to a JSON file
    
    Args:
        config_file: Path to the configuration file
        config: Configuration dictionary
    """
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_file}")
    except Exception as e:
        logger.error(f"Error saving configuration to {config_file}: {str(e)}")

def get_secret(secret_name: str, config: Dict, use_key_vault: bool = False) -> Optional[str]:
    """
    Get a secret from environment variables, config, or Azure Key Vault
    
    Args:
        secret_name: Name of the secret to retrieve
        config: Configuration dictionary
        use_key_vault: Whether to attempt to retrieve from Azure Key Vault
        
    Returns:
        Secret value or None if not found
    """
    # First check environment variables
    env_value = os.getenv(secret_name.upper())
    if env_value:
        return env_value
        
    # Next check config
    config_value = config.get(secret_name.lower())
    if config_value:
        return config_value
    
    # Finally, check Azure Key Vault if enabled
    if use_key_vault and config.get('use_key_vault', False):
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
            
            key_vault_url = config.get('key_vault_url')
            if not key_vault_url:
                logger.error("Azure Key Vault URL not specified in configuration")
                return None
                
            credential = DefaultAzureCredential()
            secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
            
            # Transform the secret name to match Key Vault naming conventions
            # Key Vault secret names can only contain alphanumeric characters and dashes
            key_vault_secret_name = secret_name.lower().replace('_', '-')
            
            try:
                retrieved_secret = secret_client.get_secret(key_vault_secret_name)
                logger.info(f"Retrieved secret {secret_name} from Azure Key Vault")
                return retrieved_secret.value
            except Exception as e:
                logger.error(f"Failed to retrieve secret {secret_name} from Azure Key Vault: {str(e)}")
                return None
        except ImportError:
            logger.warning("Azure SDK not installed. Cannot retrieve secrets from Key Vault.")
            return None
    
    return None

def validate_keywords(keywords: Dict[str, List[str]]) -> bool:
    """
    Validate that keywords dictionary has the required structure
    
    Args:
        keywords: Dictionary with must-have, should-have, and wont-have keywords
        
    Returns:
        True if keywords are valid, False otherwise
    """
    # Check if at least one category exists
    if not any(k in keywords for k in ['must-have', 'should-have', 'wont-have']):
        logger.error("Keywords must include at least one of 'must-have', 'should-have', or 'wont-have'")
        return False
    
    # Check if 'must-have' is empty
    if 'must-have' not in keywords or not keywords['must-have']:
        logger.error("'must-have' keywords are required")
        return False
    
    # Ensure all values are lists
    for key, value in keywords.items():
        if not isinstance(value, list):
            logger.error(f"'{key}' must be a list of strings")
            return False
    
    return True

def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the main module
    
    Args:
        log_level: Default logging level
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Default logging configuration if not already configured
    if not logging.getLogger().handlers:
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
                },
                'sourcing_agent.main': {
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                }
            }
        }
        
        # Apply the configuration
        logging.config.dictConfig(logging_config)

def search_candidates(
    keywords: Dict[str, List[str]],
    location: Optional[str] = None,
    llm_type: Optional[str] = None,
    llm_params: Optional[Dict] = None,
    min_results: int = 20,
    output_file: Optional[str] = None,
    config_file: str = "config/config.json"
) -> List[Dict]:
    """
    Search for candidates based on keywords and location
    
    Args:
        keywords: Dictionary with must-have, should-have, and wont-have keywords
        location: Location to search for candidates
        llm_type: Type of LLM to use ('llama', 'ollama', 'anthropic', or 'openai')
        llm_params: Parameters for the LLM
        min_results: Minimum number of results to fetch
        output_file: Path to output file (default: data/candidates_YYYY-MM-DD.json)
        config_file: Path to configuration file
        
    Returns:
        List of candidate dictionaries
    """
    # Configure logging
    configure_logging()
    
    # Validate keywords
    if not validate_keywords(keywords):
        return []
    
    # Load environment variables
    dotenv.load_dotenv()
    
    # Load configuration
    config = load_config(config_file)
    
    # Get API keys from config or environment
    google_api_key = get_secret('google_api_key', config, use_key_vault=True)
    google_cse_id = get_secret('google_cse_id', config, use_key_vault=True)
    
    if not google_api_key or not google_cse_id:
        logger.error("Google API key and Custom Search Engine ID are required")
        return []
    
    # Create search engine
    search_engine = SearchQuery(
        api_key=google_api_key,
        custom_search_id=google_cse_id,
        min_results=min_results
    )
    
    # Execute search
    logger.info(f"Searching for candidates with the following keywords:")
    logger.info(f"Must have: {', '.join(keywords.get('must-have', []))}")
    if 'should-have' in keywords:
        logger.info(f"Should have: {', '.join(keywords.get('should-have', []))}")
    if 'wont-have' in keywords:
        logger.info(f"Won't have: {', '.join(keywords.get('wont-have', []))}")
    if location:
        logger.info(f"Location: {location}")
    
    search_results = search_engine.execute_search(keywords, location=location)
    
    if not search_results:
        logger.warning("No search results found")
        return []
    
    logger.info(f"Found {len(search_results)} search results")
    
    # Determine which LLM to use
    if llm_type is None:
        llm_type = os.getenv('LLM_TYPE', 'openai').lower()
        logger.info(f"Using LLM type from environment: {llm_type}")
    
    # Setup LLM
    llm_params = llm_params or {}
    
    try:
        # For Llama, set API parameters to use Ollama API
        if llm_type == 'llama':
            logger.info("Note: Using Llama model via Ollama API")
            if 'api_url' not in llm_params:
                llm_params['api_url'] = config.get('ollama_api_url') or os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
            if 'model_name' not in llm_params:
                llm_params['model_name'] = config.get('ollama_model_name') or os.getenv('OLLAMA_MODEL_NAME', 'llama3')
                
        # For Ollama, set API URL and model name if not provided
        elif llm_type == 'ollama':
            if 'api_url' not in llm_params:
                llm_params['api_url'] = config.get('ollama_api_url') or os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
            if 'model_name' not in llm_params:
                llm_params['model_name'] = config.get('ollama_model_name') or os.getenv('OLLAMA_MODEL_NAME', 'llama3')
        
        # For OpenAI, set API key if not provided
        elif llm_type == 'openai':
            if 'api_key' not in llm_params:
                llm_params['api_key'] = get_secret('openai_api_key', config, use_key_vault=True)
                if not llm_params['api_key']:
                    logger.error("OpenAI API key is required. Set OPENAI_API_KEY in .env or provide via --openai-api-key")
                    return []
        
        # For Anthropic, set API key if not provided
        elif llm_type == 'anthropic':
            if 'api_key' not in llm_params:
                llm_params['api_key'] = get_secret('anthropic_api_key', config, use_key_vault=True)
                if not llm_params['api_key']:
                    logger.error("Anthropic API key is required. Set ANTHROPIC_API_KEY in .env or provide via --anthropic-api-key")
                    return []
        
        logger.info(f"Initializing {llm_type.capitalize()} LLM...")
        llm = LLMFactory.create_llm(llm_type, **llm_params)
        
        # Check if Ollama server is available, if not, try to use OpenAI as fallback
        if (llm_type == 'ollama' or llm_type == 'llama') and hasattr(llm, 'server_available') and not llm.server_available:
            logger.warning("Ollama server is not available. Attempting to fall back to OpenAI...")
            
            # Check if OpenAI API key is available
            openai_api_key = get_secret('openai_api_key', config, use_key_vault=True)
            if openai_api_key:
                llm_type = 'openai'
                llm = LLMFactory.create_llm('openai', api_key=openai_api_key)
                logger.info("Successfully switched to OpenAI as fallback LLM provider.")
            else:
                logger.error("No OpenAI API key available for fallback. Please provide an API key or start the Ollama server.")
                return []
        
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        logger.debug(f"LLM type: {llm_type}, Parameters: {llm_params}")
        return []
    
    # Create scraper
    scraper = CandidateScraper(llm=llm)
    
    # Extract candidates
    logger.info("Extracting candidate information from search results...")
    candidates = scraper.extract_candidates_from_search_results(search_results, keywords)
    
    # Match skills
    logger.info("Matching candidate skills to required skills...")
    for candidate in candidates:
        candidate = scraper.match_skills(candidate, keywords)
    
    # Sort candidates by match score
    candidates.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    # Save candidates
    if output_file is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_file = f"data/candidates_{date_str}.log"
    
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    scraper.save_candidates(candidates, output_file)
    
    return candidates

def main():
    # Configure logging
    configure_logging()
    
    parser = argparse.ArgumentParser(description='Recruitment Agent for Candidate Sourcing')
    
    # Define command line arguments
    parser.add_argument('--must-have', nargs='+', help='List of must-have keywords', required=True)
    parser.add_argument('--should-have', nargs='+', help='List of should-have keywords')
    parser.add_argument('--wont-have', nargs='+', help='List of won\'t-have keywords')
    parser.add_argument('--location', help='Location to search for candidates')
    parser.add_argument('--llm', choices=['llama', 'ollama', 'anthropic', 'openai'], 
                        help='LLM to use for parsing (default: from .env file)')
    parser.add_argument('--llama-model-path', help='Path to Llama model file (if using Llama)')
    parser.add_argument('--ollama-api-url', help='Ollama API URL (if using Ollama)')
    parser.add_argument('--ollama-model-name', help='Ollama model name (if using Ollama)')
    parser.add_argument('--openai-api-key', help='OpenAI API key (if using OpenAI)')
    parser.add_argument('--anthropic-api-key', help='Anthropic API key (if using Anthropic)')
    parser.add_argument('--min-results', type=int, default=100, 
                        help='Minimum number of results to fetch (default: 100)')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--config', default='config/config.json', help='Configuration file path')
    parser.add_argument('--log-level', default='INFO', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level (default: INFO)')
    parser.add_argument('--environment', help='Environment name (dev, test, prod)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging with the specified level
    configure_logging(args.log_level)
    
    # Load the configuration file
    config = load_config(args.config, environment=args.environment)
    
    # Create keywords dictionary
    keywords = {'must-have': args.must_have}
    if args.should_have:
        keywords['should-have'] = args.should_have
    if args.wont_have:
        keywords['wont-have'] = args.wont_have
    
    # Use min_results from config if not explicitly specified in command line
    if args.min_results == 100:  # This is the default value
        args.min_results = config.get('min_results', 100)
    
    # Set up LLM parameters based on command-line arguments
    llm_params = {}
    if args.llm == 'llama' and args.llama_model_path:
        llm_params['model_path'] = args.llama_model_path
    elif args.llm == 'ollama':
        if args.ollama_api_url:
            llm_params['api_url'] = args.ollama_api_url
        if args.ollama_model_name:
            llm_params['model_name'] = args.ollama_model_name
    elif args.llm == 'openai' and args.openai_api_key:
        llm_params['api_key'] = args.openai_api_key
    elif args.llm == 'anthropic' and args.anthropic_api_key:
        llm_params['api_key'] = args.anthropic_api_key
    
    # Call search_candidates function
    candidates = search_candidates(
        keywords=keywords,
        location=args.location,
        llm_type=args.llm,
        llm_params=llm_params,
        min_results=args.min_results,
        output_file=args.output,
        config_file=args.config
    )
    
    # Print summary
    logger.info(f"\nSummary: Found {len(candidates)} potential candidates")
    if candidates:
        logger.info(f"Top 3 candidates by match score:")
        for i, candidate in enumerate(candidates[:3], 1):
            name = candidate.get('name', 'Unknown')
            skills = ', '.join(candidate.get('matched_must_have', []))
            score = candidate.get('match_score', 0)
            logger.info(f"{i}. {name} (Match score: {score:.1f}) - Matched skills: {skills}")

if __name__ == '__main__':
    main()
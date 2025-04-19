import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import requests
import re

# LLM base class for implementing different LLM providers
class BaseLLM(ABC):
    @abstractmethod
    def parse_candidate_data(self, content: str, keywords: Dict[str, List[str]]) -> Dict:
        """
        Parse content to extract candidate information
        
        Args:
            content: The text content to parse
            keywords: Dictionary containing must-have, should-have keywords
            
        Returns:
            Dictionary with extracted candidate information
        """
        pass
    
    def generate_extraction_prompt(self, content: str, keywords: Dict[str, List[str]], max_content_tokens: int = 3600) -> str:
        """
        Generate a common prompt for candidate information extraction across all LLM providers
        
        Args:
            content: The text content to parse
            keywords: Dictionary containing must-have, should-have keywords
            max_content_tokens: Maximum number of tokens for content
            
        Returns:
            A formatted prompt string
        """
        # Combine keywords for context
        must_have = ", ".join(keywords.get('must-have', []))
        should_have = ", ".join(keywords.get('should-have', []))
        
        # Truncate content if needed - very rough estimation: 1 token ≈ 4 characters
        char_limit = max_content_tokens * 3
        if len(content) > char_limit:
            content = content[:char_limit] + "\n\n[Content truncated due to length limits]"
        
        # Create prompt for extraction with specific attention to names and skills
        prompt = f"""
        You are an AI assistant tasked with extracting candidate information from provided content. You will be given a set of must-have skills, should-have skills, and content to analyze. Your goal is to extract specific information and present it in a JSON format.

        Here are the inputs you will be working with:

        <must_have_skills>
        {must_have}
        </must_have_skills>

        <should_have_skills>
        {should_have}
        </should_have_skills>

        <content_to_analyze>
        {content}
        </content_to_analyze>

        Your task is to extract the following information from the content, if available:

        1. Full Name: Look for names in the title or prominent locations.
        2. Email Address
        3. Phone Number
        4. LinkedIn URL or other profile URL
        5. Skills that match the keywords provided in must-have and should-have skills
        6. Current Company and Role
        7. Years of Experience
        8. Education

        When extracting skills, be thorough and pay special attention to:
        - Skills mentioned in certifications, courses, or project sections
        - Keywords that match or are similar to the must-have and should-have skills provided
        - Certifications like "Machine Learning with Python" that may indicate relevant skills

        If any field is not found in the content, mark it as "Not found" (including the quotes) in the JSON output.

        Your entire response must be a valid, parseable JSON object. Do not include any explanatory text, markdown formatting, or code blocks. The JSON object should begin with {{ and end with }}.

        The JSON object should have the following structure:

        {{
        "full_name": "",
        "email": "",
        "phone": "",
        "profile_url": "",
        "skills": [],
        "current_company": "",
        "current_role": "",
        "years_of_experience": "",
        "education": ""
        }}

        Remember to be thorough in your search for skills, and include any relevant skills found in the content that match or are similar to the must-have and should-have skills provided.
        """
        
        return prompt

# Implementation for Ollama API (Llama running in Docker)
class OllamaLLM(BaseLLM):
    def __init__(self, api_url: str, model_name: str = "llama3.2"):
        """
        Initialize the Ollama LLM
        
        Args:
            api_url: URL of the Ollama API (e.g., http://localhost:11434)
            model_name: Name of the model to use (e.g., llama3)
        """
        self.api_url = api_url.rstrip('/')
        self.model_name = model_name
        self.generate_endpoint = f"{self.api_url}/api/generate"
        self.server_available = False
        
        # Test connection
        try:
            self._test_connection()
            self.server_available = True
            print(f"Successfully connected to Ollama API at {self.api_url}")
            
            # Check if the model is available
            self._check_model_availability()
            
        except Exception as e:
            print(f"\n====== OLLAMA SERVER ERROR ======")
            print(f"Could not connect to Ollama API at {self.api_url}: {str(e)}")
            print(f"Please make sure the Ollama server is running. You can start it by:")
            print(f"1. Opening a command prompt/terminal")
            print(f"2. Running the command: ollama serve")
            print(f"3. Wait for the server to start")
            print(f"Alternatively, you can use a different LLM by setting the --llm parameter")
            print(f"====== OLLAMA SERVER ERROR ======\n")
    
    def _test_connection(self):
        """Test the connection to the Ollama API"""
        try:
            response = requests.get(f"{self.api_url}/api/version", timeout=5)
            response.raise_for_status()
            print(f"Ollama version: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"ERROR in _test_connection: {str(e)}")
            raise ConnectionError(f"Failed to connect to Ollama server: {str(e)}")
    
    def _check_model_availability(self):
        """Check if the specified model is available"""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json()
            
            # Check if our model is in the list
            model_available = False
            model_name_lower = self.model_name.lower()
            
            if "models" in models:
                for model in models["models"]:
                    if model_name_lower in model["name"].lower():
                        model_available = True
                        break
            
            if not model_available:
                print(f"Warning: Model '{self.model_name}' may not be available. Available models are:")
                if "models" in models:
                    for model in models["models"]:
                        print(f"  - {model['name']}")
                else:
                    print("  No models found")
                print(f"You may need to pull the model first using 'ollama pull {self.model_name}'")
        except Exception as e:
            print(f"Warning: Could not check model availability: {str(e)}")
    
    def _truncate_content(self, content: str, max_tokens: int = 1600) -> str:
        """
        Truncate content to fit within token limits for the model
        
        Args:
            content: The text content to truncate
            max_tokens: Maximum number of tokens to allow
            
        Returns:
            Truncated content
        """
        # More accurate token estimation: 1 token ≈ 4 characters for English text
        char_limit = max_tokens * 3
        
        if len(content) <= char_limit:
            return content
        
        # If content is too long, use a more sophisticated truncation
        # First prioritize sections likely to contain skills information
        skill_sections = [
            "skills", "technical skills", "technologies", "programming languages",
            "certifications", "qualifications", "expertise", "competencies"
        ]
        
        lines = content.split('\n')
        skill_content = []
        other_content = []
        
        # Categorize content lines
        for line in lines:
            line_lower = line.lower()
            if any(section in line_lower for section in skill_sections):
                # Grab this line and the next 5 lines
                idx = lines.index(line)
                skill_content.extend(lines[idx:min(idx+6, len(lines))])
            else:
                other_content.append(line)
        
        # Combine prioritized content
        prioritized_content = "\n".join(skill_content)
        remaining_space = char_limit - len(prioritized_content)
        
        if remaining_space > 0:
            # Add as much of the other content as will fit
            other_text = "\n".join(other_content)
            added_text = other_text[:remaining_space]
            result = prioritized_content + "\n\n" + added_text
        else:
            # If no space remains, truncate the prioritized content
            result = prioritized_content[:char_limit]
        
        return result + "\n\n[Content truncated due to length limits]"
    
    def parse_candidate_data(self, content: str, keywords: Dict[str, List[str]]) -> Dict:
        """
        Parse content using Ollama API to extract candidate information
        
        Args:
            content: The text content to parse
            keywords: Dictionary containing must-have, should-have keywords
            
        Returns:
            Dictionary with extracted candidate information
        """
        # Check if server is available before making API calls
        if not self.server_available:
            return {
                "error": "Ollama server is not available. Please start the server or use a different LLM.",
                "raw_response": ""
            }
        
        # Truncate content more aggressively to ensure it fits within model context
        truncated_content = self._truncate_content(content, max_tokens=3000)
        
        # Use the common prompt generator with a smaller content length for better performance
        prompt = self.generate_extraction_prompt(truncated_content, keywords, max_content_tokens=3000)
        
        # Send request to Ollama API
        try:
            # API payload for /api/generate endpoint with reduced context window for better performance
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "options": {
                    "num_ctx": 4096  # Reduced context window for better performance
                },
                "system": "You are an expert AI assistant that helps extract structured information from text content about job candidates. You must ONLY respond with a valid JSON object, with no explanations or additional text. Do not use markdown code blocks. The entire response must be a valid JSON object that can be parsed directly."
            }
            
            # Print minimal debug information
            print(f"Sending request to Ollama API with {len(truncated_content)} chars of content")
            
            # Use a shorter timeout for first attempt
            try:
                response = requests.post(self.generate_endpoint, json=payload, timeout=60)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                print("First attempt timed out after 60s, retrying with smaller context...")
                # Reduce context further on timeout
                payload["options"]["num_ctx"] = 2048
                truncated_content = self._truncate_content(content, max_tokens=1500)
                prompt = self.generate_extraction_prompt(truncated_content, keywords, max_content_tokens=1500)
                payload["prompt"] = prompt
                print(f"Retrying with reduced context: {len(truncated_content)} chars")
                response = requests.post(self.generate_endpoint, json=payload, timeout=180)
                response.raise_for_status()
            
            result = response.json()
            result_text = result.get('response', '')
            
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "error": "Failed to extract valid JSON response",
                    "raw_response": result_text[:200] + "..." if len(result_text) > 200 else result_text
                }
        except requests.exceptions.HTTPError as http_err:
            print(f"ERROR in parse_candidate_data: HTTP Error with Ollama API: {http_err}")
            print(f"Response: {http_err.response.text if hasattr(http_err, 'response') else 'No response text'}")
            return {
                "error": f"HTTP Error with Ollama API: {http_err}",
                "raw_response": ""
            }
        except requests.exceptions.ConnectionError as conn_err:
            print(f"ERROR in parse_candidate_data: Connection Error with Ollama API: {conn_err}")
            return {
                "error": f"Connection Error with Ollama API: {conn_err}",
                "raw_response": ""
            }
        except requests.exceptions.Timeout as timeout_err:
            print(f"ERROR in parse_candidate_data: Ollama API timeout after 180 seconds: {timeout_err}")
            print("Consider using a smaller model, reducing context size, or using a cloud-based LLM")
            return {
                "error": "Ollama API timeout - model inference is taking too long",
                "raw_response": ""
            }
        except Exception as e:
            print(f"ERROR in parse_candidate_data: Error with Ollama API request: {str(e)}")
            return {
                "error": f"Error with Ollama API: {str(e)}",
                "raw_response": ""
            }

# Implementation for Anthropic Claude
class AnthropicLLM(BaseLLM):
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the Anthropic Claude LLM without using the Anthropic library
        
        Args:
            api_key: Anthropic API key
            **kwargs: Additional arguments (ignored for compatibility)
        """
        self.api_key = api_key
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-opus-20240229"  # Can be updated to latest model
        
        # Headers for Anthropic API requests - using newer authentication format
        self.headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Check if the API key format is the newer style (starting with sk-ant-)
        if api_key.startswith('sk-ant-'):
            self.headers["x-api-key"] = self.api_key
            print("Using x-api-key authentication header for Anthropic API")
        else:
            # Use the Authorization header format for newer Anthropic API
            self.headers["Authorization"] = f"Bearer {self.api_key}"
            print("Using Bearer token authentication header for Anthropic API")
        
        # Log any ignored parameters for debugging
        ignored_params = [k for k in kwargs.keys() if k not in ['api_key']]
        if ignored_params:
            print(f"Warning: The following parameters were ignored by the AnthropicLLM: {', '.join(ignored_params)}")
            
        print(f"Initialized Anthropic API client with model: {self.model}")
    
    def parse_candidate_data(self, content: str, keywords: Dict[str, List[str]]) -> Dict:
        """
        Parse content using Anthropic Claude API to extract candidate information
        
        Args:
            content: The text content to parse
            keywords: Dictionary containing must-have, should-have keywords
            
        Returns:
            Dictionary with extracted candidate information
        """
        # Use the common prompt generator with Claude's higher token limit
        prompt = self.generate_extraction_prompt(content, keywords, max_content_tokens=10000)
        
        try:
            # Build request payload for Anthropic API
            payload = {
                "model": self.model,
                "max_tokens": 1024,
                "temperature": 0.1,
                "system": "You are an expert AI assistant that helps extract structured information from text content about job candidates. Always respond with a valid JSON object.",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Make direct API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120  # Allow 2 minutes for completion
            )
            response.raise_for_status()
            
            # Parse the response JSON
            result = response.json()
            
            if "content" in result and len(result["content"]) > 0:
                result_text = result["content"][0]["text"]
                
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result_text[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    return {
                        "error": "Failed to extract valid JSON response",
                        "raw_response": result_text[:200] + "..." if len(result_text) > 200 else result_text
                    }
            else:
                return {
                    "error": "Invalid response format from Anthropic API",
                    "raw_response": str(result)
                }
                
        except requests.exceptions.HTTPError as http_err:
            print(f"ERROR in AnthropicLLM.parse_candidate_data: HTTP Error: {http_err}")
            print(f"Response: {http_err.response.text if hasattr(http_err, 'response') else 'No response text'}")
            return {
                "error": f"HTTP Error with Anthropic API: {http_err}",
                "raw_response": http_err.response.text if hasattr(http_err, 'response') else ""
            }
        except requests.exceptions.Timeout as timeout_err:
            print(f"ERROR in AnthropicLLM.parse_candidate_data: Anthropic API timeout after 120 seconds: {timeout_err}")
            return {
                "error": "Anthropic API timeout - request took too long",
                "raw_response": ""
            }
        except Exception as e:
            print(f"ERROR in AnthropicLLM.parse_candidate_data: {str(e)}")
            return {
                "error": f"Error with Anthropic API: {str(e)}",
                "raw_response": ""
            }

# Implementation for OpenAI GPT
class OpenAILLM(BaseLLM):
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the OpenAI GPT LLM without using the OpenAI library
        
        Args:
            api_key: OpenAI API key
            **kwargs: Additional arguments (ignored for compatibility)
        """
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4-turbo"  # Can be updated to latest model
        
        # Headers for OpenAI API requests
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Log any ignored parameters for debugging
        ignored_params = [k for k in kwargs.keys() if k not in ['api_key']]
        if ignored_params:
            print(f"Warning: The following parameters were ignored by the OpenAILLM: {', '.join(ignored_params)}")
    
    def parse_candidate_data(self, content: str, keywords: Dict[str, List[str]]) -> Dict:
        """
        Parse content using OpenAI GPT API to extract candidate information
        
        Args:
            content: The text content to parse
            keywords: Dictionary containing must-have, should-have keywords
            
        Returns:
            Dictionary with extracted candidate information
        """
        # Use the common prompt generator with GPT-4's token limit
        prompt = self.generate_extraction_prompt(content, keywords, max_content_tokens=8000)
        
        try:
            # Build request payload for OpenAI API
            payload = {
                "model": self.model,
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "You are an expert AI assistant that helps extract structured information from text content about job candidates. Always respond with a valid JSON object."},
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Make direct API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120  # Allow 2 minutes for completion
            )
            response.raise_for_status()
            
            # Parse the response JSON
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                result_text = result["choices"][0]["message"]["content"]
                return json.loads(result_text)
            else:
                return {
                    "error": "Invalid response format from OpenAI API",
                    "raw_response": str(result)
                }
                
        except requests.exceptions.HTTPError as http_err:
            print(f"ERROR in OpenAILLM.parse_candidate_data: HTTP Error: {http_err}")
            print(f"Response: {http_err.response.text if hasattr(http_err, 'response') else 'No response text'}")
            return {
                "error": f"HTTP Error with OpenAI API: {http_err}",
                "raw_response": http_err.response.text if hasattr(http_err, 'response') else ""
            }
        except requests.exceptions.Timeout as timeout_err:
            print(f"ERROR in OpenAILLM.parse_candidate_data: OpenAI API timeout after 120 seconds: {timeout_err}")
            return {
                "error": "OpenAI API timeout - request took too long",
                "raw_response": ""
            }
        except Exception as e:
            print(f"ERROR in OpenAILLM.parse_candidate_data: {str(e)}")
            return {
                "error": f"Error with OpenAI API: {str(e)}",
                "raw_response": ""
            }

# LLM Factory to create appropriate LLM instance
class LLMFactory:
    @staticmethod
    def create_llm(llm_type: str, **kwargs) -> BaseLLM:
        """
        Create and return an LLM instance based on the specified type
        
        Args:
            llm_type: Type of LLM to create ('llama', 'ollama', 'anthropic', or 'openai')
            **kwargs: Additional arguments for the LLM constructor
            
        Returns:
            An instance of BaseLLM
            
        Raises:
            ValueError: If llm_type is not supported
        """
        if llm_type.lower() == 'llama':
            # For 'llama' type, we use OllamaLLM with the llama model
            print("Using Llama model via Ollama API")
            return OllamaLLM(
                api_url=kwargs.get('api_url', 'http://localhost:11434'),
                model_name=kwargs.get('model_name', 'llama3')
            )
        elif llm_type.lower() == 'ollama':
            return OllamaLLM(
                api_url=kwargs.get('api_url', 'http://localhost:11434'),
                model_name=kwargs.get('model_name', 'llama3')
            )
        elif llm_type.lower() == 'anthropic':
            # Pass all kwargs to AnthropicLLM - it will handle filtering out unsupported parameters
            return AnthropicLLM(**kwargs)
        elif llm_type.lower() == 'openai':
            return OpenAILLM(api_key=kwargs.get('api_key'))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
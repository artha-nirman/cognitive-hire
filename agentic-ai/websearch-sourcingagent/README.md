# Web Search Sourcing Agent

An AI-powered sourcing agent that automatically discovers and evaluates potential job candidates by searching the web and analyzing their online profiles.

## Overview

The Web Search Sourcing Agent is an intelligent tool designed to automate the initial candidate sourcing process for recruiters. It uses Google's Custom Search API to find potential candidates based on specific skills and location criteria, then leverages AI language models to parse and analyze the candidate information.

Key features:

- Automated web search for candidates with specific skills and qualifications
- Support for must-have, should-have, and won't-have skill requirements
- Location-based filtering
- AI-powered extraction of candidate information from web pages
- Special handling for LinkedIn profiles
- Skill matching and candidate scoring
- Multiple LLM support (OpenAI, Anthropic Claude, Llama, Ollama)
- Integration with Azure Key Vault for secure credential management

## Installation

### Prerequisites

- Python 3.8+
- Google API key and Custom Search Engine ID
- (Optional) OpenAI API key, Anthropic API key, or Ollama server

### Setup

1. Create a Python virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a configuration file:
   ```
   mkdir -p config
   cp config/config.json.example config/config.json
   ```

5. Edit `config/config.json` to add your API keys and configuration.

## Configuration

You need to configure the following:

1. Create a `.env` file in the root directory with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_custom_search_engine_id
   OPENAI_API_KEY=your_openai_api_key  # Optional
   ANTHROPIC_API_KEY=your_anthropic_api_key  # Optional
   ```

2. Alternatively, edit the `config/config.json` file with your settings:
   ```json
   {
     "google_api_key": "your_google_api_key",
     "google_cse_id": "your_custom_search_engine_id",
     "openai_api_key": "your_openai_api_key",
     "anthropic_api_key": "your_anthropic_api_key",
     "ollama_api_url": "http://localhost:11434",
     "ollama_model_name": "llama3",
     "min_results": 50,
     "use_key_vault": false
   }
   ```

3. Azure Integration (Optional):
   To use Azure Key Vault for secure credential storage, set `use_key_vault` to `true` and provide the `key_vault_url` in your config file. Make sure the Azure SDK dependencies are installed.

## Usage

### Running with the Batch File

The simplest way to run the agent is using the included batch file:

```
run_agent.bat --must-have "python developer" "cloud experience" --should-have "Azure" "DevOps" --location "United States"
```

### Command Line Options

You can run the agent with the following command-line options:

```
python -m src.main --must-have KEYWORD1 KEYWORD2 [--should-have KEYWORD3 KEYWORD4] [--wont-have KEYWORD5 KEYWORD6] [--location LOCATION] [--llm MODEL] [--min-results NUM] [--output FILE]
```

Required arguments:
- `--must-have`: List of required skills (space-separated)

Optional arguments:
- `--should-have`: List of preferred skills (space-separated)
- `--wont-have`: List of skills to exclude (space-separated)
- `--location`: Geographic location to search for candidates
- `--llm`: LLM to use for parsing (`llama`, `ollama`, `anthropic`, `openai`)
- `--min-results`: Minimum number of search results to process (default: 100)
- `--output`: Custom output file path
- `--config`: Configuration file path (default: config/config.json)
- `--log-level`: Logging level (default: INFO)
- `--environment`: Environment name for config (dev, test, prod)
- `--openai-api-key`: OpenAI API key (if using OpenAI)
- `--anthropic-api-key`: Anthropic API key (if using Anthropic)
- `--ollama-api-url`: Ollama API URL (if using Ollama)
- `--ollama-model-name`: Ollama model name (if using Ollama)

### Examples

Search for Python developers with cloud experience and preferably Azure knowledge:
```
python -m src.main --must-have "Python developer" "cloud experience" --should-have "Azure" "DevOps" --location "United States"
```

Search for data scientists with machine learning skills:
```
python -m src.main --must-have "data scientist" "machine learning" --should-have "Python" "TensorFlow" --wont-have "junior" "intern" --location "Remote"
```

Use a specific LLM:
```
python -m src.main --must-have "frontend developer" "React" --llm openai --min-results 50
```

## Output

The agent saves the results in the following files:

- `data/candidates_YYYY-MM-DD.log`: JSON file containing candidate information for the current date
- `logs/sourcing_agent.log`: Detailed log of the agent's actions
- `logs/linkedin_access_failures.log`: Record of LinkedIn profiles that couldn't be accessed fully

Each candidate entry includes:
- Name (when available)
- Source URL
- Matched skills
- Match score (weighted based on must-have and should-have matches)
- Other extracted information (when available)

## LLM Support

The agent supports multiple language models:

1. **OpenAI GPT**: Requires an OpenAI API key
2. **Anthropic Claude**: Requires an Anthropic API key
3. **Llama/Ollama**: Uses the Ollama API (requires a local Ollama server)

The default is specified in your config or .env file. You can override it with the `--llm` parameter.

## Troubleshooting

- **Ollama Server Issues**: If using Llama or Ollama and the server is not available, the agent will attempt to fall back to OpenAI if an API key is available.
- **LinkedIn Access**: Due to LinkedIn's access restrictions, full profile data may not always be available. The agent creates fallback entries with partial information in these cases.
- **API Keys**: Ensure your API keys are correctly set in your .env file or config.json.
- **Logs**: Check the logs directory for detailed error information.

## License

This project is proprietary software owned by Cognitive Hire. All rights reserved.
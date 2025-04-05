#!/usr/bin/env python
"""
Environment Setup Script

This script securely fetches development secrets from Azure Key Vault 
and creates appropriate .env files for local development.

Requirements:
- Azure CLI installed and logged in
- Appropriate access to the development Key Vault

Usage:
    python setup-env.py --service recruitment
"""

import argparse
import os
import subprocess
import json
from pathlib import Path
from getpass import getpass

# Configuration
KEY_VAULT_NAME = "cognitivehire-dev-kv"
SERVICES = {
    "recruitment": {
        "path": "backend/recruitment-service/.env",
        "secrets": [
            "AUTH-SECRET-KEY",
            "AZURE-AD-B2C-TENANT-NAME",
            "AZURE-AD-B2C-CLIENT-ID",
            "AZURE-AD-B2C-CLIENT-SECRET",
            "DATABASE-URL"
        ]
    },
    "candidate": {
        "path": "backend/candidate-service/.env",
        "secrets": [
            "AUTH-SECRET-KEY",
            "AZURE-AD-B2C-TENANT-NAME",
            "AZURE-AD-B2C-CLIENT-ID",
            "AZURE-AD-B2C-CLIENT-SECRET",
            "DATABASE-URL"
        ]
    },
    # Add other services as needed
}

def check_azure_login():
    """Check if user is logged in to Azure CLI"""
    try:
        result = subprocess.run(
            ["az", "account", "show"], 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def get_secret_from_keyvault(secret_name):
    """Fetch a secret from Azure Key Vault"""
    try:
        result = subprocess.run(
            ["az", "keyvault", "secret", "show", "--vault-name", KEY_VAULT_NAME, 
             "--name", secret_name, "--query", "value", "-o", "tsv"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error fetching secret {secret_name}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error accessing Key Vault: {str(e)}")
        return None

def create_env_file(service_name):
    """Create .env file for a service from example and Key Vault secrets"""
    service_config = SERVICES.get(service_name)
    if not service_config:
        print(f"Unknown service: {service_name}")
        return False
        
    # Get paths
    service_path = service_config["path"]
    example_path = service_path + ".example"
    
    # Check if example file exists
    if not os.path.exists(example_path):
        print(f"Example file not found: {example_path}")
        return False
        
    # Read example file
    with open(example_path, "r") as f:
        example_content = f.read()
    
    # Replace secrets with actual values
    env_content = example_content
    for secret_name in service_config["secrets"]:
        # Convert from KEY-VAULT-FORMAT to ENV_FILE_FORMAT
        env_var = secret_name.replace("-", "_")
        
        # Get the secret value
        secret_value = get_secret_from_keyvault(secret_name)
        if secret_value:
            # Replace the placeholder with the actual value
            placeholder = f"{env_var}=your-{env_var.lower()}-here"
            env_content = env_content.replace(placeholder, f"{env_var}={secret_value}")
            
    # Write .env file
    with open(service_path, "w") as f:
        f.write(env_content)
        
    print(f"Created .env file for {service_name} with secrets from Key Vault")
    return True

def main():
    parser = argparse.ArgumentParser(description="Set up environment variables for local development")
    parser.add_argument("--service", required=True, help="Service to set up (recruitment, candidate, etc.)")
    args = parser.parse_args()
    
    # Check Azure login
    if not check_azure_login():
        print("You need to log in to Azure CLI first. Run 'az login'")
        return
    
    # Create .env file
    create_env_file(args.service)

if __name__ == "__main__":
    main()

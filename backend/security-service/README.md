# Security Service

This service handles authentication, authorization, and user identity management for the Cognitive Hire platform.

## Architecture

This service implements the Security Framework as described in the [High-Level Design](../../architecture/high-level-design.md), providing:

- Authentication using Azure AD B2C
- Role-based access control
- Permission management
- Development authentication bypass

## Local Development

### Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Azure AD B2C tenant (or local development bypass enabled)

### Setting Up the Python Virtual Environment

#### On Windows

```bash
# Navigate to the security-service directory
cd c:\dev\hire-cognition\cognitive-hire\backend\security-service

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### On Linux/macOS

```bash
# Navigate to the security-service directory
cd /path/to/hire-cognition/cognitive-hire/backend/security-service

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Troubleshooting Installation Issues

#### Rust Dependencies

Some Python packages (like `cryptography` which is a dependency of `python-jose`) require Rust to compile. If you see this error:

```
Cargo, the Rust package manager, is not installed or is not on PATH.
This package requires Rust and Cargo to compile extensions. Install it through
the system's package manager or via https://rustup.rs/
```

Install Rust using one of these methods:

**On Windows:**
1. Download and run the Rust installer from https://rustup.rs/
2. Follow the installation prompts
3. Restart your terminal/command prompt
4. Try installing requirements again

**On Linux/macOS:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

#### Visual Studio Build Tools Issues

If you've installed Rust but encounter MSVC linker errors like:

```
note: the msvc targets depend on the msvc linker but `link.exe` was not found
note: please ensure that Visual Studio 2017 or later, or Build Tools for Visual Studio were installed with the Visual C++ option.
```

Follow these steps to fix it:

1. **Install Visual Studio Build Tools with C++ workload**:
   - Download the Visual Studio Build Tools installer from [Microsoft's website](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Run the installer and select "Desktop development with C++" workload
   - Ensure "MSVC" and "Windows 10 SDK" components are selected
   - Complete the installation

2. **Verify the installation**:
   - Open a new command prompt (you may need to restart your computer)
   - Run `where link.exe` to check if the linker is in the PATH

3. **Reinstall packages with wheel preference**:
   ```bash
   # Upgrade pip
   python -m pip install --upgrade pip
   
   # Install specific problem packages first with binary preference
   pip install --prefer-binary pydantic-core asyncpg
   
   # Then install remaining requirements
   pip install --prefer-binary -r requirements.txt
   ```

#### Alternative: Using Pre-compiled Wheels

If you don't want to install Rust, you can use pre-compiled binary wheels:

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try installing with binary preference
pip install --prefer-binary -r requirements.txt
```

#### Alternative: Use Prebuilt Wheels Repository

If you continue having build issues, try using an alternative PyPI repository that provides prebuilt wheels:

```bash
pip install --index-url https://pypi.org/simple/ --extra-index-url https://www.piwheels.org/simple/ -r requirements.txt
```

### Verifying Installation

After creating and activating the virtual environment, verify that dependencies are installed correctly:

```bash
# Check FastAPI version
python -c "import fastapi; print(fastapi.__version__)"
# Check other key packages
python -c "import uvicorn, sqlalchemy, fastapi_azure_auth; print('Dependencies installed successfully')"
```

### Setup

1. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. Run database migrations:
   ```bash
   alembic upgrade head
   ```

3. Start the service:
   ```bash
   uvicorn app.main:app --reload
   ```

## Configuration

Configuration is managed through environment variables. See `.env.example` for available options.

## Testing

```bash
pytest
```

### Running Tests

To run the test suite:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app

# Run specific test files
pytest tests/services/test_user_service.py

# Run tests with detailed output
pytest -v
```

### Types of Tests

1. **Unit Tests**: Test individual service and utility functions in isolation
   - Location: `tests/services/`
   - Example: `test_user_service.py`

2. **API Tests**: Test API endpoints using FastAPI TestClient
   - Location: `tests/api/`
   - Example: `test_auth_api.py`

3. **Integration Tests**: Test interactions between components
   - Location: `tests/integration/`

### Testing Development Bypass

For local development and testing without real Azure AD B2C, use the development bypass:

```python
# Example API test with auth bypass
headers = {
    "X-Bypass-Auth": "dev-bypass-secret",  # Must match AUTH_BYPASS_SECRET in .env
    "X-Test-User": "admin"  # Options: admin, recruiter, candidate
}
response = client.get("/api/v1/protected-endpoint", headers=headers)
```

### Manual Testing with Swagger UI

When running the service locally, you can use Swagger UI for manual testing:

1. Start the service: `uvicorn app.main:app --reload`
2. Navigate to: http://localhost:8000/docs
3. Click the "Authorize" button to set the Bearer token or bypass headers
4. Test endpoints directly from the UI

For bypass authentication in Swagger UI, set the following headers:
- `X-Bypass-Auth: dev-bypass-secret`
- `X-Test-User: admin`

## API Documentation

When running locally, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

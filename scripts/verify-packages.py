#!/usr/bin/env python
"""Verify that required Python packages are installed correctly."""

import importlib
import sys
import subprocess
from pathlib import Path

# Packages to verify
CRITICAL_PACKAGES = [
    "structlog",
    "fastapi",
    "sqlalchemy",
    "pydantic"
]

def check_package(package_name):
    """Check if a package can be imported."""
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} is installed and importable")
        return True
    except ImportError:
        print(f"❌ {package_name} CANNOT be imported")
        return False

def install_package(package_name):
    """Try to install a package."""
    print(f"🔧 Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main function."""
    print("Checking critical packages...")
    
    failed_packages = []
    for package in CRITICAL_PACKAGES:
        if not check_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print("\n⚠️  Some packages failed to import. Attempting to install them...")
        for package in failed_packages:
            if install_package(package):
                if check_package(package):
                    print(f"✅ {package} was successfully installed and is now importable")
                else:
                    print(f"⚠️ {package} was installed but still can't be imported")
            else:
                print(f"❌ Failed to install {package}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\n✅ Running in a virtual environment")
    else:
        print("\n⚠️ NOT running in a virtual environment. This may cause import issues.")
    
    print(f"\nPython interpreter: {sys.executable}")
    
    # Print Python path
    print("\nPython path:")
    for path in sys.path:
        print(f"  {path}")

if __name__ == "__main__":
    main()

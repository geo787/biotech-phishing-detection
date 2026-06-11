#!/usr/bin/env python3
"""Test if all required dependencies are installed."""

import sys

def check_dependencies():
    """Check all required packages."""
    required_packages = {
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'sklearn': 'scikit-learn',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
    }
    
    missing = []
    print("Checking dependencies...\n")
    
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"✓ {package_name:20} OK")
        except ImportError:
            print(f"✗ {package_name:20} MISSING")
            missing.append(package_name)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    else:
        print("\nAll dependencies installed!")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)

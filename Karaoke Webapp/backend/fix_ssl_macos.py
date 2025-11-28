#!/usr/bin/env python3
"""
Helper script to fix SSL certificate issues on macOS
Run this if you encounter SSL certificate verification errors
"""

import subprocess
import sys
import os

def install_certificates():
    """Install SSL certificates for Python on macOS"""
    print("Attempting to fix SSL certificates...")
    
    # Try to find and run the Install Certificates.command script
    python_path = sys.executable
    python_dir = os.path.dirname(python_path)
    
    # Common locations for the certificate installer
    possible_paths = [
        f"{python_dir}/Install Certificates.command",
        "/Applications/Python 3.12/Install Certificates.command",
        "/Applications/Python 3.11/Install Certificates.command",
        "/Applications/Python 3.10/Install Certificates.command",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found certificate installer at: {path}")
            try:
                subprocess.run([path], check=True)
                print("✅ Certificates installed successfully!")
                return True
            except Exception as e:
                print(f"❌ Error running installer: {e}")
    
    print("⚠️  Could not find certificate installer script.")
    print("You may need to:")
    print("1. Reinstall Python from python.org (not Homebrew)")
    print("2. Or manually install certificates using certifi")
    print("3. Or run: pip install --upgrade certifi")
    
    return False

if __name__ == "__main__":
    install_certificates()


#!/usr/bin/env python3
"""
Python 3.13 Installation Script for Financial Tracker
This script handles the specific compatibility issues with Python 3.13
"""

import sys
import subprocess
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("🐍 Python 3.13 Installation Script for Financial Tracker")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info.minor < 13:
        print("❌ This script is designed for Python 3.13+")
        print(f"   Current version: {sys.version}")
        return
    
    print(f"✅ Python {sys.version} detected")
    print()
    
    # Step 1: Upgrade pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return
    
    # Step 2: Install core packages first (these are usually pre-compiled)
    core_packages = [
        "numpy>=1.26.0",
        "pandas>=2.2.0",
        "flask>=2.3.3",
        "werkzeug>=2.3.7"
    ]
    
    print("\n📦 Installing core packages...")
    for package in core_packages:
        if not run_command(f"{sys.executable} -m pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: Failed to install {package}, continuing...")
    
    # Step 3: Install packages that might need compilation
    print("\n📦 Installing additional packages...")
    additional_packages = [
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
        "plotly>=5.17.0",
        "scikit-learn>=1.4.0",
        "nltk>=3.8.1",
        "pdfplumber>=0.10.0",
        "python-dotenv>=1.0.0",
        "flask-cors>=4.0.0"
    ]
    
    for package in additional_packages:
        if not run_command(f"{sys.executable} -m pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: Failed to install {package}, continuing...")
    
    # Step 4: Test imports
    print("\n🧪 Testing package imports...")
    test_packages = [
        'flask', 'pandas', 'numpy', 'matplotlib', 'seaborn', 
        'plotly', 'scikit-learn', 'nltk', 'pdfplumber'
    ]
    
    failed_imports = []
    for package in test_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError as e:
            print(f"   ❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️  Some packages failed to import: {', '.join(failed_imports)}")
        print("   The application may still work with limited functionality")
    else:
        print("\n✅ All packages imported successfully!")
    
    print("\n🎉 Installation completed!")
    print("\n💡 Next steps:")
    print("   1. Run: python start.py")
    print("   2. Or run: streamlit run streamlit_app.py")
    print("   3. Open browser to: http://localhost:8501")
    
    if failed_imports:
        print(f"\n⚠️  Note: Some packages ({', '.join(failed_imports)}) failed to install.")
        print("   You may need to install Visual Studio Build Tools or use Python 3.11/3.12")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Installation interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...") 
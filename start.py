#!/usr/bin/env python3
"""
Financial Tracker Startup Script
Automatically sets up the environment and starts the application
"""

import sys
import subprocess
import os
import platform

def print_header():
    print("=" * 50)
    print("🏦 Financial Tracker - Smart Spending Insights")
    print("=" * 50)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️  Python 3.13 detected - using compatible package versions")
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # First, upgrade pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install dependencies
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies:")
        print(f"   {e.stderr}")
        
        # Try alternative approach for Python 3.13
        if sys.version_info.minor >= 13:
            print("🔄 Trying alternative installation method for Python 3.13...")
            try:
                # Install core packages individually
                packages = [
                    "streamlit>=1.28.0",
                    "pandas>=2.2.0", 
                    "numpy>=1.26.0",
                    "nltk>=3.8.1",
                    "pdfplumber>=0.10.0",
                    "plotly>=5.17.0",
                    "matplotlib>=3.8.0",
                    "seaborn>=0.13.0",
                    "scikit-learn>=1.4.0",
                    "python-dotenv>=1.0.0",
                    "psutil>=5.9.0",
                    "dask>=2023.1.0",
                    "openpyxl>=3.1.0",
                    "requests>=2.31.0"
                ]
                
                for package in packages:
                    print(f"   Installing {package}...")
                    subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  check=True, capture_output=True)
                
                print("✅ Alternative installation completed!")
                return True
                
            except subprocess.CalledProcessError as e2:
                print(f"❌ Alternative installation also failed: {e2}")
                return False
        
        return False

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'matplotlib', 'seaborn', 
        'plotly', 'scikit-learn', 'nltk', 'pdfplumber'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError as e:
            print(f"   ❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All packages imported successfully!")
    return True

def start_application():
    """Start the Streamlit application"""
    print("🚀 Starting Financial Tracker application...")
    
    try:
        # Check if streamlit_app.py exists
        if not os.path.exists("streamlit_app.py"):
            print("❌ streamlit_app.py not found in current directory")
            return False
        
        # Start the application
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

def main():
    """Main startup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        print("\n💡 Please install Python 3.8+ and try again")
        input("Press Enter to exit...")
        return
    
    print()
    
    # Install dependencies
    if not install_dependencies():
        print("\n💡 Try these solutions:")
        print("   1. Update pip: python -m pip install --upgrade pip")
        print("   2. Install Visual Studio Build Tools (for Windows)")
        print("   3. Use Python 3.11 or 3.12 instead of 3.13")
        print("   4. Try: pip install --only-binary=all -r requirements.txt")
        input("\nPress Enter to exit...")
        return
    
    print()
    
    # Test imports
    if not test_imports():
        print("\n💡 Some packages failed to import. Please check the errors above.")
        input("Press Enter to exit...")
        return
    
    print()
    
    # Start application
    start_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...") 
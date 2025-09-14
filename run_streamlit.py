#!/usr/bin/env python3
"""
Startup script for the Streamlit Financial Tracker
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    # Check each dependency
    dependencies = [
        ("streamlit", "streamlit"),
        ("pandas", "pandas"),
        ("plotly", "plotly"),
        ("scikit-learn", "sklearn"),
        ("nltk", "nltk"),
        ("pdfplumber", "pdfplumber"),
    ]
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            missing_deps.append(package_name)
            print(f"❌ {package_name} is missing")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Installing missing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("\n🔄 Alternative: Try the minimal version:")
            print("   streamlit run streamlit_app_minimal.py")
            return False
    else:
        print("✅ All dependencies are installed")
        return True

def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        print("✅ NLTK data downloaded")
    except Exception as e:
        print(f"⚠️ Warning: Could not download NLTK data: {e}")

def main():
    """Main startup function"""
    print("🚀 Starting Financial Tracker (Streamlit Version)")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("streamlit_app.py").exists():
        print("❌ streamlit_app.py not found. Please run this script from the project directory.")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install requirements manually.")
        return
    
    # Download NLTK data
    download_nltk_data()
    
    # Check for model file
    model_path = Path("models/categorization_model.pkl")
    if not model_path.exists():
        print("⚠️ Warning: Categorization model not found. Some features may not work.")
        print("   Run the training script to create the model.")
    
    print("\n🌐 Starting Streamlit server...")
    print("📱 The app will open in your default web browser")
    print("🔗 If it doesn't open automatically, go to: http://localhost:8501")
    print("\n" + "=" * 60)
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Financial Tracker...")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

if __name__ == "__main__":
    main()

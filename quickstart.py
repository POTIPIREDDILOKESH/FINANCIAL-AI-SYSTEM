"""
Quick start script to initialize and run the system
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10+"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")

def check_dependencies():
    """Check if key dependencies are installed"""
    try:
        import fastapi
        import streamlit
        import sklearn
        import sentence_transformers
        import faiss
        print("✅ All key dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def initialize_data():
    """Ensure data files exist"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    if (data_dir / "transactions.csv").exists():
        print("✅ Transaction data found")
    else:
        print("⚠️  Transaction data not found - will be created on first run")
    
    if (data_dir / "financial_docs.txt").exists():
        print("✅ Financial documents found")
    else:
        print("⚠️  Financial documents not found - will be created on first run")

def run_fastapi():
    """Run FastAPI server"""
    print("\n🚀 Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    os.system(f"{sys.executable} -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000")

def run_streamlit():
    """Run Streamlit app"""
    print("\n🚀 Starting Streamlit app...")
    print("Dashboard will be available at: http://localhost:8501")
    os.system(f"{sys.executable} -m streamlit run frontend/streamlit_app.py")

def main():
    """Main initialization script"""
    print("=" * 60)
    print("   Financial AI System - Quick Start")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Initialize data
    print("\n📁 Initializing data...")
    initialize_data()
    
    # Check dependencies
    print("\n📚 Checking dependencies...")
    if not check_dependencies():
        response = input("\nInstall missing dependencies? (y/n): ").lower()
        if response == 'y':
            install_dependencies()
        else:
            print("Cannot continue without dependencies")
            sys.exit(1)
    
    # Ask user what to run
    print("\n" + "=" * 60)
    print("What would you like to run?")
    print("1. FastAPI backend only")
    print("2. Streamlit frontend only (uses integrated backend)")
    print("3. Both (requires 2 terminals)")
    print("=" * 60)
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        run_fastapi()
    elif choice == "2":
        run_streamlit()
    elif choice == "3":
        print("\n📌 Note: This requires running commands in separate terminals:")
        print("\nTerminal 1:")
        print("python -m uvicorn app.api.main:app --reload")
        print("\nTerminal 2:")
        print("streamlit run frontend/streamlit_app.py")
        input("\nPress Enter to continue...")
    else:
        print("Invalid option")
        sys.exit(1)

if __name__ == "__main__":
    main()

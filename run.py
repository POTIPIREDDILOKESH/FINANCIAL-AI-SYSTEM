#!/usr/bin/env python3
"""
Insurance Claims Predictor - Launcher Script

This script provides convenient commands to run the FastAPI backend and Streamlit frontend.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def check_requirements():
    """Check if required files exist"""
    required_files = [
        "app.py",
        "streamlit_app.py",
        "model.pkl",
        "train.csv",
        "requirements.txt"
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all project files are present.")
        return False

    print("✅ All required files found")
    return True

def run_api():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("Press Ctrl+C to stop\n")

    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 FastAPI server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running FastAPI: {e}")

def run_streamlit():
    """Run the Streamlit application"""
    print("🌟 Starting Streamlit application...")
    print("📍 Web app will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop\n")

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Streamlit application stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")

def run_both():
    """Run both API and Streamlit in parallel"""
    print("🚀 Starting Insurance Claims Predictor...")
    print("📍 FastAPI: http://localhost:8000")
    print("📍 Streamlit: http://localhost:8501")
    print("Press Ctrl+C to stop both applications\n")

    # Start FastAPI in background
    api_process = subprocess.Popen([sys.executable, "app.py"])

    # Wait a moment for API to start
    time.sleep(3)

    try:
        # Start Streamlit in foreground
        streamlit_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping applications...")
    finally:
        # Clean up processes
        try:
            api_process.terminate()
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()

        try:
            streamlit_process.terminate()
            streamlit_process.wait(timeout=5)
        except:
            streamlit_process.kill()

        print("✅ All applications stopped")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def main():
    if len(sys.argv) < 2:
        print("Insurance Claims Predictor - Launcher")
        print("=" * 40)
        print("Usage: python run.py <command>")
        print("\nCommands:")
        print("  install    - Install dependencies")
        print("  api        - Run FastAPI server only")
        print("  web        - Run Streamlit app only")
        print("  both       - Run both API and web app")
        print("  check      - Check if all files are present")
        return

    command = sys.argv[1].lower()

    if command == "check":
        check_requirements()
    elif command == "install":
        install_dependencies()
    elif command == "api":
        if check_requirements():
            run_api()
    elif command == "web":
        if check_requirements():
            run_streamlit()
    elif command == "both":
        if check_requirements():
            run_both()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python run.py' to see available commands")

if __name__ == "__main__":
    main()
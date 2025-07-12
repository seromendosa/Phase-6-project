#!/usr/bin/env python3
"""
Launcher script for the Drug Matching System
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'fuzzywuzzy', 
        'sklearn', 'plotly', 'sqlalchemy', 'psycopg2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'sklearn':
                __import__('sklearn')
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_config():
    """Check if configuration files exist"""
    config_files = ['config.py', 'app.py']
    missing_files = []
    
    for file in config_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def setup_environment():
    """Setup environment variables"""
    env_file = Path('.env')
    env_example = Path('env_example.txt')
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ .env file created successfully!")
            print("💡 Please update the database credentials in .env file")
        except Exception as e:
            print(f"⚠️ Could not create .env file: {e}")

def main():
    """Main launcher function"""
    print("🚀 Drug Matching System Launcher")
    print("=" * 40)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies found!")
    
    # Check configuration
    print("🔍 Checking configuration...")
    if not check_config():
        sys.exit(1)
    print("✅ Configuration files found!")
    
    # Setup environment
    setup_environment()
    
    # Launch application
    print("\n🚀 Starting Drug Matching System...")
    print("💡 The application will open in your default browser")
    print("💡 Press Ctrl+C to stop the application")
    print("-" * 40)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
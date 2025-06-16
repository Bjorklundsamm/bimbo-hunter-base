#!/usr/bin/env python3
"""
Paimon Discord Bot Launcher
Run this from the main project directory to start Paimon
"""

import os
import sys
import subprocess

def main():
    """Launch Paimon from the main project directory"""
    print("🌟 Launching Paimon Discord Bot...")
    
    # Change to the paimon directory
    paimon_dir = os.path.join(os.path.dirname(__file__), 'p(ai)mon')
    
    if not os.path.exists(paimon_dir):
        print("❌ Paimon directory not found!")
        print("   Make sure you're running this from the main project directory")
        sys.exit(1)
    
    # Check if .env file exists
    env_file = os.path.join(paimon_dir, '.env')
    if not os.path.exists(env_file):
        print("❌ Paimon .env file not found!")
        print("📝 Please configure Paimon first:")
        print(f"   cd {paimon_dir}")
        print("   cp .env.example .env")
        print("   # Edit .env with your Discord bot token and channel ID")
        sys.exit(1)
    
    # Run the Paimon startup script
    startup_script = os.path.join(paimon_dir, 'start_paimon.py')
    
    try:
        os.chdir(paimon_dir)
        subprocess.run([sys.executable, 'start_paimon.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Paimon failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Paimon stopped by user")

if __name__ == "__main__":
    main()

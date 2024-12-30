import subprocess
from typing import List, Dict, Any
import os

def run_scanner_script(script_path: str) -> bool:
    """Run a scanner script and return success status"""
    try:
        subprocess.run(['python', script_path], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def ensure_output_dir():
    """Ensure the output directory exists"""
    os.makedirs('scanner/output', exist_ok=True)
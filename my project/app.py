# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from scanner.scan_manager import ScanManager
import threading
import os

app = Flask(__name__)
scan_manager = ScanManager()
scan_in_progress = False

def run_scan():
    global scan_in_progress
    scan_manager.run_scans()
    scan_in_progress = False

def parse_software_vulns(file_path):
    vulnerabilities = []
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file.readlines():
                # Split by commas and clean up each part
                parts = [part.strip() for part in line.split(',')]
                if len(parts) == 3:
                    # Extract values after the labels
                    software = parts[0].replace('Software:', '').strip()
                    version = parts[1].replace('Version:', '').strip()
                    vuln_id = parts[2].replace('Vulnerability ID:', '').strip()
                    
                    vulnerabilities.append({
                        'name': software,
                        'version': version,
                        'cve': vuln_id
                    })
    
    # Remove duplicates while preserving order
    seen = set()
    unique_vulns = []
    for vuln in vulnerabilities:
        key = (vuln['name'], vuln['version'])
        if key not in seen:
            seen.add(key)
            unique_vulns.append(vuln)
            
    return unique_vulns

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    global scan_in_progress
    admin_granted = request.form.get("admin_privilege")
    if admin_granted == "yes":
        if not scan_in_progress:
            scan_in_progress = True
            # Run scan in background
            thread = threading.Thread(target=run_scan)
            thread.start()
        return redirect(url_for("scanning"))
    return "Admin privileges are required to proceed.", 403

@app.route("/scanning")
def scanning():
    return render_template("scanning.html")

@app.route("/scan-status")
def scan_status():
    return jsonify({"completed": not scan_in_progress})

@app.route("/report")
def report():
    if scan_in_progress:
        return redirect(url_for("scanning"))
    
    # Add debug prints
    print("Reading software vulnerabilities...")
    software_vulnerabilities = parse_software_vulns('software_vuln.txt')
    print(f"Found {len(software_vulnerabilities)} software vulnerabilities")
    
    print("Reading Windows vulnerabilities...")
    results = scan_manager.get_results()
    windows_vulns = results['windows']
    print(f"Found {len(windows_vulns)} Windows vulnerabilities")
    print("Windows vulnerabilities:", windows_vulns)
    
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template("report.html",
                         software_vulnerabilities=software_vulnerabilities,
                         windows_vulnerabilities=windows_vulns,
                         scan_time=scan_time)

if __name__ == "__main__":
    app.run(debug=True)

# scanner/scan_manager.py
from typing import Dict, List
import os
from .config import SOFTWARE_SCAN_FILE, WINDOWS_SCAN_FILE
from .software_scanner import parse_software_vulnerabilities
from .windows_scanner import parse_windows_vulnerabilities
from .utils import run_scanner_script, ensure_output_dir

class ScanManager:
    def __init__(self):
        ensure_output_dir()
        
    def run_scans(self) -> bool:
        """Run both scanner scripts"""
        scripts = [
            'softwarepatch.py',
            'windowspatch.py'
        ]
        
        return all(run_scanner_script(script) for script in scripts)
    
    def get_results(self) -> Dict[str, List[Dict]]:
        """Get combined scan results"""
        return {
            'software': parse_software_vulnerabilities(SOFTWARE_SCAN_FILE),
            'windows': parse_windows_vulnerabilities(WINDOWS_SCAN_FILE)
        }

# scanner/software_scanner.py
def parse_software_vulnerabilities(file_path):
    vulnerabilities = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) == 3:
                        software = parts[0].replace('Software:', '').strip()
                        version = parts[1].replace('Version:', '').strip()
                        vuln_id = parts[2].replace('Vulnerability ID:', '').strip()
                        
                        vulnerabilities.append({
                            "name": software,
                            "version": version,
                            "cve": vuln_id
                        })
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
    return vulnerabilities

# scanner/windows_scanner.py
def parse_windows_vulnerabilities(file_path):
    vulnerabilities = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    vulnerabilities.append({
                        "name": parts[0],
                        "kb": parts[1]
                    })
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
    return vulnerabilities

# scanner/utils.py
import subprocess
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

# scanner/config.py
SOFTWARE_SCAN_FILE = "software_vuln.txt"  # Updated to match actual filename
WINDOWS_SCAN_FILE = "windowsvulnresults.txt"

# Scanning settings
SCAN_TIMEOUT = 30  # seconds
DEFAULT_CVE = "CVE-2023-XXXX"
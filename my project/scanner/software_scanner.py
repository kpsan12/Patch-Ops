def parse_software_vulnerabilities(file_path):
    vulnerabilities = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('Software:'):
                    # Parse "Software: name version" format
                    parts = line.replace('Software:', '').strip().rsplit(' ', 1)
                    if len(parts) == 2:
                        vulnerabilities.append({
                            "name": parts[0].strip(),
                            "version": parts[1],
                            "cve": "CVE-2023-XXXX"  # Placeholder CVE
                        })
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
    return vulnerabilities
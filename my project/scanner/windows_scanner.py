def parse_windows_vulnerabilities(file_path):
    """Parse Windows vulnerability data from the scan output file.
    Returns a list of dictionaries containing KB information."""
    vulnerabilities = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                # Look for lines containing KB numbers and vulnerability counts
                if '- KB' in line and ':' in line:
                    # Extract KB number
                    kb_part = line.split(':')[0].strip()
                    kb_number = kb_part.replace('- ', '')
                    if kb_number.startswith('KB') and 'KBUpdate Information' not in kb_number:
                        vulnerabilities.append({
                            "kb": kb_number
                        })
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
        return []
    except Exception as e:
        print(f"Error parsing Windows vulnerabilities: {e}")
        return []
    
    # Debug print
    print(f"Found {len(vulnerabilities)} Windows vulnerabilities")
    print("Vulnerabilities:", vulnerabilities)
    
    return vulnerabilities